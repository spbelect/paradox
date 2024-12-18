# Generated by Django 2.2.3 on 2019-12-20 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0011_auto_20191220_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoolAnswer',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='paradox.Answer')),
                ('value', models.BooleanField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('paradox.answer',),
        ),
        migrations.CreateModel(
            name='IntegerAnswer',
            fields=[
                ('answer_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='paradox.Answer')),
                ('value', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('paradox.answer',),
        ),
        migrations.RenameField(
            model_name='inputeventimage',
            old_name='event',
            new_name='answer',
        ),
        migrations.RenameField(
            model_name='inputeventusercomment',
            old_name='event',
            new_name='answer',
        ),
    ]