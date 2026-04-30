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
            budget = int(budget_str) if budget_str and budget_str.isdigit() else 0
            if budget < 10000:
                raise ValueError("Мінімальний бюджет для підбору — 10,000 грн.")

            configs = {
                "gaming": {"cpu_w": 0.25, "gpu_w": 0.40, "ram_w": 0.10, "label": "ігор"},
                "streaming": {"cpu_w": 0.35, "gpu_w": 0.25, "ram_w": 0.15, "label": "стрімінгу"},
                "office": {"cpu_w": 0.45, "gpu_w": 0.00, "ram_w": 0.15, "label": "офісної роботи"},
                "work": {"cpu_w": 0.35, "gpu_w": 0.15, "ram_w": 0.25, "label": "професійної роботи"}
            }

            cfg = configs.get(pc_type, configs["gaming"])
            variants = [{"name": "Максимальна потужність", "m": 1.0}, {"name": "Оптимальний баланс", "m": 0.80}]

            for var in variants:
                b = budget * var["m"]
                explanations = [] # Список для пояснень
                
                # 1. Процесор + Пояснення
                cpu = Cpu.objects.filter(price__lte=b * cfg['cpu_w']).order_by('-price').first()
                if cpu:
                    explanations.append(f"🧠 {cpu.name}: Обрано як основний обчислювальний центр для {cfg['label']}.")
                
                # 2. Відеокарта + Пояснення
                gpu = Gpu.objects.filter(price__lte=b * cfg['gpu_w']).order_by('-price').first()
                if gpu:
                    explanations.append(f"🎮 {gpu.name}: Забезпечує графічну потужність для плавного зображення.")
                elif pc_type in ["gaming", "streaming"]:
                    explanations.append("⚠️ Бюджету недостатньо для дискретної відеокарти, рекомендується збільшити суму.")
                else:
                    explanations.append("🏢 Використовується вбудоване відеоядро, що ідеально для офісних завдань.")

                # 3. Материнка (сумісність)
                mb = Motherboard.objects.filter(socket=cpu.socket if cpu else None).order_by('price').first()
                if mb:
                    explanations.append(f"🔌 {mb.name}: Надійна база, що повністю сумісна з вашим процесором.")

                # 4. ОЗП
                ram = Ram.objects.filter(price__lte=b * 0.15).order_by('-price').first()
                if ram:
                    explanations.append(f"⚡ {ram.name}: Достатньо пам'яті для багатозадачності.")

                # Інші деталі
                ssd = Storage.objects.order_by('price').first()
                psu = Psu.objects.order_by('price').first()

                total_p = sum([item.price for item in [cpu, gpu, mb, ram, ssd, psu] if hasattr(item, 'price')])

                results.append({
                    "variant_name": var["name"],
                    "cpu": cpu, "gpu": gpu or "Вбудована", "mb": mb,
                    "ram": ram, "ssd": ssd, "psu": psu,
                    "total": total_p,
                    "explanations": explanations # Передаємо пояснення в шаблон
                })

        except Exception as e:
            error = str(e)

    return render(request, "home.html", {
        "results": results, "error": error, 
        "selected_budget": budget_str, "selected_type": pc_type
    })