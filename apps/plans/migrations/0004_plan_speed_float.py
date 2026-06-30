import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plans", "0003_plan_speed_and_features"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plan",
            name="download_speed",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                help_text="Average download speed in Mbps. e.g. 73.6",
                verbose_name="Download Speed (Mbps)",
            ),
        ),
        migrations.AlterField(
            model_name="plan",
            name="upload_speed",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                help_text="Average upload speed in Mbps. e.g. 18.4",
                verbose_name="Upload Speed (Mbps)",
            ),
        ),
    ]
