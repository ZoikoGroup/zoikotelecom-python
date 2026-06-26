import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_alter_plan_id_alter_plancategory_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='download_speed',
            field=models.PositiveIntegerField(blank=True, help_text='Average download speed in Mbps. e.g. 40', null=True, verbose_name='Download Speed (Mbps)'),
        ),
        migrations.AddField(
            model_name='plan',
            name='upload_speed',
            field=models.PositiveIntegerField(blank=True, help_text='Average upload speed in Mbps. e.g. 10', null=True, verbose_name='Upload Speed (Mbps)'),
        ),
        migrations.CreateModel(
            name='PlanFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(help_text='A feature/benefit line, e.g. "No Long-Term Contracts".', max_length=255, verbose_name='Feature')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Sort Order')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='plans.plan', verbose_name='Plan')),
            ],
            options={
                'verbose_name': 'Plan Feature',
                'verbose_name_plural': 'Plan Features',
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]
