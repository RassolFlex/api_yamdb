# Generated by Django 3.2 on 2024-01-26 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_apiuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiuser',
            name='role',
            field=models.CharField(choices=[('user', 'Пользователь'), ('moderator', 'Модератор'), ('admin', 'Администратор')], default='user', max_length=30, verbose_name='Роль'),
        ),
    ]
