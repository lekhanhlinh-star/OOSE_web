# Generated by Django 4.1.7 on 2023-05-26 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("CustomerSite", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Image",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="laptop_images")),
            ],
        ),
        migrations.RemoveField(
            model_name="laptop",
            name="image",
        ),
        migrations.AddField(
            model_name="laptop",
            name="images",
            field=models.ManyToManyField(to="CustomerSite.image"),
        ),
    ]
