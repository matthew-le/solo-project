# Generated by Django 2.2 on 2021-08-12 02:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snowboard_app', '0002_auto_20210812_0155'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='CustomUser',
        ),
    ]
