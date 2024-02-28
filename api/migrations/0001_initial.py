# Generated by Django 5.0.2 on 2024-02-28 14:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('username', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=True)),
                ('date_joined', models.DateField(auto_now_add=True)),
                ('is_pharmacie', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prenom', models.CharField(max_length=255)),
                ('adresse', models.CharField(max_length=255)),
                ('ville', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=15)),
                ('image', models.CharField(max_length=255)),
                ('n_cmu', models.CharField(blank=True, max_length=255, null=True)),
                ('n_assurance', models.CharField(blank=True, max_length=255, null=True)),
                ('sexe', models.CharField(choices=[('Homme', 'Homme'), ('Femme', 'Femme')], max_length=10)),
                ('maladie_chronique', models.TextField(blank=True, null=True)),
                ('poids', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('taille', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('num_pharmacie', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pharmacie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_pharmacie', models.CharField(blank=True, max_length=20, null=True)),
                ('nom_pharmacie', models.CharField(blank=True, max_length=255, null=True)),
                ('adresse_pharmacie', models.CharField(blank=True, max_length=255, null=True)),
                ('commune_pharmacie', models.CharField(blank=True, max_length=100, null=True)),
                ('ville_pharmacie', models.CharField(blank=True, max_length=100, null=True)),
                ('numero_contact_pharmacie', models.CharField(blank=True, max_length=20, null=True)),
                ('horaire_ouverture_pharmacie', models.CharField(blank=True, max_length=255, null=True)),
                ('degarde', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacie_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Conseil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('pharmacie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.pharmacie')),
            ],
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordornance', models.CharField(blank=True, max_length=255, null=True)),
                ('nom_medicament', models.CharField(blank=True, max_length=255, null=True)),
                ('quantite', models.PositiveIntegerField(default=1)),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('traite', 'Traité'), ('en_cours', 'En cours de livraison'), ('livree', 'Livrée'), ('termine', 'Terminé'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('en_attente', models.BooleanField(default=True)),
                ('terminer', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_livraison', models.DateTimeField(blank=True, null=True)),
                ('Facture', models.CharField(blank=True, max_length=255, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('pharmacie_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.pharmacie')),
            ],
        ),
    ]
