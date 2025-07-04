# Generated by Django 5.0.2 on 2025-05-01 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_refreshtoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='scraped_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='PENDING', max_length=20),
        ),
    ]
