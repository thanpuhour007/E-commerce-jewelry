# Generated by Django 3.2 on 2024-09-26 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myadmin', '0006_auto_20240926_1605'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='product',
            name='unique_product_in_category_type',
        ),
    ]