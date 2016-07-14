# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def create_map_feature_configs(apps, schema_editor):
    Instance = apps.get_model("treemap", "Instance")
    instances = Instance.objects.filter(
        config__contains='\"map_feature_types\":')
    for instance in instances:
        create_map_feature_config(instance)


def create_map_feature_config(instance):
    types = instance.config.map_feature_types
    terms = instance.config.pop('terms', {})
    map_feature_config = {type: terms.get(type, {}) for type in types}
    if 'Resource' in terms:
        instance.config.terms = {'Resource': terms['Resource']}
    instance.config.map_feature_config = map_feature_config
    del instance.config['map_feature_types']
    instance.save()


def remove_map_feature_configs(apps, schema_editor):
    Instance = apps.get_model("treemap", "Instance")
    instances = Instance.objects.filter(
        config__contains='\"map_feature_config\":')
    for instance in instances:
        remove_map_feature_config(instance)


def remove_map_feature_config(instance):
    map_feature_config = instance.config.map_feature_config
    terms = instance.config.pop('terms', {})
    terms.update(map_feature_config)
    instance.config.terms = terms
    instance.config.map_feature_types = map_feature_config.keys()
    del instance.config['map_feature_config']
    instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ('treemap', '0029_merge'),
    ]

    operations = [
        migrations.RunPython(create_map_feature_configs,
                             remove_map_feature_configs),
    ]
