# Generated by Django 4.2.5 on 2023-09-24 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_remove_product_stock_product_coach'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='coach',
            field=models.TextField(max_length=200, unique=True),
        ),
    ]
