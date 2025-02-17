# Generated by Django 5.0.2 on 2024-11-03 14:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_client_sexe_alter_conseil_titre_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_date', models.DateField(auto_now_add=True)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('draft', 'Brouillon'), ('sent', 'Envoyée'), ('unpaid', 'Impayée'), ('paid', 'Payée'), ('overdue', 'En retard')], default='draft', max_length=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('reference', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_invoices', to='api.client')),
                ('commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commande_invoices', to='api.commande')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.invoice')),
            ],
        ),
    ]
