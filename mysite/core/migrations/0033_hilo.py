# Generated by Django 2.2.1 on 2019-10-01 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20190915_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hilo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ultimo', models.CharField(default='', max_length=50)),
                ('hilo', models.IntegerField()),
            ],
        ),
    ]