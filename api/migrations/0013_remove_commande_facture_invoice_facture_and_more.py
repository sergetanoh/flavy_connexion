# Generated by Django 5.0.2 on 2024-11-03 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_invoice_invoiceitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commande',
            name='Facture',
        ),
        migrations.AddField(
            model_name='invoice',
            name='facture',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('brouilon', 'Brouillon'), ('envoyee', 'Envoyée'), ('impayee', 'Impayée'), ('payee', 'Payée'), ('en_retard', 'En retard')], default='impayee', max_length=10),
        ),
    ]