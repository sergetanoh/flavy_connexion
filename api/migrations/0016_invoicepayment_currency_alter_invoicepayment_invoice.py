# Generated by Django 5.0.2 on 2024-11-13 07:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_invoicepayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicepayment',
            name='currency',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='invoicepayment',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='api.invoice'),
        ),
    ]
