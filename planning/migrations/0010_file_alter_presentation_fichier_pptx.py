# Generated by Django 4.1.7 on 2023-06-02 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0009_alter_presentation_fichier_pptx'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=50)),
                ('eof', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='presentation',
            name='fichier_pptx',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='planning.file'),
        ),
    ]
