# Generated by Django 4.2.13 on 2024-06-10 20:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curtain', '0003_remove_curtain_encrypted_with_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_access', models.DateTimeField(auto_now=True)),
                ('curtain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='last_access', to='curtain.curtain')),
            ],
        ),
    ]