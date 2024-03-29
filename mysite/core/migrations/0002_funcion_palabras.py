# Generated by Django 2.2.1 on 2019-05-16 00:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Funcion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30, unique=True)),
                ('descripcion', models.CharField(max_length=255)),
                ('frase', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Palabras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('palabra', models.CharField(max_length=30, unique=True)),
                ('fk_funcion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='funcion', to='core.Funcion')),
            ],
            options={
                'unique_together': {('fk_funcion', 'palabra')},
            },
        ),
    ]
