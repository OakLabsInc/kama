import kama.database
import unittest


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.root_role, self.root_user = kama.database.schema_init()
        self.context = kama.database.RequestContext(self.root_user)

    def tearDown(self):
        with kama.database.DatabaseContext() as cursor:
            cursor.execute('DROP TABLE permissions')
            cursor.execute('DROP TABLE links')
            cursor.execute('DROP TABLE attributes')
            cursor.execute('DROP TABLE entities')

    def test_create_delete_entity(self):
        test1 = kama.database.Entity.create('device', 'test1', self.root_role)
        test1.delete(context=self.context)

    def test_attributes(self):
        test2 = kama.database.Entity.create('device', 'test2', self.root_role)
        a1 = test2.add_attribute('hello', 'there', context=self.context)
        self.assertEqual(test2.attributes(context=self.context), [a1])
        self.assertEqual(test2.attributes(key='hello', context=self.context), [a1])
        self.assertEqual(test2.attributes(key='there', context=self.context), [])
        test2.delete_attributes(key='hello', context=self.context)
        self.assertEqual(test2.attributes(context=self.context), [])
        test2.delete(context=self.context)

    def test_links(self):
        test3 = kama.database.Entity.create('device', 'test3', self.root_role)
        test4 = kama.database.Entity.create('device', 'test4', self.root_role)

        test3.add_link(test4, context=self.context)
        self.assertEqual([x.to_entity for x in test3.links_from(context=self.context)], [test4])
        self.assertEqual([x.to_entity for x in test3.links(context=self.context)], [test4])
        self.assertEqual([x.to_entity for x in test3.links_to(context=self.context)], [])

        self.assertEqual([x.from_entity for x in test4.links_to(context=self.context)], [test3])
        self.assertEqual([x.from_entity for x in test4.links(context=self.context)], [test3])
        self.assertEqual([x.from_entity for x in test4.links_from(context=self.context)], [])

        test3.delete_link(test4, context=self.context)
        self.assertEqual(test3.links(context=self.context), [])
        test3.delete(context=self.context)
        test4.delete(context=self.context)

    def test_permissions(self):
        role1 = kama.database.Entity.create('role', 'role1', self.root_role)
        user1 = kama.database.Entity.create('user', 'user1', self.root_role)
        role1.add_link(user1, context=self.context)
        user1_context = kama.database.RequestContext(user1)

        role2 = kama.database.Entity.create('role', 'role2', self.root_role)
        user2 = kama.database.Entity.create('user', 'user2', self.root_role)
        role2.add_link(user2, context=self.context)
        user2_context = kama.database.RequestContext(user2)

        test5 = kama.database.Entity.create('device', 'test5', role1)
        test5.add_attribute('totally', 'allowed', context=user1_context)

        caught_exception = False
        try:
            test5.add_attribute('not', 'allowed', context=user2_context)
        except kama.database.PermissionDeniedException:
            caught_exception = True
        self.assertTrue(caught_exception)

        caught_exception = False
        try:
            test5.attributes(context=user2_context)
        except kama.database.PermissionDeniedException:
            caught_exception = True
        self.assertTrue(caught_exception)

        read_permission = test5.add_permission(role2, 'entity.read_attribute', context=user1_context)
        self.assertIn(read_permission, test5.permissions(context=user1_context))

        caught_exception = False
        try:
            test5.attributes(context=user2_context)
        except kama.database.PermissionDeniedException as e:
            caught_exception = True
        self.assertFalse(caught_exception)

        caught_exception = False
        try:
            test5.add_permission(role2, 'entity.add_attribute', context=user2_context)
        except kama.database.PermissionDeniedException:
            caught_exception = True
        self.assertTrue(caught_exception)

        test5.add_permission(role2, 'entity.add_attribute', context=user1_context)
        attribute = test5.add_attribute('really', 'allowed', context=user2_context)
        self.assertIn(attribute, test5.attributes(key='really', context=user2_context))

        test5.add_permission(role2, 'entity.delete_permission', context=user1_context)
        test5.delete_permission(role1, 'entity.add_attribute', context=user2_context)

        caught_exception = False
        try:
            test5.add_attribute('access', 'revoked', context=user1_context)
        except kama.database.PermissionDeniedException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_context(self):
        test6 = kama.database.Entity.create('device', 'test6', self.root_role)

        caught_exception = False
        try:
            test6.add_attribute('no', 'context')
        except kama.database.PermissionDeniedException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_entity_operators(self):
        test7 = kama.database.Entity.create('device', 'test7', self.root_role)
        test8 = kama.database.Entity.create('device', 'test8', self.root_role)
        self.assertEqual(repr(test7), 'Entity(%r, %r, %r)' % (test7.uuid, 'device', 'test7'))
        self.assertNotEqual(test7, test8)
        self.assertNotEqual(cmp(test7, test8), 0)

    def test_not_found_exceptions(self):
        test9 = kama.database.Entity.create('device', 'test9', self.root_role)
        test10 = kama.database.Entity.create('device', 'test10', self.root_role)

        caught_exception = False
        try:
            test9.delete_attributes('nonexistent', context=self.context)
        except kama.database.AttributeNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

        caught_exception = False
        try:
            test9.delete_link(test10, context=self.context)
        except kama.database.LinkNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

        test9.delete(context=self.context)
        caught_exception = False
        try:
            test9.get()
        except kama.database.EntityNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_attribute_operators(self):
        test11 = kama.database.Entity.create('device', 'test11', self.root_role)
        attribute = test11.add_attribute('dummy', 'value', context=self.context)

        self.assertEqual(str(attribute), '%s %s=%s' % (attribute.entity(), attribute.key, attribute.value))
        self.assertEqual(repr(attribute), 'Attribute(%r, %r, %r, %r)' % (attribute.uuid, attribute.entity_uuid, attribute.key, attribute.value))
        self.assertNotEqual(attribute, test11)
        self.assertNotEqual(cmp(attribute, test11), 0)

        self.assertEqual(attribute.entity(), test11)

        test11.delete_attributes('dummy', context=self.context)
        
        caught_exception = False
        try:
            attribute.get()
        except kama.database.AttributeNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_link_operators(self):
        test12 = kama.database.Entity.create('device', 'test12', self.root_role)
        test13 = kama.database.Entity.create('device', 'test13', self.root_role)

        link1 = test12.add_link(test13, context=self.context)
        link2 = test13.add_link(test12, context=self.context)

        self.assertNotEqual(link1, link2)
        self.assertNotEqual(cmp(link1, link2), 0)
        self.assertFalse(link1 == link2)
        self.assertEqual(str(link1), 'Link %s -> %s' % (link1.from_entity, link1.to_entity))
        self.assertEqual(repr(link1), 'Link(%r, %r, %r)' % (link1.uuid, link1.from_entity, link1.to_entity))

        link1_copy = kama.database.Link(link1.uuid)
        self.assertEqual(link1, link1_copy)

        test12.delete_link(test13, context=self.context)
        caught_exception = False
        try:
            link1.get()
        except kama.database.LinkNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_permission_overators(self):
        test14 = kama.database.Entity.create('device', 'test14', self.root_role)
        test15 = kama.database.Entity.create('device', 'test15', self.root_role)

        p1 = test14.permissions(context=self.context)[0]
        p2 = test15.permissions(context=self.context)[0]

        self.assertNotEqual(p1, p2)
        self.assertNotEqual(cmp(p1, p2), 0)
        self.assertEqual(str(p1), 'Permission %s has %s on %s' % (p1.role, p1.name, p1.entity))
        self.assertEqual(repr(p1), 'Permission(%r, %r, %r, %r)' % (p1.uuid, p1.role, p1.entity, p1.name))

        self.assertEqual(kama.database.Permission(p1.uuid), p1)

        test15.delete_permission(p2.role, p2.name, context=self.context)
        caught_exception = False
        try:
            p2.get()
        except kama.database.PermissionNotFoundException:
            caught_exception = True
        self.assertTrue(caught_exception)

    def test_entity_query(self):
        test16 = kama.database.Entity.create('device', 'test16', self.root_role)

        self.assertEqual(kama.database.Entity.get_by_name('device', 'test16'), test16)
        self.assertEqual(kama.database.Entity.get_by_name('device', 'test17'), None)

        entities = kama.database.Entity.get_by_kind('device')
        self.assertEqual(entities, [test16])

    def test_entity_rename(self):
        test17 = kama.database.Entity.create('device', 'test17', self.root_role)
        test17.set_name('test18', context=self.context)
        self.assertEqual(test17.name, 'test18')
        test18 = kama.database.Entity(test17.uuid)
        self.assertEqual(test18.name, 'test18')
        test18 = kama.database.Entity.get_by_name('device', 'test18')
        self.assertEqual(test18.name, 'test18')
        test17 = kama.database.Entity.get_by_name('device', 'test17')
        self.assertEqual(test17, None)

    def test_entity_get_all(self):
        entities = kama.database.Entity.get_all()
        self.assertNotEqual(len(entities), 0)
