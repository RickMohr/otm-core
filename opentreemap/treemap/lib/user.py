# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import urllib

from django.db.models import Q

from treemap.audit import Audit, Authorizable, get_auditable_class
from treemap.models import Instance, MapFeature, InstanceUser, User
from treemap.util import get_filterable_audit_models
from treemap.lib.object_caches import udf_defs
from treemap.udf import UDFModel


def _instance_ids_edited_by(user):
    return Audit.objects.filter(user=user)\
                        .values_list('instance_id', flat=True)\
                        .exclude(instance_id=None)\
                        .distinct()


def get_audits(logged_in_user, instance, query_vars, user, models,
               model_id, page=0, page_size=20, exclude_pending=True,
               should_count=False):
    start_pos = page * page_size
    end_pos = start_pos + page_size

    if instance:
        if instance.is_accessible_by(logged_in_user):
            instances = Instance.objects.filter(pk=instance.pk)
        else:
            instances = Instance.objects.none()
    # If we didn't specify an instance we only want to
    # show audits where the user has permission
    else:
        instances = Instance.objects\
                            .filter(pk__in=_instance_ids_edited_by(user))\
                            .filter(user_accessible_instance_filter(
                                logged_in_user))\
                            .distinct()

    if not instances.exists():
        # Force no results
        return {'audits': Audit.objects.none(),
                'total_count': 0,
                'next_page': None,
                'prev_page': None}

    map_feature_models = set(MapFeature.subclass_dict().keys())
    model_filter = Q()
    # We only want to show the TreePhoto's image, not other fields
    # and we want to do it automatically if 'Tree' was specified as
    # a model.  The same goes for MapFeature(s) <-> MapFeaturePhoto
    # There is no need to check permissions, because photos are always visible
    if 'Tree' in models:
        model_filter = model_filter | Q(model='TreePhoto', field='image')
    if map_feature_models.intersection(models):
        model_filter = model_filter | Q(model='MapFeaturePhoto', field='image')

    for inst in instances:
        eligible_models = ({'Tree', 'TreePhoto', 'MapFeaturePhoto'} |
                           set(inst.map_feature_types)) & set(models)

        if logged_in_user == user:
            eligible_udfs = {'udf:%s' % udf.id for udf in udf_defs(inst)
                             if udf.model_type in eligible_models
                             and udf.iscollection}

            # The logged-in user can see all their own edits
            model_filter = model_filter | Q(
                instance=inst, model__in=(eligible_models | eligible_udfs))

        else:
            # Filter other users' edits by their visibility to the
            # logged-in user
            for model in eligible_models:
                ModelClass = get_auditable_class(model)
                fake_model = ModelClass(instance=inst)
                if issubclass(ModelClass, Authorizable):
                    visible_fields = fake_model.visible_fields(logged_in_user)
                    model_filter = model_filter |\
                        Q(model=model, field__in=visible_fields, instance=inst)
                else:
                    model_filter = model_filter | Q(model=model, instance=inst)

                if issubclass(ModelClass, UDFModel):
                    model_collection_udfs_audit_names = (
                        fake_model.visible_collection_udfs_audit_names(
                            logged_in_user))

                    model_filter = model_filter | (
                        Q(model__in=model_collection_udfs_audit_names))

    udf_bookkeeping_fields = Q(
        model__startswith='udf:',
        field__in=('id', 'model_id', 'field_definition'))

    audits = (Audit.objects
              .filter(model_filter)
              .filter(instance__in=instances)
              .select_related('instance')
              .exclude(udf_bookkeeping_fields)
              .exclude(user=User.system_user())
              .order_by('-created'))

    if user:
        audits = audits.filter(user=user)
    if model_id:
        audits = audits.filter(model_id=model_id)
    if exclude_pending:
        audits = audits.exclude(requires_auth=True, ref__isnull=True)

    total_count = audits.count() if should_count else 0
    audits = audits[start_pos:end_pos]

    query_vars = {k: v for (k, v) in query_vars.iteritems() if k != 'page'}
    next_page = None
    prev_page = None
    # We are using len(audits) instead of audits.count() because we
    # have already realized the queryset at this point
    if len(audits) == page_size:
        query_vars['page'] = page + 1
        next_page = "?" + urllib.urlencode(query_vars)
    if page > 0:
        query_vars['page'] = page - 1
        prev_page = "?" + urllib.urlencode(query_vars)

    return {'audits': audits,
            'total_count': total_count,
            'next_page': next_page,
            'prev_page': prev_page}


def get_audits_params(request):
    PAGE_MAX = 100
    PAGE_DEFAULT = 20

    r = request.REQUEST

    page_size = min(int(r.get('page_size', PAGE_DEFAULT)), PAGE_MAX)
    page = int(r.get('page', 0))

    models = []

    allowed_models = get_filterable_audit_models()
    models_param = r.get('models', None)

    if models_param:
        for model in models_param.split(','):
            if model.lower() in allowed_models:
                models.append(allowed_models[model.lower()])
            else:
                raise Exception("Invalid model: %s" % model)
    else:
        models = allowed_models.values()

    model_id = r.get('model_id', None)

    if model_id is not None and len(models) != 1:
        raise Exception("You must specific one and only model "
                        "when looking up by id")

    exclude_pending = r.get('exclude_pending', "false") == "true"

    return (page, page_size, models, model_id, exclude_pending)


def user_accessible_instance_filter(logged_in_user):
    public = Q(is_public=True)
    if logged_in_user is not None and not logged_in_user.is_anonymous():
        private_with_access = Q(instanceuser__user=logged_in_user)

        instance_filter = public | private_with_access
    else:
        instance_filter = public
    return instance_filter


def get_user_instances(logged_in_user, user, current_instance=None):

    # Which instances can the logged-in user see?
    instance_filter = (user_accessible_instance_filter(logged_in_user))

    user_instance_ids = (InstanceUser.objects
                         .filter(user_id=user.pk)
                         .values_list('instance_id', flat=True))

    instance_filter = Q(instance_filter, Q(pk__in=user_instance_ids))

    # The logged-in user should see the current instance in their own list
    if current_instance and logged_in_user == user:
        instance_filter = instance_filter | Q(pk=current_instance.id)

    return (Instance.objects
            .filter(instance_filter)
            .distinct()
            .order_by('name'))
