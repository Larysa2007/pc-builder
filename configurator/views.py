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
            ratios = {
                "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'score': 95, 'name': "Ігровий ПК"},
                "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'score': 50, 'name': "Офісний ПК"},
                "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'score': 85, 'name': "Робоча станція"},
                "stream": {'cpu': 0.30, 'gpu': 0.30, 'ram': 0.15, 'ssd': 0.10, 'psu': 0.07, 'mb': 0.08, 'score': 90, 'name': "ПК для стрімінгу"}
            }
            ratio = ratios.get(pc_type, ratios["gaming"])

            # Функція "м'якого" пошуку: шукає в межах ціни, а якщо немає - бере найдешевше
            def find_part(model, max_price, extra_filters={}):
                part = model.objects.filter(**extra_filters, price__lte=max_price).order_by('-price').first()
                if not part:
                    part = model.objects.filter(**extra_filters).order_by('price').first()
                return part

            # 1. Спершу знаходимо процесор
            cpu = find_part(Cpu, budget * ratio['cpu'])
            
            if cpu:
                # 2. Знаходимо материнку ПІД ЦЕЙ процесор (найважливіша сумісність)
                mb = find_part(Motherboard, budget * ratio['mb'], {'socket': cpu.socket})
                
                if mb:
                    # 3. Решта деталей з урахуванням сумісності RAM
                    gpu = find_part(Gpu, budget * ratio['gpu'])
                    ram = find_part(Ram, budget * ratio['ram'], {'ram_type': mb.ram_type})
                    storage = find_part(Storage, budget * ratio['ssd'])
                    psu = find_part(Psu, budget * ratio['psu'])

                    items = [cpu, mb, gpu, ram, storage, psu]
                    total = sum(item.price for item in items if item)

                    # Перевірка: якщо після підбору "найдешевшого" ми все одно вилізли за бюджет
                    if total > budget:
                        error = f"На жаль, навіть мінімальна збірка коштує {total} грн. Бюджету {budget} недостатньо."
                    else:
                        result = {
                            "cpu": cpu, "gpu": gpu, "ram": ram, "storage": storage,
                            "psu": psu, "motherboard": mb, "total": total,
                            "power": ratio['score'], "type_name": ratio['name']
                        }
                else:
                    error = "У базі немає материнської плати для цього процесора."
            else:
                error = "У базі немає жодного процесора."

        except ValueError:
            error = "Введіть числове значення бюджету."

    return render(request, "home.html", {"result": result, "error": error, "selected_type": pc_type, "selected_budget": budget_str})

# Додай це в кінець файлу views.py
def save_build(request):
    if request.method == "POST":
        from .models import Build # переконайся, що імпорт правильний
        Build.objects.create(
            cpu=request.POST.get("cpu_name"),
            gpu=request.POST.get("gpu_name"),
            motherboard=request.POST.get("mb_name"),
            ram=request.POST.get("ram_name"),
            storage=request.POST.get("storage_name"),
            psu=request.POST.get("psu_name"),
            total_price=request.POST.get("total_price")
        )
        return redirect('view_builds')
    return redirect('home')

def view_builds(request):
    from .models import Build
    builds = Build.objects.all().order_by('-id')
    return render(request, 'builds.html', {'builds': builds})
