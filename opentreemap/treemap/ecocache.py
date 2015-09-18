# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.core.cache import cache

# Cache the results of tree ecobenefit summaries.
#
# For each instance, maintain in the cache a dictionary of tree searches
# and their resulting ecobenefit summaries. For example, the cache key
# phillytreemap would contain results for all searches of PhillyTreeMap:
#
#    {
#        '':        <ecobenefit summary for empty search>
#        <search1>: <ecobenefit summary for search 1>
#        <search2>: <ecobenefit summary for search 2>
#        ...
#    }


def cache_benefits(instance, filter, benefits):
    key = _get_key(instance)
    all_results = cache.get(key, {})
    all_results[filter.cache_key] = benefits
    cache.set(key, all_results)


def get_cached_benefits(instance, filter):
    key = _get_key(instance)
    all_results = cache.get(key, {})
    benefits = all_results.get(filter.cache_key, None)
    return benefits


def clear_benefit_cache(instance):
    key = _get_key(instance)
    cache.delete(key)


def _get_key(instance):
    return instance.url_name
