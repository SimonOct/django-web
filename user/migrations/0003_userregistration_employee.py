# Generated by Django 3.2 on 2022-01-17 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_emailvalidation_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userregistration',
            name='employee',
            field=models.BooleanField(default=False, verbose_name='是否是雇员'),
        ),
    ]
