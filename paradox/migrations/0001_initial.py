# Generated by Django 2.2 on 2019-04-20 06:52

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('phones', models.TextField()),
                ('external_channels', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InputEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('send_status', models.CharField(default='pending', max_length=20)),
                ('input_id', models.CharField(max_length=40)),
                ('input_label', models.TextField()),
                ('value', models.TextField()),
                ('alarm', models.BooleanField()),
                ('country', models.IntegerField()),
                ('region', models.IntegerField()),
                ('uik', models.IntegerField()),
                ('complaint_status', models.CharField(choices=[('none', 'не подавалась'), ('refuse_to_accept', 'отказ принять жалобу'), ('refuse_to_resolve', 'отказ рассмотрения жалобы'), ('waiting_reply', 'ожидание решения комиссии'), ('got_unfair_reply', 'получено неудовлетворительное решение'), ('got_fair_reply', 'получено удовлетворительное решение')], max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InputEventImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('uik_complaint', 'Подаваемые в УИК жалобы'), ('uik_reply', 'Ответы, решения от УИК'), ('tik_complaint', 'Подаваемые в ТИК жалобы'), ('tik_reply', 'Ответы, решения от ТИК')], max_length=20)),
                ('file', models.TextField()),
                ('send_status', models.CharField(max_length=20)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='paradox.InputEvent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fromtime', models.DateTimeField()),
                ('totime', models.DateTimeField()),
                ('country', models.IntegerField()),
                ('region', models.IntegerField()),
                ('phones', models.TextField()),
                ('external_channels', models.TextField()),
                ('elect_flags', models.TextField()),
                ('coordinator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='paradox.Coordinator')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
