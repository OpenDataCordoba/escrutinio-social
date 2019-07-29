# Generated by Django 2.2.2 on 2019-07-29 03:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elecciones', '0043_auto_20190728_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgrupacionCircuito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='agrupacioncircuitos',
            name='circuitos',
        ),
        migrations.AddField(
            model_name='agrupacioncircuitos',
            name='circuitos',
            field=models.ManyToManyField(related_name='agrupaciones', through='elecciones.AgrupacionCircuito', to='elecciones.Circuito'),
        ),
        migrations.AddField(
            model_name='agrupacioncircuito',
            name='agrupacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elecciones.AgrupacionCircuitos'),
        ),
        migrations.AddField(
            model_name='agrupacioncircuito',
            name='circuito',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elecciones.Circuito'),
        ),
    ]
