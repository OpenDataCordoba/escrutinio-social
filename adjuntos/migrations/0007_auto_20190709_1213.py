# Generated by Django 2.2.1 on 2019-07-09 15:13

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('adjuntos', '0006_auto_20190708_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='identificacion',
            name='consolidada',
            field=models.BooleanField(default=False, help_text='una identificacion consolidada es aquella que se considera representativa y determina el estado del attachment'),
        ),
        migrations.AlterField(
            model_name='identificacion',
            name='attachment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identificaciones', to='adjuntos.Attachment'),
        ),
        migrations.AlterField(
            model_name='identificacion',
            name='fiscal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fiscales.Fiscal'),
        ),
        migrations.AlterField(
            model_name='identificacion',
            name='mesa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='elecciones.Mesa'),
        ),
        migrations.AlterField(
            model_name='identificacion',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='sin_identificar', max_length=100, no_check_for_status=True),
        ),
    ]
