# Generated by Django 5.0.2 on 2024-11-23 15:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_alter_invoicepayment_type_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='recherche',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commande_recherche', to='api.recherche'),
        ),
        migrations.AlterField(
            model_name='commande',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commande_client', to='api.client'),
        ),
        migrations.AlterField(
            model_name='recherche',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recherche_client', to='api.client'),
        ),
    ]