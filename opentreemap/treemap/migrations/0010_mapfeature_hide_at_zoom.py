# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0009_restructure_replaceable_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapfeature',
            name='hide_at_zoom',
            field=models.IntegerField(null=True),
        ),
    ]
