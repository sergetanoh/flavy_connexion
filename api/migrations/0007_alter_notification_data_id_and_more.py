# Generated by Django 5.0.2 on 2024-03-18 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_notification_client_firebase_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='data_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='metadata',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
