# Generated by Django 5.0.2 on 2025-02-03 22:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_invoicepayment_is_refunded'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=255)),
                ('ref', models.CharField(max_length=255)),
                ('currency', models.CharField(max_length=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fees', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_receive', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('phone', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('type_transaction', models.CharField(max_length=20)),
                ('operator', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField()),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_payment', to='api.invoice')),
            ],
        ),
    ]
