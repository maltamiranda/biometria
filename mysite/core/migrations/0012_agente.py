# Generated by Django 2.2.1 on 2019-06-02 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_campaña_audio_analisis_campaña_funciones'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default='', max_length=60, unique=True)),
            ],
        ),
    ]
