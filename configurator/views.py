from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    
    # Завантажуємо всі деталі для випадаючих списків
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
            budget_val = request.POST.get("budget", "0")
            budget = int(budget_val) if budget_val.isdigit() else 0
            pc_type = request.POST.get("pc_type", "gaming")

            # Перевірка на мінімальний бюджет
            if budget < 10000:
                error = "⚠️ Мінімальний бюджет для збірки — 10,000 грн."
                return render(request, "home.html", {**context, "error": error})

            # Дві стратегії: Максимальна та Оптимальна
            strategies = [
                {"name": "🚀 Максимальна потужність", "factor": 1.0},
                {"name": "⚖️ Оптимальний баланс", "factor": 0.85}
            ]

            for st in strategies:
                money_left = budget * st["factor"]
                explanations = [f"Збірка орієнтована на {st['name']}."]

                # ФУНКЦІЯ ПІДБОРУ: Пріоритет ручному вибору (тільки для першої збірки)
                def select_part(model_class, form_name, limit_percent, filter_kwargs={}):
                    user_id = request.POST.get(form_name)
                    # Якщо користувач обрав сам і це перша збірка (factor 1.0)
                    if user_id and st["factor"] == 1.0:
                        part = model_class.objects.get(id=user_id)
                        explanations.append(f"✅ Враховано ваш вибір: {part.name}")
                        return part
                    # Автопідбір
                    part = model_class.objects.filter(**filter_kwargs, price__lte=money_left * limit_percent).order_by('-price').first()
                    if not part: part = model_class.objects.filter(**filter_kwargs).order_by('price').first()
                    if not part: part = model_class.objects.order_by('price').first()
                    return part

                # 1. Процесор
                cpu = select_part(Cpu, "cpu_id", 0.35)
                money_left -= cpu.price

                # 2. Материнка (Сумісність по сокету)
                mb = select_part(Motherboard, "mb_id", 0.2, {"socket": cpu.socket})
                money_left -= mb.price

                # 3. Відеокарта (Тільки якщо не офісний ПК)
                gpu = None
                user_gpu_id = request.POST.get("gpu_id")
                if user_gpu_id and st["factor"] == 1.0:
                    gpu = Gpu.objects.get(id=user_gpu_id)
                elif pc_type in ["gaming", "streaming", "video_editing"]:
                    gpu = Gpu.objects.filter(price__lte=money_left * 0.6).order_by('-price').first()
                
                if gpu: money_left -= gpu.price

                # 4. Решта компонентів
                ram = select_part(Ram, "ram_id", 0.4)
                money_left -= ram.price
                storage = select_part(Storage, "storage_id", 0.5)
                money_left -= storage.price
                psu = select_part(Psu, "psu_id", 1.0)

                total_sum = cpu.price + mb.price + (gpu.price if gpu else 0) + ram.price + storage.price + psu.price
                
                results.append({
                    "variant_name": st["name"],
                    "cpu": cpu, "gpu": gpu, "motherboard": mb,
                    "ram": ram, "storage": storage, "psu": psu,
                    "total": total_sum,
                    "explanations": explanations
                })

        except Exception as e:
            error = f"Сталася помилка: {e}"

    context.update({"results": results, "error": error})
    return render(request, "home.html", context)