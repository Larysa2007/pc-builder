from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    budget_str = ""
    pc_type = "gaming"

    # Дані для випадаючих списків (Конструктора)
    context_data = {
        "all_cpus": Cpu.objects.all().order_by('price'),
        "all_gpus": Gpu.objects.all().order_by('price'),
        "all_mbs": Motherboard.objects.all().order_by('price'),
        "all_rams": Ram.objects.all().order_by('price'),
    }

    if request.method == "POST":
        budget_str = request.POST.get("budget", "")
        pc_type = request.POST.get("pc_type", "gaming")
        
        try:
            total_budget = int(budget_str) if budget_str and budget_str.isdigit() else 0
            if total_budget < 10000:
                raise ValueError("Мінімальний бюджет для збірки — 10,000 грн.")

            # Логіка підбору (Бюджетний та Потужний варіанти)
            ratios = [1.0] # Можна додати 0.8 для другого варіанту
            for m in ratios:
                current_limit = total_budget * m
                money_left = current_limit
                explanations = []

                # 1. Процесор (30% бюджету)
                cpu = Cpu.objects.filter(price__lte=money_left * 0.35).order_by('-price').first()
                if not cpu: cpu = Cpu.objects.order_by('price').first()
                money_left -= cpu.price
                explanations.append(f"Процесор {cpu.name} обрано як оптимальне серце системи за свою ціну.")

                # 2. Материнка (під сокет)
                mb = Motherboard.objects.filter(socket=cpu.socket, price__lte=money_left * 0.25).order_by('-price').first()
                if not mb: mb = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()
                money_left -= mb.price
                explanations.append(f"Материнська плата на сокеті {cpu.socket} забезпечує стабільну роботу та сумісність.")

                # 3. Відеокарта (тільки для ігор/стрімінгу)
                gpu = None
                if pc_type in ["gaming", "streaming"] and money_left > 3000:
                    gpu = Gpu.objects.filter(price__lte=money_left * 0.6).order_by('-price').first()
                
                gpu_price = 0
                if gpu:
                    money_left -= gpu.price
                    gpu_price = gpu.price
                    explanations.append(f"Відеокарта {gpu.name} дозволить запускати сучасні додатки на високих налаштуваннях.")
                else:
                    explanations.append("Використовується інтегроване графічне ядро для економії бюджету.")

                # 4. ОЗП
                ram = Ram.objects.filter(price__lte=money_left * 0.4).order_by('-price').first() or Ram.objects.order_by('price').first()
                money_left -= ram.price

                # 5. Накопичувач
                storage = Storage.objects.filter(price__lte=money_left * 0.5).order_by('-price').first() or Storage.objects.order_by('price').first()
                money_left -= storage.price

                # 6. Блок живлення
                psu = Psu.objects.filter(price__lte=money_left).order_by('-price').first() or Psu.objects.order_by('price').first()
                
                total_p = cpu.price + mb.price + gpu_price + ram.price + storage.price + psu.price

                results.append({
                    "cpu": cpu, "gpu": gpu, "motherboard": mb, 
                    "ram": ram, "storage": storage, "psu": psu,
                    "total": total_p, "explanations": explanations
                })

        except Exception as e:
            error = str(e)

    context_data.update({"results": results, "error": error, "selected_budget": budget_str, "selected_type": pc_type})
    return render(request, "home.html", context_data)