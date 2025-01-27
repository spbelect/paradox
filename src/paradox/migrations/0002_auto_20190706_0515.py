# Generated by Django 2.2 on 2019-07-06 10:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputevent',
            name='revoked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='inputevent',
            name='id',
            field=models.CharField(default=uuid.uuid4, max_length=40, primary_key=True, serialize=False),
        ),
    ]
