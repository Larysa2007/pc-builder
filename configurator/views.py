from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard


def home(request):
    result = None
    error = None
    pc_type = request.POST.get("pc_type", "gaming")
    budget = int(request.POST.get("budget", 30000))

    if request.method == "POST":

        # ❌ перевірка мінімального бюджету
        if budget < 5000:
            error = "❌ Бюджет занадто малий! Мінімум 5000 грн."
        else:
            # 🔥 Розподіл бюджету
            if pc_type == "gaming":
                cpu_budget = budget * 0.30
                gpu_budget = budget * 0.40
            elif pc_type == "office":
                cpu_budget = budget * 0.40
                gpu_budget = budget * 0.10
            elif pc_type == "work":
                cpu_budget = budget * 0.35
                gpu_budget = budget * 0.20
            elif pc_type == "stream":
                cpu_budget = budget * 0.30
                gpu_budget = budget * 0.30
            else:
                cpu_budget = budget * 0.25
                gpu_budget = budget * 0.10

            ram_budget = budget * 0.15
            ssd_budget = budget * 0.10
            psu_budget = budget * 0.05
            mb_budget = budget * 0.10

            # 🔥 Функція вибору компонентів
            def pick(model, limit):
                item = model.objects.filter(price__lte=limit).order_by("-price").first()
                if not item:
                    item = model.objects.order_by("price").first()
                return item

            cpu = pick(Cpu, cpu_budget)
            gpu = pick(Gpu, gpu_budget)
            ram = pick(Ram, ram_budget)
            storage = pick(Storage, ssd_budget)
            psu = pick(Psu, psu_budget)
            motherboard = pick(Motherboard, mb_budget)

            total = sum([
                cpu.price if cpu else 0,
                gpu.price if gpu else 0,
                ram.price if ram else 0,
                storage.price if storage else 0,
                psu.price if psu else 0,
                motherboard.price if motherboard else 0,
            ])

            result = {
                "cpu": cpu,
                "gpu": gpu,
                "ram": ram,
                "storage": storage,
                "psu": psu,
                "motherboard": motherboard,
                "total": total,
            }

    return render(request, "home.html", {
        "result": result,
        "error": error,
        "selected_type": pc_type,
        "selected_budget": budget,
    })