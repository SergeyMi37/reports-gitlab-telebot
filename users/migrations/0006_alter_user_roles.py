# Generated by Django 3.2.9 on 2024-08-09 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20240809_1425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='roles',
            field=models.CharField(blank=True, default='', help_text='Роли пользователя через запятую', max_length=256, null=True),
        ),
    ]
