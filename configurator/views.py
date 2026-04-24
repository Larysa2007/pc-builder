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
            # Коефіцієнти розподілу бюджету та метадані для аналізу
            ratios = {
                "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'score': 95, 'name': "Ігровий ПК"},
                "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'score': 50, 'name': "Офісний ПК"},
                "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'score': 85, 'name': "Робоча станція"},
                "stream": {'cpu': 0.30, 'gpu': 0.30, 'ram': 0.15, 'ssd': 0.10, 'psu': 0.07, 'mb': 0.08, 'score': 90, 'name': "ПК для стрімінгу"}
            }
            ratio = ratios.get(pc_type, ratios["gaming"])

            # Підбір процесора (з невеликим запасом по ціні +10%)
            cpu = Cpu.objects.filter(price__lte=budget * (ratio['cpu'] + 0.10)).order_by('-price').first()
            
            if cpu:
                # Підбір материнської плати за сокетом процесора
                motherboard = Motherboard.objects.filter(socket=cpu.socket, price__lte=budget * (ratio['mb'] + 0.10)).order_by('-price').first()
                if not motherboard:
                    motherboard = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()

                # Підбір оперативної пам'яті (відповідно до типу плати)
                ram = Ram.objects.filter(ram_type=motherboard.ram_type if motherboard else "DDR4", price__lte=budget * (ratio['ram'] + 0.05)).order_by('-price').first()
                
                # Відеокарта, Накопичувач та Блок живлення
                gpu = Gpu.objects.filter(price__lte=budget * (ratio['gpu'] + 0.10)).order_by('-price').first()
                storage = Storage.objects.filter(price__lte=budget * (ratio['ssd'] + 0.05)).order_by('-price').first()
                psu = Psu.objects.filter(price__lte=budget * (ratio['psu'] + 0.05)).order_by('-price').first()

                # Рахуємо загальну вартість
                items = [cpu, gpu, ram, storage, psu, motherboard]
                total = sum(item.price for item in items if item)
                
                # Формуємо словник result (всі назви тепер збігаються з HTML)
                result = {
                    "cpu": cpu,
                    "gpu": gpu,
                    "ram": ram,
                    "storage": storage,
                    "psu": psu,
                    "motherboard": motherboard,
                    "total": total,
                    "power": ratio['score'],
                    "type_name": ratio['name']
                }
        except ValueError:
            error = "Введіть коректне числове значення."

    return render(request, "home.html", {
        "result": result, 
        "error": error, 
        "selected_type": pc_type, 
        "selected_budget": budget_str
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