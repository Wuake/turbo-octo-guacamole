# Generated by Django 4.1.7 on 2023-04-18 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="day",
            name="congress",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="confs_days",
                to="planning.congress",
            ),
            preserve_default=False,
        ),
    ]
