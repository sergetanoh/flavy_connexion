# Generated by Django 5.0.2 on 2024-03-02 00:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_commande_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recherche',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordonnance', models.CharField(blank=True, max_length=255, null=True)),
                ('nom_medicament', models.CharField(blank=True, max_length=255, null=True)),
                ('quantite', models.PositiveIntegerField(default=1)),
                ('description', models.TextField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('trouve', 'Trouvé'), ('termine', 'Terminé'), ('annulee', 'Annulée')], default='en_attente', max_length=255)),
                ('en_attente', models.BooleanField(default=True)),
                ('terminer', models.BooleanField(default=False)),
                ('facture', models.TextField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('pharmacie_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.pharmacie')),
            ],
        ),
    ]