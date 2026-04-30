from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    
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

            if budget < 10000:
                error = "⚠️ Мінімальний бюджет для коректного підбору — 10,000 грн."
                return render(request, "home.html", {**context, "error": error})

            strategies = [
                {"name": "🚀 Максимальна потужність", "factor": 1.0},
                {"name": "⚖️ Оптимальний баланс", "factor": 0.85}
            ]

            for st in strategies:
                money_left = budget * st["factor"]
                explanations = []

                # --- 1. ПРОЦЕСОР ---
                u_cpu = request.POST.get("cpu_id")
                if u_cpu and st["factor"] == 1.0:
                    cpu = Cpu.objects.get(id=u_cpu)
                    explanations.append(f"✅ **Процесор**: Ви обрали <b>{cpu.name}</b>. Це серце вашої системи.")
                else:
                    cpu = Cpu.objects.filter(price__lte=money_left * 0.35).order_by('-price').first()
                    if not cpu: cpu = Cpu.objects.order_by('price').first()
                    explanations.append(f"🤖 **Процесор**: <b>{cpu.name}</b> — найкращий вибір за потужністю у межах ліміту.")
                money_left -= cpu.price

                # --- 2. МАТЕРИНКА ---
                u_mb = request.POST.get("mb_id")
                if u_mb and st["factor"] == 1.0:
                    mb = Motherboard.objects.get(id=u_mb)
                    explanations.append(f"✅ **Материнка**: Вибрано вашу модель <b>{mb.name}</b>.")
                else:
                    mb = Motherboard.objects.filter(socket=cpu.socket, price__lte=money_left * 0.25).order_by('-price').first()
                    if not mb: mb = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()
                    explanations.append(f"🤖 **Материнка**: <b>{mb.name}</b> підібрана автоматично під сокет {cpu.socket}.")
                money_left -= mb.price

                # --- 3. ВІДЕОКАРТА ---
                u_gpu = request.POST.get("gpu_id")
                gpu = None
                if u_gpu and st["factor"] == 1.0:
                    gpu = Gpu.objects.get(id=u_gpu)
                    explanations.append(f"✅ **Відеокарта**: Встановлено обрану вами <b>{gpu.name}</b>.")
                elif pc_type in ["gaming", "streaming", "video_editing"]:
                    gpu = Gpu.objects.filter(price__lte=money_left * 0.7).order_by('-price').first()
                    if gpu:
                        explanations.append(f"🤖 **Відеокарта**: <b>{gpu.name}</b> обрана для високого FPS.")
                    else:
                        explanations.append("ℹ️ **Відеокарта**: Бюджет обмежений, використовуємо графіку процесора.")
                
                if gpu: money_left -= gpu.price

                # --- 4. ОЗП ---
                u_ram = request.POST.get("ram_id")
                if u_ram and st["factor"] == 1.0:
                    ram = Ram.objects.get(id=u_ram)
                    explanations.append(f"✅ **ОЗП**: Ви обрали <b>{ram.name}</b>.")
                else:
                    ram = Ram.objects.filter(price__lte=money_left * 0.4).order_by('-price').first()
                    if not ram: ram = Ram.objects.order_by('price').first()
                    explanations.append(f"🤖 **ОЗП**: <b>{ram.name}</b> забезпечить стабільну роботу.")
                money_left -= ram.price

                # --- 5. ДИСК ТА БЖ ---
                storage = Storage.objects.filter(price__lte=money_left * 0.5).order_by('-price').first() or Storage.objects.first()
                money_left -= storage.price
                psu = Psu.objects.filter(price__lte=money_left).order_by('-price').first() or Psu.objects.first()
                
                explanations.append(f"🤖 **Блок живлення**: <b>{psu.name}</b> підібраний з урахуванням споживання деталей.")

                total_sum = cpu.price + mb.price + (gpu.price if gpu else 0) + ram.price + storage.price + psu.price
                
                results.append({
                    "variant_name": st["name"],
                    "cpu": cpu, "gpu": gpu, "motherboard": mb,
                    "ram": ram, "storage": storage, "psu": psu,
                    "total": total_sum,
                    "explanations": explanations
                })

        except Exception as e:
            error = f"Сталася помилка при розрахунку: {e}"

    context.update({"results": results, "error": error})
    return render(request, "home.html", context)