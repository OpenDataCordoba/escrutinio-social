# Generated by Django 2.2.2 on 2019-08-02 01:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elecciones', '0040_auto_20190730_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='seccion',
            name='cantidad_minima_prioridad_hasta_2',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='seccion',
            name='prioridad_10_a_100',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='seccion',
            name='prioridad_2_a_10',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='seccion',
            name='prioridad_hasta_2',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='prioridad',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, validators=[django.core.validators.MaxValueValidator(1000000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='seccion',
            name='prioridad',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
    ]