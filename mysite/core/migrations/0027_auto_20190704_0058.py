# Generated by Django 2.2.1 on 2019-07-04 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_campaña_funciones'),
    ]

    operations = [
        migrations.RenameField(
            model_name='campaña',
            old_name='funciones',
            new_name='fk_funciones',
        ),
    ]
