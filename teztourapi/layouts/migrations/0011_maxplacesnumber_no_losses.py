# Generated by Django 2.0.1 on 2018-05-10 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('layouts', '0010_auto_20180423_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='maxplacesnumber',
            name='no_losses',
            field=models.BooleanField(default=False),
        ),
    ]