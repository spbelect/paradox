# Generated by Django 2.2.3 on 2019-12-20 17:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0013_auto_20191220_1126'),
    ]

    operations = [
        migrations.RenameField(
            model_name='answer',
            old_name='input_id',
            new_name='question_id',
        ),
    ]
