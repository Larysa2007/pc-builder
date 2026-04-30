from django.shortcuts import render
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

def home(request):
    results = []
    error = None
    budget_str = ""  # Додано: ініціалізація змінної, щоб уникнути помилки UnboundLocalError
    pc_type = "gaming" # Початкове значення за замовчуванням
    manual_ids = {}

    # Попереднє завантаження всіх списків для конструктора
    context = {
        "all_cpus": Cpu.objects.all().order_by('name'),
        "all_gpus": Gpu.objects.all().order_by('name'),
        "all_mbs": Motherboard.objects.all().order_by('name'),
        "all_rams": Ram.objects.all().order_by('name'),
    }

    if request.method == "POST":
        budget_str = request.POST.get("budget", "")
        pc_type = request.POST.get("pc_type", "gaming")
        
        # Отримуємо ID деталей, які користувач обрав вручну
        manual_ids = {
            'cpu': request.POST.get("cpu_id"),
            'gpu': request.POST.get("gpu_id"),
            'mb': request.POST.get("mb_id"),
            'ram': request.POST.get("ram_id"),
        }

        try:
            budget = int(budget_str) if budget_str and budget_str.isdigit() else 0
            
            # Коефіцієнти розподілу бюджету та мітки для пояснень
            ratios = {
                "gaming": {'cpu': 0.25, 'gpu': 0.40, 'ram': 0.12, 'ssd': 0.08, 'psu': 0.07, 'mb': 0.08, 'label': 'ігрових задач'},
                "office": {'cpu': 0.40, 'gpu': 0.05, 'ram': 0.15, 'ssd': 0.15, 'psu': 0.10, 'mb': 0.15, 'label': 'офісної роботи'},
                "work":   {'cpu': 0.35, 'gpu': 0.20, 'ram': 0.20, 'ssd': 0.10, 'psu': 0.05, 'mb': 0.10, 'label': 'професійної роботи'},
            }
            ratio = ratios.get(pc_type, ratios["gaming"])
            explanations = []

            # --- ПІДБІР КОМПОНЕНТІВ ---

            # 1. ПРОЦЕСОР
            if manual_ids.get('cpu'):
                cpu = Cpu.objects.get(id=manual_ids['cpu'])
                explanations.append(f"✅ Процесор {cpu.name} обрано вами вручну.")
            else:
                cpu = Cpu.objects.filter(price__lte=budget * ratio['cpu']).order_by('-price').first()
                if cpu: explanations.append(f"🤖 Процесор {cpu.name} підібрано як оптимальний за ціною для {ratio['label']}.")

            if not cpu: raise ValueError("Бюджет занадто малий для підбору процесора.")

            # 2. МАТЕРИНСЬКА ПЛАТА
            if manual_ids.get('mb'):
                motherboard = Motherboard.objects.get(id=manual_ids['mb'])
                if motherboard.socket != cpu.socket:
                    error = f"❌ Помилка сумісності: Материнка ({motherboard.socket}) не підходить до CPU ({cpu.socket})!"
                explanations.append(f"✅ Материнську плату {motherboard.name} обрано вами.")
            else:
                motherboard = Motherboard.objects.filter(socket=cpu.socket, price__lte=budget * ratio['mb']).order_by('-price').first()
                if not motherboard:
                    motherboard = Motherboard.objects.filter(socket=cpu.socket).order_by('price').first()
                if motherboard:
                    explanations.append(f"⚙️ Плата {motherboard.name} автоматично перевірена на сумісність із сокетом {cpu.socket}.")

            # 3. ВІДЕОКАРТА
            if manual_ids.get('gpu'):
                gpu = Gpu.objects.get(id=manual_ids['gpu'])
                explanations.append(f"✅ Відеокарту {gpu.name} обрано вами.")
            else:
                gpu = Gpu.objects.filter(price__lte=budget * ratio['gpu']).order_by('-price').first()
                if gpu: explanations.append(f"🎮 Відеокарта {gpu.name} забезпечує найкращу графіку для даного бюджету.")
                else: explanations.append("⚠️ Використовується вбудоване графічне ядро для економії коштів.")

            # 4. ОПЕРАТИВНА ПАМ'ЯТЬ
            if manual_ids.get('ram'):
                ram = Ram.objects.get(id=manual_ids['ram'])
                explanations.append(f"✅ ОЗП {ram.name} обрано вами.")
            else:
                ram = Ram.objects.filter(price__lte=budget * ratio['ram']).order_by('-price').first()
                if ram: explanations.append(f"⚡ Пам'ять {ram.name} обрана для стабільної роботи додатків.")

            # 5. НАКОПИЧУВАЧ ТА БЛОК ЖИВЛЕННЯ
            storage = Storage.objects.filter(price__lte=budget * ratio['ssd']).order_by('-price').first()
            psu = Psu.objects.filter(price__lte=budget * ratio['psu']).order_by('-price').first()
            if storage: explanations.append(f"💾 Накопичувач {storage.name} забезпечить швидкість роботи ОС.")
            if psu: explanations.append(f"🔌 Блок живлення {psu.name} підібрано під потужність системи.")

            # Розрахунок загальної вартості
            items = [cpu, gpu, ram, storage, psu, motherboard]
            total_price = sum(item.price for item in items if item)

            if total_price > budget and budget > 0:
                error = f"Увага: Загальна вартість ({total_price} грн) перевищила вказаний бюджет!"

            results.append({
                "cpu": cpu, "gpu": gpu, "ram": ram, "storage": storage,
                "psu": psu, "motherboard": motherboard, "total": total_price,
                "explanations": explanations
            })

        except Exception as e:
            error = str(e)

    # Оновлюємо контекст для відображення результатів
    context.update({
        "results": results, 
        "error": error, 
        "selected_budget": budget_str,
        "selected_type": pc_type,
        "manual": manual_ids
    })
    
    return render(request, "home.html", context)