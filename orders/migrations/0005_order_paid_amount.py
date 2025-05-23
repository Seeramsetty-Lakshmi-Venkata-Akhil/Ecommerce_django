# Generated by Django 5.2 on 2025-05-01 20:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Total amount paid towards this order', max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Paid Amount'),
        ),
    ]
