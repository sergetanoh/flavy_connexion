# Generated by Django 5.0.2 on 2024-12-01 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_alter_commande_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='code_recu',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]