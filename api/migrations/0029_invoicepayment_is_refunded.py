# Generated by Django 5.0.2 on 2025-02-03 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_invoice_service_fees_invoice_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicepayment',
            name='is_refunded',
            field=models.BooleanField(default=False),
        ),
    ]
