# Generated by Django 3.2 on 2022-01-18 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repair', '0004_alter_campus_operater_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dormitory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creater_id', models.BigIntegerField(verbose_name='报修者id')),
                ('title', models.CharField(max_length=30, verbose_name='标题')),
                ('campus', models.CharField(max_length=10, verbose_name='校区')),
                ('buldding_name', models.CharField(max_length=10, verbose_name='地点')),
                ('dormitory_number', models.IntegerField(null=True, verbose_name='宿舍号')),
                ('levelradio', models.CharField(max_length=5, verbose_name='损害程度')),
                ('picture', models.ImageField(blank=True, null=True, upload_to='picture/dormitory/%Y/%m/%d/', verbose_name='照片')),
                ('description', models.TextField(default='', null=True, verbose_name='描述')),
                ('done', models.BooleanField(default=False, verbose_name='是否已处理')),
                ('operater_id', models.BigIntegerField(default='0000', null=True, verbose_name='维修者')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '宿舍报修列表',
                'verbose_name_plural': '宿舍报修列表',
            },
        ),
        migrations.AlterModelOptions(
            name='campus',
            options={'verbose_name': '校园报修列表', 'verbose_name_plural': '校园报修列表'},
        ),
        migrations.AlterField(
            model_name='campus',
            name='description',
            field=models.TextField(default='', null=True, verbose_name='描述'),
        ),
        migrations.AlterField(
            model_name='campus',
            name='done',
            field=models.BooleanField(default=False, verbose_name='是否已处理'),
        ),
    ]
