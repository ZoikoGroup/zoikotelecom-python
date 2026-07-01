from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0004_alter_productvariant_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="productcategory",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="category_images/"
            ),
        ),
    ]
