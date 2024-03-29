# Generated by Django 4.2.10 on 2024-02-12 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("servers", "0002_outlineserver_country"),
    ]

    operations = [
        migrations.AlterField(
            model_name="outlineserver",
            name="keys_per_user",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="outlineserver",
            name="max_data_per_key",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="outlineserver",
            name="port",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="outlineserver",
            name="url",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="outlineserverkey",
            name="data_limit",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="outlineserverkey",
            name="data_used",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="outlineserverkey",
            name="key",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="outlineserverkey",
            name="key_id",
            field=models.CharField(default="", max_length=255),
        ),
    ]
