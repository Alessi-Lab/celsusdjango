# Generated by Django 4.1.1 on 2022-11-02 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('celsus', '0018_genenamemap_entry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to='media/files/user_upload/'),
        ),
    ]