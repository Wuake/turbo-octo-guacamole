# Generated by Django 4.1.7 on 2023-05-04 08:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0008_alter_presentation_fichier_pptx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentation',
            name='fichier_pptx',
            field=models.FileField(blank=True, null=True, upload_to='documents', validators=[django.core.validators.FileExtensionValidator(['pptx'])]),
        ),
    ]
