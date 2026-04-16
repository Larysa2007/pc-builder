from django.contrib import admin
from .models import Cpu, Gpu, Ram, Storage, Psu, Motherboard

admin.site.register(Cpu)
admin.site.register(Gpu)
admin.site.register(Ram)
admin.site.register(Storage)
admin.site.register(Psu)
admin.site.register(Motherboard)