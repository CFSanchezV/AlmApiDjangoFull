# Generated by Django 3.2.8 on 2022-04-10 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0006_alter_itempedido_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prenda',
            name='inventario',
            field=models.PositiveIntegerField(null=True),
        ),
    ]