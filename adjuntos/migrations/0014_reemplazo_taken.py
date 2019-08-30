# Generated by Django 2.2.2 on 2019-08-14 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adjuntos', '0013_auto_20190804_2322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='taken',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='taken_by',
        ),
        migrations.AddField(
            model_name='attachment',
            name='cant_fiscales_asignados',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='attachment',
            name='cant_asignaciones_realizadas',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
