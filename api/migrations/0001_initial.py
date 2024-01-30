# Generated by Django 5.0.1 on 2024-01-25 22:03

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
            name='Categorie_Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Category', models.CharField(max_length=255)),
                ('Description', models.TextField()),
            ],
        ),
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
                ('Prenom', models.CharField(max_length=255)),
                ('adresse', models.CharField(max_length=255)),
                ('ville', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=15)),
                ('image', models.CharField(max_length=255)),
                ('id_type_assurance', models.IntegerField()),
                ('n_cmu', models.CharField(max_length=255)),
                ('n_assurance', models.CharField(max_length=255)),
                ('sexe', models.CharField(choices=[('Homme', 'Homme'), ('Femme', 'Femme')], max_length=10)),
                ('maladie_chronique', models.TextField()),
                ('poids', models.DecimalField(decimal_places=2, max_digits=5)),
                ('taille', models.DecimalField(decimal_places=2, max_digits=5)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.PositiveIntegerField()),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('en_cours', 'En cours de livraison'), ('livree', 'Livrée'), ('annulee', 'Annulée')], default='en_attente', max_length=20)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_livraison', models.DateTimeField(blank=True, null=True)),
                ('generer_recu', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
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
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pharmacie_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Date_Facture', models.DateTimeField(auto_now_add=True)),
                ('Montant_Total_Facture', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Nom_Produit', models.CharField(max_length=255)),
                ('Quantite_Produit', models.PositiveIntegerField()),
                ('Prix_Unitaire_Produit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Nom_Pharmacie', models.CharField(max_length=255)),
                ('Nom_Commande', models.CharField(max_length=255)),
                ('Statut_Paiement', models.CharField(choices=[('payee', 'Payée'), ('en_attente', 'En attente de paiement')], default='en_attente', max_length=20)),
                ('Informations_Client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.client')),
                ('id_Commande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.commande')),
                ('Informations_pharmacie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.pharmacie')),
            ],
        ),
        migrations.CreateModel(
            name='Produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nom', models.CharField(max_length=255)),
                ('Description', models.TextField()),
                ('Prix_Unitaire', models.DecimalField(decimal_places=2, max_digits=10)),
                ('Quantite', models.PositiveIntegerField()),
                ('Disponibilite', models.BooleanField(default=True)),
                ('Client_Cible', models.CharField(max_length=255)),
                ('Date_Exp', models.DateField()),
                ('Date_Creation', models.DateTimeField(auto_now_add=True)),
                ('Id_Category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.categorie_produit')),
                ('Id_Pharmacie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.pharmacie')),
            ],
        ),
        migrations.AddField(
            model_name='commande',
            name='produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.produit'),
        ),
    ]
