# Generated by Django 3.2.5 on 2021-12-04 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0011_match'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='result',
            new_name='status',
        ),
    ]