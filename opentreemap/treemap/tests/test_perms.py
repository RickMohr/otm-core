# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from treemap.tests.base import OTMTestCase

from treemap.models import Role, Plot, Tree
from treemap.lib import perms
from treemap.tests import make_instance, make_officer_user, make_admin_user


class PermTestCase(OTMTestCase):
    def test_none_perm(self):
        self.assertEqual(False,
                         perms._allows_perm(Role(),
                                            'NonExistentModel',
                                            any, 'allows_reads'))


class UserCanDeleteTestCase(OTMTestCase):
    def setUp(self):
        instance = make_instance()

        self.creator_user = make_officer_user(instance)
        self.admin_user = make_admin_user(instance)
        self.other_user = make_officer_user(instance, username='other')

        self.plot = Plot(geom=instance.center, instance=instance)
        self.plot.save_with_user(self.creator_user)

        self.tree = Tree(plot=self.plot, instance=instance)
        self.tree.save_with_user(self.creator_user)

    def assert_can_delete(self, user, deletable, should_be_able_to_delete):
        can = deletable.user_can_delete(user)
        self.assertEqual(can, should_be_able_to_delete)

    def test_user_can_delete(self):
        self.assert_can_delete(self.creator_user, self.plot, True)
        self.assert_can_delete(self.admin_user, self.plot, True)
        self.assert_can_delete(self.other_user, self.plot, False)
        self.assert_can_delete(self.creator_user, self.tree, True)
        self.assert_can_delete(self.admin_user, self.tree, True)
        self.assert_can_delete(self.other_user, self.tree, False)

