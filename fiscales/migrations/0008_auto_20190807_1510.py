# Generated by Django 2.2.2 on 2019-08-07 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiscales', '0007_merge_20190804_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fiscal',
            name='referente_apellido',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='fiscal',
            name='referente_nombres',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]