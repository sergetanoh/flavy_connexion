# Generated by Django 5.0.2 on 2024-11-13 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_invoicepayment_type_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicepayment',
            name='type_payment',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
