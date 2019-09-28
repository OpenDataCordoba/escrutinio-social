# Generated by Django 2.2.2 on 2019-09-28 17:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fiscales', '0012_fiscal_puntaje_scoring_troll'),
        ('adjuntos', '0014_reemplazo_taken'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSVTareaDeImportacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('csv', models.FileField(upload_to='')),
                ('status', model_utils.fields.StatusField(choices=[('pendiente', 'pendiente'), ('en progreso', 'en progreso'), ('procesado', 'procesado'), ('error', 'error')], default='pendiente', max_length=100, no_check_for_status=True)),
                ('errores', models.TextField(blank=True, null=True)),
                ('mesas_total_ok', models.PositiveIntegerField(default=0)),
                ('mesas_parc_ok', models.PositiveIntegerField(default=0)),
                ('fiscal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fiscales.Fiscal')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
