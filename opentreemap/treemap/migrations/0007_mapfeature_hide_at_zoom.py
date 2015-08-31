# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0006_stop_tracking_polygonal_mapfeature_ptr'),
    ]

    operations = [
        migrations.AddField(
            model_name='mapfeature',
            name='hide_at_zoom',
            field=models.IntegerField(null=True),
        ),
    ]
