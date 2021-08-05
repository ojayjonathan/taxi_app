# Generated by Django 3.2.5 on 2021-07-31 10:10

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='time',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2021, 7, 31, 10, 10, 38, 677293, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customerbooking',
            name='status',
            field=models.CharField(choices=[('C', 'canceled'), ('A', 'active'), ('F', 'fulfiled')], default='A', max_length=1),
        ),
        migrations.AlterField(
            model_name='route',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='travel_origin', to='api.city'),
        ),
        migrations.CreateModel(
            name='Fcm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fcm_token', models.CharField(max_length=100)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]