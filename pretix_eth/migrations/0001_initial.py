# Generated by Django 2.2.2 on 2019-07-12 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pretixbase', '0122_orderposition_web_secret'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('txn_hash', models.CharField(max_length=66, unique=True)),
                ('order_payment', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pretixbase.OrderPayment')),  # noqa: E501
            ],
        ),
    ]
