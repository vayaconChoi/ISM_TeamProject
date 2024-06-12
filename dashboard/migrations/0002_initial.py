# Generated by Django 4.2.13 on 2024-06-12 06:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="warehousing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="warehousing",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.warehouse"
            ),
        ),
        migrations.AddField(
            model_name="warehouse",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="shipping",
            name="barcode",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.barcode"
            ),
        ),
        migrations.AddField(
            model_name="shipping",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="shipping",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.warehouse"
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="barcode",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.barcode"
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="inventory",
            name="warehouse",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.warehouse"
            ),
        ),
        migrations.AddField(
            model_name="barcode",
            name="fruit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.fruit"
            ),
        ),
        migrations.AddField(
            model_name="barcode",
            name="origin",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="dashboard.origin"
            ),
        ),
        migrations.AddField(
            model_name="barcode",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
