# Generated by Django 4.2.5 on 2023-09-29 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_cartitem_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(),
        ),
    ]
