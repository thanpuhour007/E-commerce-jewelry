# Generated by Django 3.2 on 2024-10-20 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myadmin', '0023_remove_payment_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10),
        ),
    ]