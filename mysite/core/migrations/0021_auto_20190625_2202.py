# Generated by Django 2.2.1 on 2019-06-26 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20190625_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='canal_1',
            field=models.TextField(default='', max_length=10000),
        ),
        migrations.AlterField(
            model_name='audio',
            name='canal_2',
            field=models.TextField(default='', max_length=10000),
        ),
        migrations.AlterField(
            model_name='reporte',
            name='canal_1',
            field=models.TextField(default='', max_length=10000),
        ),
        migrations.AlterField(
            model_name='reporte',
            name='canal_2',
            field=models.TextField(default='', max_length=10000),
        ),
    ]
