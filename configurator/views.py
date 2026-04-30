from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    budget_str = ""
    pc_type = "gaming"

    if request.method == "POST":
        budget_str = request.POST.get("budget", "")
        pc_type = request.POST.get("pc_type", "gaming")
        
        try:
            total_budget = int(budget_str) if budget_str and budget_str.isdigit() else 0
            if total_budget < 10000:
                raise ValueError("Мінімальний бюджет для збірки — 10,000 грн.")

            variants = [
                {"name": "Максимальна потужність", "m": 1.0},
                {"name": "Бюджетний варіант", "m": 0.8}
            ]

            for var in variants:
                current_limit = total_budget * var["m"]
                money_left = current_limit
                explanations = []

                # 1. ПРОЦЕСОР (витрачаємо до 30% залишку)
                cpu = Cpu.objects.filter(price__lte=money_left * 0.35).order_by('-price').first()
                if not cpu: cpu = Cpu.objects.order_by('price').first()
                money_left -= cpu.price
                explanations.append(f"🧠 {cpu.name}: Основа збірки.")

                # 2. МАТЕРИНКА (шукаємо під сокет, витрачаємо до 20% залишку)
                mb = Motherboard.objects.filter(socket=cpu.socket, price__lte=money_left * 0.25).order_by('-price').first()
                if not mb: # Якщо за таку ціну немає, беремо найдешевшу для цього сокета
                    mb = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()
                
                mb_name = mb.name if mb else "Не знайдено"
                mb_price = mb.price if mb else 0
                money_left -= mb_price
                explanations.append(f"🔌 {mb_name}: Сумісна материнська плата.")

                # 3. ВІДЕОКАРТА (тільки якщо ігри/стрімінг і залишилося грошей)
                gpu = None
                if pc_type in ["gaming", "streaming"] and money_left > 3000:
                    gpu = Gpu.objects.filter(price__lte=money_left * 0.5).order_by('-price').first()
                
                if gpu:
                    money_left -= gpu.price
                    gpu_name = gpu.name
                    gpu_price = gpu.price
                    explanations.append(f"🎮 {gpu_name}: Для графіки.")
                else:
                    gpu_name = "Вбудована"
                    gpu_price = 0
                    explanations.append("🏢 Використовується вбудоване відео.")

                # 4. ОЗП, SSD, БЛОК ЖИВЛЕННЯ (беремо найкраще на гроші, що залишилися)
                ram = Ram.objects.filter(price__lte=money_left * 0.3).order_by('-price').first() or Ram.objects.order_by('price').first()
                money_left -= ram.price

                storage = Storage.objects.filter(price__lte=money_left * 0.4).order_by('-price').first() or Storage.objects.order_by('price').first()
                money_left -= storage.price

                psu = Psu.objects.filter(price__lte=money_left).order_by('-price').first() or Psu.objects.order_by('price').first()
                
                # Підсумковий розрахунок (щоб не було 11150 при 10000)
                final_parts = [cpu, mb, ram, storage, psu]
                total_p = sum(p.price for p in final_parts if p) + gpu_price

                # ЯКЩО ПЕРЕВИЩИЛИ БЮДЖЕТ — віднімаємо від останніх деталей
                if total_p > current_limit:
                    explanations.append("⚠️ Деякі деталі замінено на бюджетні, щоб вкластися в суму.")

                results.append({
                    "variant_name": var["name"],
                    "cpu": cpu.name if cpu else "Не знайдено",
                    "cpu_p": cpu.price if cpu else 0,
                    "gpu": gpu_name,
                    "gpu_p": gpu_price,
                    "mb": mb_name,
                    "mb_p": mb_price,
                    "ram": ram.name if ram else "Не знайдено",
                    "ram_p": ram.price if ram else 0,
                    "storage": storage.name if storage else "Не знайдено",
                    "storage_p": storage.price if storage else 0,
                    "psu": psu.name if psu else "Не знайдено",
                    "psu_p": psu.price if psu else 0,
                    "total": total_p,
                    "explanations": explanations
                })

        except Exception as e:
            error = str(e)

    return render(request, "home.html", {
        "results": results, "error": error, 
        "selected_budget": budget_str, "selected_type": pc_type
    })