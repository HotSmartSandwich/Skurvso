from django.db import models
from django.urls import reverse


class Building(models.Model):
    """Модель здания"""

    id = models.AutoField(primary_key=True)
    name = models.CharField('Название здания', max_length=150)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('building_detail', kwargs={'building_id': self.id})

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = '  Здания'
        ordering = ['name']


class Node(models.Model):
    """Модель узла"""

    id = models.AutoField(primary_key=True)
    name = models.CharField('Название узла', max_length=150)
    host = models.GenericIPAddressField('IP-адрес', protocol='IPv4', unique=True)
    image = models.ImageField('Фото', upload_to='nodes_photo', null=True, blank=True)
    is_monitoring = models.BooleanField('Мониторинг', default=False)
    key = models.CharField('Ключ сессии', max_length=10, default='', null=True, blank=True)
    time_delta = models.FloatField('Разница времени', null=True, blank=True)
    building = models.ForeignKey(Building, verbose_name='Здание', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.building or ""} // {self.name}'

    def get_absolute_url(self):
        return reverse('node_detail', kwargs={'node_id': self.id})

    class Meta:
        verbose_name = 'Узел'
        verbose_name_plural = '  Узлы'
        ordering = ['building', 'name']


class Unit(models.Model):
    """Модель единицы оборудования"""

    id = models.AutoField(primary_key=True)
    name = models.CharField('Название оборудования', max_length=150)
    host = models.GenericIPAddressField('IP-адрес', protocol='IPv4', null=True, blank=True)
    node = models.ForeignKey(Node, verbose_name='Узел', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.node or ""} // {self.name} // {self.host}'

    def get_absolute_url(self):
        return reverse('unit_detail', kwargs={'unit_id': self.id})

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудования'
        ordering = ['node', 'name', 'host']


class Measurement(models.Model):
    """Модель измерения"""

    id = models.BigAutoField(primary_key=True)
    time = models.DateTimeField()
    value = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    class Meta:
        get_latest_by = 'time'
