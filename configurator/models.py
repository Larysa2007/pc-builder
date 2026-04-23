from django.db import models

class Cpu(models.Model):
    name = models.CharField(max_length=100)
    socket = models.CharField(max_length=50, help_text="Наприклад: AM4, LGA1700")
    cores = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.socket})"

class Gpu(models.Model):
    name = models.CharField(max_length=100)
    memory = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Ram(models.Model):
    name = models.CharField(max_length=100)
    ram_type = models.CharField(max_length=10, default="DDR4", help_text="DDR4 або DDR5")
    size = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.ram_type}"

class Storage(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Psu(models.Model):
    name = models.CharField(max_length=100)
    power = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name

class Motherboard(models.Model):
    name = models.CharField(max_length=100)
    socket = models.CharField(max_length=50)
    ram_type = models.CharField(max_length=10, default="DDR4")
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.socket}, {self.ram_type})"

class Build(models.Model):
    cpu = models.ForeignKey(Cpu, on_delete=models.SET_NULL, null=True)
    gpu = models.ForeignKey(Gpu, on_delete=models.SET_NULL, null=True, blank=True)
    ram = models.ForeignKey(Ram, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    psu = models.ForeignKey(Psu, on_delete=models.SET_NULL, null=True)
    motherboard = models.ForeignKey(Motherboard, on_delete=models.SET_NULL, null=True)

    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Збірка за {self.total_price} грн"