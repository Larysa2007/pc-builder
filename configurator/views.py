from django.shortcuts import render, redirect
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard, Build

def home(request):
    results = []
    error = None
    pc_type = request.POST.get("pc_type")
    budget_str = request.POST.get("budget")
    selected_gpu_id = request.POST.get("gpu_id")

    gpus = Gpu.objects.all()

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

            def pick_build(multiplier):
                cpu = Cpu.objects.filter(price__lte=budget * (ratio['cpu'] * multiplier)).order_by('-price').first()
                if not cpu:
                    return None

                motherboard = Motherboard.objects.filter(socket=cpu.socket).order_by('-price').first()
                ram = Ram.objects.filter(price__lte=budget * (ratio['ram'] * multiplier)).order_by('-price').first()

                if selected_gpu_id:
                    gpu = Gpu.objects.get(id=selected_gpu_id)
                else:
                    gpu = Gpu.objects.filter(price__lte=budget * (ratio['gpu'] * multiplier)).order_by('-price').first()

                storage = Storage.objects.filter(price__lte=budget * (ratio['ssd'] * multiplier)).order_by('-price').first()
                psu = Psu.objects.filter(price__lte=budget * (ratio['psu'] * multiplier)).order_by('-price').first()

                items = [cpu, gpu, ram, storage, psu, motherboard]
                total = sum(item.price for item in items if item)

                if total > budget:
                    return None

                explanation = [
                    f"Процесор {cpu.name} обрано через оптимальне співвідношення ціни та продуктивності.",
                    f"Відеокарта {gpu.name if gpu else 'вбудована'} відповідає типу ПК ({ratio['name']}).",
                    f"Материнська плата сумісна із сокетом {cpu.socket}.",
                    f"Оперативна пам’ять забезпечує стабільну роботу системи.",
                    f"Загальна вартість {total} грн не перевищує бюджет {budget} грн."
                ]

                return {
                    "cpu": cpu,
                    "gpu": gpu,
                    "ram": ram,
                    "storage": storage,
                    "psu": psu,
                    "motherboard": motherboard,
                    "total": total,
                    "explanation": explanation
                }

            # 3 варіанти
            for m in [1.0, 0.85, 0.7]:
                build = pick_build(m)
                if build:
                    results.append(build)

            if not results:
                error = f"На жаль, у базі немає деталей для бюджету {budget} грн."

        except ValueError:
            error = "Введіть числове значення бюджету."

    return render(request, "home.html", {
        "results": results,
        "error": error,
        "selected_type": pc_type,
        "selected_budget": budget_str,
        "gpus": gpus
    })


def save_build(request):
    if request.method == "POST":
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
    builds = Build.objects.all().order_by('-id')
    return render(request, 'builds.html', {'builds': builds})