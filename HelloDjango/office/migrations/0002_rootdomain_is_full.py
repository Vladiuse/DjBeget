# Generated by Django 3.2.2 on 2022-01-03 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rootdomain',
            name='is_full',
            field=models.BooleanField(default=False, verbose_name='Привышен ли лимит поддоменов'),
        ),
    ]