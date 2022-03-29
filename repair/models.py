from statistics import mode
from django.db import models


# Create your models here.

class Campus(models.Model):
    creater_id = models.BigIntegerField(verbose_name='报修者id', null=False)
    title = models.CharField(verbose_name='标题' , max_length=30, null=False)
    campus = models.CharField(max_length=10, verbose_name='校区', null=False)
    buldding_name = models.CharField(verbose_name='地点', max_length=10, null=False)
    levelradio = models.CharField(verbose_name='损害程度', max_length=5, null=False)
    picture = models.ImageField(verbose_name='照片', upload_to='picture/campus/%Y/%m/%d/', blank=True, null=True)
    description = models.TextField(verbose_name='描述', default='', null=True)
    done = models.BooleanField(verbose_name='是否已处理', default=False)
    operater_id = models.BigIntegerField(verbose_name='维修者', default='0000', null=True)
    date_added = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    date_update = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self) -> str:
        return f'{self.levelradio}|{self.campus}|{self.buldding_name}|{self.title}|{self.done}'
    
    class Meta:
        verbose_name = '校园报修列表'
        verbose_name_plural = '校园报修列表'

class Dormitory(models.Model):
    creater_id = models.BigIntegerField(verbose_name='报修者id', null=False)
    title = models.CharField(verbose_name='标题' , max_length=30, null=False)
    campus = models.CharField(max_length=10, verbose_name='校区', null=False)
    buldding_name = models.CharField(verbose_name='地点', max_length=10, null=False)
    dormitory_number = models.IntegerField(verbose_name='宿舍号', null=True, default=0)
    levelradio = models.CharField(verbose_name='损害程度', max_length=5, null=False)
    picture = models.ImageField(verbose_name='照片', upload_to='picture/dormitory/%Y/%m/%d/', blank=True, null=True)
    description = models.TextField(verbose_name='描述', default='', null=True)
    done = models.BooleanField(verbose_name='是否已处理', default=False)
    operater_id = models.BigIntegerField(verbose_name='维修者', default='0000', null=True)
    date_added = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    date_update = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self) -> str:
        return f'{self.levelradio}|{self.campus}|{self.buldding_name}{self.dormitory_number}|{self.title}|{self.done}'
    
    class Meta:
        verbose_name = '宿舍报修列表'
        verbose_name_plural = '宿舍报修列表'