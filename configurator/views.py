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
                error = "❌ Мінімальний бюджет 5000 грн"
            else:
                ratios = {
                    "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08},
                    "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15},
                    "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10},
                }

                ratio = ratios.get(pc_type, ratios["gaming"])

                # CPU
                cpu = Cpu.objects.filter(price__lte=budget * ratio['cpu']).order_by('-price').first()

                if not cpu:
                    error = "Немає CPU під бюджет"
                else:
                    # Motherboard
                    motherboard = Motherboard.objects.filter(
                        socket=cpu.socket
                    ).order_by('-price').first()

                    # RAM
                    ram = Ram.objects.filter(
                        ram_type=motherboard.ram_type
                    ).order_by('-price').first()

                    # GPU (автопокращення)
                    gpu_budget = budget * ratio['gpu']
                    gpu = Gpu.objects.filter(price__lte=gpu_budget).order_by('-price').first()

                    # SSD
                    storage = Storage.objects.order_by('-price').first()

                    # PSU
                    psu = Psu.objects.order_by('-price').first()

                    total = sum([
                        cpu.price if cpu else 0,
                        gpu.price if gpu else 0,
                        ram.price if ram else 0,
                        storage.price if storage else 0,
                        psu.price if psu else 0,
                        motherboard.price if motherboard else 0
                    ])

                    # 🔥 АВТОПОКРАЩЕННЯ
                    leftover = budget - total
                    if leftover > 2000:
                        better_gpu = Gpu.objects.filter(price__lte=budget).order_by('-price').first()
                        if better_gpu:
                            gpu = better_gpu
                            total = total - (gpu.price if gpu else 0) + better_gpu.price

                    result = {
                        "cpu": cpu,
                        "gpu": gpu,
                        "ram": ram,
                        "storage": storage,
                        "psu": psu,
                        "motherboard": motherboard,
                        "total": total,
                    }

        except ValueError:
            error = "Введіть число!"

    return render(request, "home.html", {
        "result": result,
        "error": error,
        "selected_type": pc_type,
        "selected_budget": budget_str
    })


# 💾 ЗБЕРЕЖЕННЯ
def save_build(request):
    if request.method == "POST":
        build = Build.objects.create(
            cpu=Cpu.objects.first(),
            gpu=Gpu.objects.first(),
            ram=Ram.objects.first(),
            storage=Storage.objects.first(),
            psu=Psu.objects.first(),
            motherboard=Motherboard.objects.first(),
            total_price=10000
        )
    return redirect("home")


# 👤 СПИСОК ЗБІРОК
def builds(request):
    builds = Build.objects.all().order_by('-created_at')
    return render(request, "builds.html", {"builds": builds})