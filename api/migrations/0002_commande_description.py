# Generated by Django 5.0.2 on 2024-02-28 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
