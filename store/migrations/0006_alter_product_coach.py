# Generated by Django 4.2.5 on 2023-09-24 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_product_coach'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='coach',
            field=models.TextField(default='Generic', max_length=200),
        ),
    ]
