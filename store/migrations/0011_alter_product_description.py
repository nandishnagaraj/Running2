# Generated by Django 4.2.5 on 2023-10-07 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_product_coach'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, max_length=1500),
        ),
    ]
