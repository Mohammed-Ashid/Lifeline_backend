# Generated by Django 5.1.7 on 2025-03-15 19:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedRequest",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("requestedDate", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Approved", "Approved"),
                            ("Rejected", "Rejected"),
                        ],
                        default="Pending",
                        max_length=20,
                    ),
                ),
                ("updatedDate", models.DateTimeField(auto_now=True)),
                (
                    "feedId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feed_requests",
                        to="app1.feed",
                    ),
                ),
                (
                    "secondPersonId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feed_requests",
                        to="app1.person",
                    ),
                ),
            ],
        ),
    ]
