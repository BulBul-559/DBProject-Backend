# Generated by Django 4.2.7 on 2023-12-18 17:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Youthol", "0008_dutyhistory_duty_times"),
    ]

    operations = [
        migrations.AddField(
            model_name="sduter",
            name="birthday",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="sduter",
            name="qq_number",
            field=models.CharField(max_length=30, null=True),
        ),
    ]
