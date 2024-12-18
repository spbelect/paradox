# Generated by Django 2.2.3 on 2019-08-24 16:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0007_auto_20190815_0635'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='vote_date',
            field=models.DateField(default=datetime.date(2019, 9, 8)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inputevent',
            name='tik_complaint_status',
            field=models.CharField(choices=[('none', 'не подавалась'), ('request_pending', 'запрос отправляется'), ('request_sent', 'запрос отправлен'), ('denied', 'отклонено'), ('email_sent', 'email отправлен')], default='none', max_length=30),
        ),
    ]