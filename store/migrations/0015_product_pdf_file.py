# Generated by Django 4.2.5 on 2023-10-22 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_reviewrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='pdf_file',
            field=models.FileField(blank=True, null=True, upload_to='pdfs/'),
        ),
    ]