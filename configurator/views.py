from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    budget_str = ""
    pc_type = "gaming"
    manual_ids = {}

    context = {
        "all_cpus": Cpu.objects.all().order_by('name'),
        "all_gpus": Gpu.objects.all().order_by('name'),
        "all_mbs": Motherboard.objects.all().order_by('name'),
        "all_rams": Ram.objects.all().order_by('name'),
    }

    if request.method == "POST":
        budget_str = request.POST.get("budget", "")
        pc_type = request.POST.get("pc_type", "gaming")
        
        try:
            budget = int(budget_str) if budget_str and budget_str.isdigit() else 0
            
            # 1. ПЕРЕВІРКА НА МІНІМАЛЬНУ СУМУ
            if budget < 8000:
                raise ValueError("Мінімальний бюджет для збірки ПК — 8000 грн. Будь ласка, введіть більшу суму.")

            ratios = {
                "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'label': 'ігор'},
                "streaming": {'cpu': 0.35, 'gpu': 0.30, 'ram': 0.15, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.05, 'label': 'стрімінгу'},
                "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'label': 'офісу'},
                "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'label': 'роботи'},
            }
            
            variants = [
                {"name": "Максимальна потужність", "mult": 1.0},
                {"name": "Оптимальний баланс", "mult": 0.85},
                {"name": "Бюджетний варіант", "mult": 0.70},
            ]

            base_ratio = ratios.get(pc_type, ratios["gaming"])

            for var in variants:
                current_budget = budget * var["mult"]
                explanations = []
                
                # Підбір з поясненнями
                cpu = Cpu.objects.filter(price__lte=current_budget * base_ratio['cpu']).order_by('-price').first()
                if cpu: explanations.append(f"🧠 {cpu.name}: Обрано для високої швидкості обробки даних у задачах {base_ratio['label']}.")
                else: cpu = Cpu.objects.order_by('price').first()

                gpu = Gpu.objects.filter(price__lte=current_budget * base_ratio['gpu']).order_by('-price').first()
                if gpu: explanations.append(f"🎮 {gpu.name}: Забезпечує необхідну графічну потужність.")
                else: explanations.append("⚠️ Використовується вбудоване графічне ядро (економія).")

                mb = Motherboard.objects.filter(socket=cpu.socket if cpu else None, price__lte=current_budget * base_ratio['mb']).order_by('-price').first()
                if mb: explanations.append(f"🔌 {mb.name}: Надійна основа з підтримкою сокета {cpu.socket}.")

                ram = Ram.objects.filter(price__lte=current_budget * base_ratio['ram']).order_by('-price').first()
                if ram: explanations.append(f"⚡ {ram.name}: Оптимальний об'єм пам'яті для стабільної роботи.")

                storage = Storage.objects.filter(price__lte=current_budget * base_ratio['ssd']).order_by('-price').first()
                if storage: explanations.append(f"💾 {storage.name}: Швидкий накопичувач для миттєвого завантаження системи.")

                psu = Psu.objects.filter(price__lte=current_budget * base_ratio['psu']).order_by('-price').first()
                if psu: explanations.append(f"🔋 {psu.name}: Блок живлення з запасом потужності для безпеки.")

                items = [cpu, gpu, ram, storage, psu, mb]
                total_price = sum(item.price for item in items if item)

                results.append({
                    "variant_name": var["name"],
                    "cpu": cpu, "gpu": gpu, "ram": ram, "storage": storage,
                    "psu": psu, "motherboard": mb, "total": total_price,
                    "explanations": explanations
                })

        except Exception as e:
            error = str(e)

    context.update({
        "results": results, 
        "error": error, 
        "selected_budget": budget_str,
        "selected_type": pc_type,
    })
    return render(request, "home.html", context)