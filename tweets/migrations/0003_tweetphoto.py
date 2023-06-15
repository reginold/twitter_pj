# Generated by Django 3.1.3 on 2022-06-02 07:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tweets", "0002_auto_20220317_0303"),
    ]

    operations = [
        migrations.CreateModel(
            name="TweetPhoto",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="")),
                ("order", models.IntegerField(default=0)),
                (
                    "status",
                    models.IntegerField(
                        choices=[(0, "Pending"), (1, "Approved"), (2, "Rejected")],
                        default=0,
                    ),
                ),
                ("has_deleted", models.BooleanField(default=True)),
                ("deleted_at", models.DateTimeField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tweet",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="tweets.tweet",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "index_together": {
                    ("tweet", "order"),
                    ("has_deleted", "created_at"),
                    ("user", "created_at"),
                    ("status", "created_at"),
                },
            },
        ),
    ]
