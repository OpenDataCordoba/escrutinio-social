# Generated by Django 2.2.2 on 2019-07-30 00:03

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('elecciones', '0038_auto_20190729_1228'),
        ('fiscales', '0005_auto_20190728_0139'),
        ('adjuntos', '0011_merge_20190729_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='subido_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachments_subidos', to='fiscales.Fiscal'),
        ),
        migrations.CreateModel(
            name='PreIdentificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('circuito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='elecciones.Circuito')),
                ('distrito', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='elecciones.Distrito')),
                ('fiscal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='fiscales.Fiscal')),
                ('seccion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='elecciones.Seccion')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='pre_identificacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachment', to='adjuntos.PreIdentificacion'),
        ),
    ]
