from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    
    # Дані для всіх випадаючих списків
    context = {
        "all_cpus": Cpu.objects.all().order_by('price'),
        "all_gpus": Gpu.objects.all().order_by('price'),
        "all_mbs": Motherboard.objects.all().order_by('price'),
        "all_rams": Ram.objects.all().order_by('price'),
        "all_storages": Storage.objects.all().order_by('price'),
        "all_psus": Psu.objects.all().order_by('price'),
    }

    if request.method == "POST":
        try:
            budget = int(request.POST.get("budget", 0))
            pc_type = request.POST.get("pc_type", "gaming")

            # Список стратегій (дві збірки)
            strategies = [
                {"name": "🚀 Максимальна потужність", "factor": 1.0},
                {"name": "⚖️ Оптимальний баланс", "factor": 0.85}
            ]

            for st in strategies:
                money_left = budget * st["factor"]
                explanations = []

                # ФУНКЦІЯ ДЛЯ ВИБОРУ (Своє або Авто)
                def get_part(model_class, form_name, price_limit_factor, filter_kwargs={}):
                    user_choice_id = request.POST.get(form_name)
                    # Якщо це перша збірка і користувач щось обрав — беремо його вибір
                    if user_choice_id and st["factor"] == 1.0:
                        part = model_class.objects.get(id=user_choice_id)
                        explanations.append(f"✅ Ви обрали: {part.name}")
                        return part
                    # Інакше — автопідбір
                    part = model_class.objects.filter(**filter_kwargs, price__lte=money_left * price_limit_factor).order_by('-price').first()
                    if not part: part = model_class.objects.filter(**filter_kwargs).order_by('price').first()
                    if not part: part = model_class.objects.order_by('price').first()
                    return part

                # 1. Процесор
                cpu = get_part(Cpu, "cpu_id", 0.35)
                money_left -= cpu.price

                # 2. Материнка (з фільтром по сокету!)
                mb = get_part(Motherboard, "mb_id", 0.2, {"socket": cpu.socket})
                money_left -= mb.price

                # 3. Відеокарта
                gpu = None
                user_gpu_id = request.POST.get("gpu_id")
                if user_gpu_id and st["factor"] == 1.0:
                    gpu = Gpu.objects.get(id=user_gpu_id)
                elif pc_type != "office":
                    gpu = Gpu.objects.filter(price__lte=money_left * 0.6).order_by('-price').first()
                
                if gpu: money_left -= gpu.price

                # 4. ОЗП, Диск, БЖ
                ram = get_part(Ram, "ram_id", 0.3)
                money_left -= ram.price
                
                storage = get_part(Storage, "storage_id", 0.3)
                money_left -= storage.price
                
                psu = get_part(Psu, "psu_id", 1.0) # БЖ на залишок

                results.append({
                    "variant_name": st["name"],
                    "cpu": cpu, "gpu": gpu, "motherboard": mb,
                    "ram": ram, "storage": storage, "psu": psu,
                    "total": cpu.price + mb.price + (gpu.price if gpu else 0) + ram.price + storage.price + psu.price,
                    "explanations": explanations
                })

        except Exception as e:
            error = f"Помилка: {e}. Перевірте наявність деталей у базі."

    context.update({"results": results, "error": error})
    return render(request, "home.html", context)