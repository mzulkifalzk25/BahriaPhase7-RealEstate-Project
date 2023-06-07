# Generated by Django 4.2.1 on 2023-05-24 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0006_alter_listing_realtor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='bathrooms',
            field=models.DecimalField(decimal_places=0, max_digits=2),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_1',
            field=models.ImageField(blank=True, upload_to='home/'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_2',
            field=models.ImageField(blank=True, upload_to='home/'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_3',
            field=models.ImageField(blank=True, upload_to='home/'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='photo_main',
            field=models.ImageField(upload_to='home/'),
        ),
    ]