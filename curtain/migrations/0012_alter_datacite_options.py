# Generated by Django 5.1.4 on 2024-12-13 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curtain', '0011_datacite_lock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datacite',
            options={'ordering': ['-updated']},
        ),
    ]
