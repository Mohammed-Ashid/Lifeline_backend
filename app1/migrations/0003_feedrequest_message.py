# Generated by Django 5.1.7 on 2025-03-15 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0002_feedrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedrequest",
            name="message",
            field=models.TextField(blank=True, null=True),
        ),
    ]
