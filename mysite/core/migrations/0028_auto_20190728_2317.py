# Generated by Django 2.2.1 on 2019-07-29 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20190704_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audio',
            name='ponderacion',
            field=models.FloatField(default=0),
        ),
    ]
