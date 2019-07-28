# Generated by Django 2.2.2 on 2019-07-25 00:43
from django.db import migrations, models


def actulizar_codigo_referido(apps, schema_editor):
    Fiscal = apps.get_model("fiscales", "Fiscal")
    fiscales = Fiscal.objects.all()
    for i, fiscal in enumerate(fiscales):
        codigo = f'{i:04}'
        fiscal.referido_codigo = codigo
        fiscal.save(update_fields=['referido_codigo'])


def actulizar_codigo_a_none(apps, schema_editor):
    Fiscal = apps.get_model("fiscales", "Fiscal")
    fiscales = Fiscal.objects.all()
    for fiscal in fiscales:
        fiscal.referido_codigo = None
        fiscal.save(update_fields=['referido_codigo'])


class Migration(migrations.Migration):

    dependencies = [
        ('fiscales', '0003_auto_20190723_1559'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE', reverse_sql=migrations.RunSQL.noop),

        migrations.AddField(
            model_name='fiscal',
            name='referido_por_apellido',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),

        migrations.AlterField(
            model_name='fiscal',
            name='referido_codigo',
            field=models.CharField(blank=True, max_length=4, null=True, unique=False),
        ),
        migrations.RunPython(actulizar_codigo_referido, actulizar_codigo_a_none),

        migrations.AlterField(
            model_name='fiscal',
            name='referido_codigo',
            field=models.CharField(blank=True, max_length=4, null=False, unique=True),
        ),


        migrations.AlterField(
            model_name='fiscal',
            name='referido_por_codigo',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.RunSQL(migrations.RunSQL.noop, reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'),
    ]
