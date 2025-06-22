# alerts/migrations/0002_enhanced_models.py
# Generated migration for enhanced models

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='performancetestresult',
            name='client_server_testing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='performancetestresult',
            name='real_measurements',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='performancetestresult',
            name='error_message',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='performancetestresult',
            name='technology',
            field=models.CharField(choices=[('websocket', 'WebSocket'), ('longpolling', 'Long Polling'), ('push', 'Push Notifications'), ('firebase', 'Firebase Push')], max_length=20),
        ),
        migrations.AlterField(
            model_name='performancetestresult',
            name='status',
            field=models.CharField(default='pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='performancetestresult',
            name='started_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='alertdeliverylog',
            name='client_server_test',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='alertdeliverylog',
            name='test_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='alertdeliverylog',
            name='source_app',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='alertdeliverylog',
            name='technology',
            field=models.CharField(choices=[('websocket', 'WebSocket'), ('longpolling', 'Long Polling'), ('push', 'Push Notifications'), ('firebase', 'Firebase Push')], max_length=20),
        ),
        migrations.AlterField(
            model_name='alertdeliverylog',
            name='delivery_status',
            field=models.CharField(choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('failed', 'Failed'), ('timeout', 'Timeout'), ('confirmed', 'Confirmed')], max_length=20),
        ),
        migrations.AddField(
            model_name='technologymetrics',
            name='median_latency_ms',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='technologymetrics',
            name='client_server_measurements',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='technologymetrics',
            name='last_test_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='technologymetrics',
            name='source_app',
            field=models.CharField(default='CLIENT', max_length=50),
        ),
        migrations.AlterField(
            model_name='technologymetrics',
            name='technology',
            field=models.CharField(choices=[('websocket', 'WebSocket'), ('longpolling', 'Long Polling'), ('push', 'Push Notifications'), ('firebase', 'Firebase Push')], max_length=20, unique=True),
        ),
        migrations.CreateModel(
            name='TestSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('session_name', models.CharField(blank=True, max_length=200)),
                ('technologies_tested', models.JSONField(default=list)),
                ('configuration', models.JSONField(default=dict)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='running', max_length=50)),
                ('total_tests', models.IntegerField(default=0)),
                ('successful_tests', models.IntegerField(default=0)),
                ('failed_tests', models.IntegerField(default=0)),
                ('client_server_testing', models.BooleanField(default=True)),
                ('resource_monitoring_enabled', models.BooleanField(default=False)),
                ('real_measurements', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Test Session',
                'verbose_name_plural': 'Test Sessions',
                'ordering': ['-started_at'],
            },
        ),
    ]
