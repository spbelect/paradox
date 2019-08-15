# Generated by Django 2.2.3 on 2019-07-30 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0005_auto_20190712_0241'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputevent',
            name='refuse_person',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='coordinator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='paradox.Coordinator'),
        ),
    ]
