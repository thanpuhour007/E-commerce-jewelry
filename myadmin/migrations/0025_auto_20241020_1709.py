# Generated by Django 3.2 on 2024-10-20 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myadmin', '0024_alter_order_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_order', to='myadmin.order'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_payment', to='myadmin.payment'),
        ),
    ]
