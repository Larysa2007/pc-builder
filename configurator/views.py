from django.shortcuts import render, redirect
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard, Build

def home(request):
    result = None
    error = None
    pc_type = request.POST.get("pc_type")
    budget_str = request.POST.get("budget")

    if request.method == "POST" and budget_str:
        try:
            budget = int(budget_str)

            if budget < 5000:
                error = f"Бюджет {budget} грн занадто малий."
            else:
                ratios = {
                    "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'score': 95, 'name': "Ігровий ПК"},
                    "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'score': 50, 'name': "Офісний ПК"},
                    "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'score': 85, 'name': "Робоча станція"},
                    "stream": {'cpu': 0.30, 'gpu': 0.30, 'ram': 0.15, 'ssd': 0.10, 'psu': 0.07, 'mb': 0.08, 'score': 92, 'name': "ПК для стрімінгу"}
                }
                ratio = ratios.get(pc_type, ratios["gaming"])

                # 1. Попередній підбір основних деталей (CPU та MB)
                cpu = Cpu.objects.filter(price__lte=budget * ratio['cpu']).order_by('-price').first()
                if not cpu: cpu = Cpu.objects.all().order_by('price').first()

                if cpu:
                    mb = Motherboard.objects.filter(socket=cpu.socket, price__lte=budget * ratio['mb']).order_by('-price').first()
                    if not mb: mb = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()

                    # 2. Підбираємо інші деталі
                    gpu = Gpu.objects.filter(price__lte=budget * ratio['gpu']).order_by('-price').first()
                    ram = Ram.objects.filter(ram_type=mb.ram_type, price__lte=budget * ratio['ram']).order_by('-price').first()
                    storage = Storage.objects.filter(price__lte=budget * ratio['ssd']).order_by('-price').first()
                    psu = Psu.objects.filter(price__lte=budget * ratio['psu']).order_by('-price').first()

                    # --- ЛОГІКА ВИКОРИСТАННЯ ЗАЛИШКУ (Upgrade) ---
                    # Рахуємо, скільки грошей залишилося
                    current_items = [cpu, gpu, ram, storage, psu, mb]
                    current_total = sum(item.price for item in current_items if item)
                    remaining_money = budget - current_total

                    # Якщо залишилося більше 1000 грн, покращуємо найважливіше (GPU або CPU)
                    if remaining_money > 1000 and gpu:
                        better_gpu = Gpu.objects.filter(price__lte=gpu.price + remaining_money).order_by('-price').first()
                        if better_gpu:
                            gpu = better_gpu
                            current_total = sum(item.price for item in [cpu, gpu, ram, storage, psu, mb] if item)

                    if current_total <= budget:
                        result = {
                            "cpu": cpu, "gpu": gpu, "ram": ram, "storage": storage,
                            "psu": psu, "motherboard": mb, "total": current_total,
                            "power": ratio['score'], "type_name": ratio['name']
                        }
                    else:
                        error = "Не вдалося вкластися в бюджет. Спробуйте інший тип ПК."
                else:
                    error = "У базі немає відповідних процесорів."

        except ValueError:
            error = "Введіть числове значення бюджету."

    return render(request, "home.html", {"result": result, "error": error, "selected_type": pc_type, "selected_budget": budget_str})


def view_builds(request):
    builds = Build.objects.all().order_by('-id')
    return render(request, 'builds.html', {'builds': builds})