from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    result = None
    error = None
    pc_type = request.POST.get("pc_type")
    budget_str = request.POST.get("budget")

    if request.method == "POST" and budget_str:
        try:
            budget = int(budget_str)
            if budget < 5000:
                error = "❌ Бюджет занадто малий! Мінімум 5000 грн."
            else:
                # 1. Розподіл часток бюджету
                ratios = {
                    "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'score': 95},
                    "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'score': 50},
                    "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'score': 85},
                    "stream": {'cpu': 0.30, 'gpu': 0.30, 'ram': 0.15, 'ssd': 0.10, 'psu': 0.07, 'mb': 0.08, 'score': 90}
                }
                ratio = ratios.get(pc_type, ratios["gaming"])

                # Крок А: Процесор (базис для всього)
                cpu = Cpu.objects.filter(price__lte=budget * ratio['cpu']).order_by('-price').first()
                
                if not cpu:
                    error = "В базі немає підходящих процесорів під цей бюджет."
                else:
                    # Крок Б: Материнка - ЖОРСТКИЙ фільтр за сокетом
                    motherboard = Motherboard.objects.filter(
                        socket=cpu.socket, 
                        price__lte=budget * (ratio['mb'] + 0.05) # Трохи розширимо ліміт для материнки
                    ).order_by('-price').first()

                    # Якщо бюджетна плата не знайшлась, беремо найдешевшу, але того ж сокета!
                    if not motherboard:
                        motherboard = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()

                    # Крок В: Оперативка - ЖОРСТКИЙ фільтр за типом пам'яті плати
                    ram_type_needed = motherboard.ram_type if motherboard else "DDR4"
                    ram = Ram.objects.filter(
                        ram_type=ram_type_needed,
                        price__lte=budget * ratio['ram']
                    ).order_by('-price').first()

                    # Крок Г: Решта
                    gpu = Gpu.objects.filter(price__lte=budget * ratio['gpu']).order_by('-price').first()
                    storage = Storage.objects.filter(price__lte=budget * ratio['ssd']).order_by('-price').first()
                    psu = Psu.objects.filter(price__lte=budget * ratio['psu']).order_by('-price').first()

                    total = sum(item.price for item in [cpu, gpu, ram, storage, psu, motherboard] if item)

                    result = {
                        "cpu": cpu, "gpu": gpu, "ram": ram, "storage": storage,
                        "psu": psu, "motherboard": motherboard, "total": total,
                        "power": ratio['score']
                    }
        except ValueError:
            error = "Будь ласка, введіть коректне число для бюджету."

    return render(request, "home.html", {
        "result": result, "error": error, 
        "selected_type": pc_type, "selected_budget": budget_str
    })