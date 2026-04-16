from django.db import models

class Cpu(models.Model):
    name = models.CharField(max_length=100)
    cores = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name


class Gpu(models.Model):
    name = models.CharField(max_length=100)
    memory = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name


class Ram(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return self.name


# 🔥 ОБОВ'ЯЗКОВО ДОДАЙ ЦЕ

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
    price = models.IntegerField()

    def __str__(self):
        return self.name