# Generated by Django 3.2 on 2024-09-27 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myadmin', '0008_auto_20240927_0803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_status',
            field=models.BooleanField(),
        ),
    ]