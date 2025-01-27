# Generated by Django 2.2.3 on 2019-08-15 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paradox', '0006_auto_20190730_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='inputevent',
            name='tik_complaint_text',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='inputevent',
            name='tik_complaint_status',
            field=models.CharField(choices=[('none', 'не подавалась'), ('request_pending', 'запрос отправляется'), ('request_sent', 'запрос отправлен'), ('email_sent', 'email отправлен')], default='none', max_length=30),
        ),
        migrations.AlterField(
            model_name='inputevent',
            name='uik_complaint_status',
            field=models.CharField(choices=[('none', 'не подавалась'), ('refuse_to_accept', 'отказ принять жалобу'), ('refuse_to_resolve', 'отказ рассмотрения жалобы'), ('refuse_to_copy_reply', 'отказ выдать копию решения'), ('waiting_reply', 'ожидание решения комиссии'), ('got_unfair_reply', 'получено неудовлетворительное решение'), ('got_fair_reply', 'получено удовлетворительное решение')], default='none', max_length=30),
        ),
    ]
