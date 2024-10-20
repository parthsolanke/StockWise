# Generated by Django 4.2.8 on 2024-10-20 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_stockprice_core_stockp_symbol_3194c4_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockprice',
            name='close',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockprice',
            name='high',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockprice',
            name='low',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stockprice',
            name='open',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
    ]
