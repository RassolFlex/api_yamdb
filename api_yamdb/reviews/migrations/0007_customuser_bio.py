# Generated by Django 3.2 on 2024-01-17 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20240117_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='Информация'),
        ),
    ]
