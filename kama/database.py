# -*- coding: utf-8 -*-
import MySQLdb
import MySQLdb.cursors
import threading
import functools
import uuid
import time
import sys
import os

import kama.acl
import kama.env
import kama.log


CACHE_TTL = 60.0


log = kama.log.get_logger('kama.database')
tlocal = threading.local()


class KamaException(Exception):
    pass


class EntityNotFoundException(KamaException):
    pass


class AttributeNotFoundException(KamaException):
    pass


class LinkNotFoundException(KamaException):
    pass


class PermissionNotFoundException(KamaException):
    pass


class PermissionDeniedException(KamaException):
    pass


def generate_uuid():
    # This is not RFC4122 UUID strictly, it's a re-ordered version of
    # UUID putting the node ID first. This makes it gentler on MySQL
    # when used as a primary key as newly generated keys will usually
    # come after older ones, so writes are more likely to be appends.
    #
    # Further, we ensure that it's encoded as an upper-case hex
    # string, because MySQL's HEX() function uses that and it makes
    # equality comparisons easier this way.
    version = 15    # definitely out of spec.
    u = uuid.uuid1()
    u = (version << 122) | (u.node << 74) | (u.time << 14) | u.clock_seq
    return '%032X' % u


class LoggingCursor(MySQLdb.cursors.Cursor):
    def execute(self, query, args=None):
        log.debug('execute: %r %% %r', query, args)
        return MySQLdb.cursors.Cursor.execute(self, query, args)


class DatabaseContext(object):
    def __init__(self):
        self.database = None

    def __enter__(self):
        if self.database is None:
            params = {
                'host': kama.env.get(['MYSQL_SERVICE_HOST', 'MYSQL_PORT_3306_TCP_ADDR'], '127.0.0.1'),
                'port': int(kama.env.get(['MYSQL_SERVICE_PORT', 'MYSQL_PORT_3306_TCP_PORT'], 3306)),
                'user': kama.env.get(['MYSQL_SERVICE_USER'], 'kama'),
                'db': kama.env.get(['MYSQL_SERVICE_DATABASE'], 'kama'),
                'connect_timeout': int(kama.env.get(['MYSQL_CONNECT_TIMEOUT'], 5)),
            }
            log.debug('Connecting to database with params: %r', params)

            params['passwd'] = kama.env.get(['MYSQL_SERVICE_PASSWORD'])
            if params['passwd'] is None:
                del params['passwd']

            self.database = MySQLdb.connect(**params)

        cursor = self.database.cursor(cursorclass=LoggingCursor)
        #cursor.execute('SET NAMES utf8mb4')
        #cursor.execute('SET CHARACTER SET utf8mb4')
        #cursor.execute('SET character_set_connection=utf8mb4')
        return cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.database.__exit__(exc_type, exc_value, exc_traceback)
        if exc_type is not None:
            try:
                log.debug('Closing database connection after exception was handled: %s', exc_type)
                self.database.close()
                self.database = None
            except: pass
        else:
            log.debug('COMMIT')
            self.database.commit()


def get_database_context():
    if not hasattr(tlocal, 'database_context'):
        tlocal.database_context = DatabaseContext()
    return tlocal.database_context


def schema_init():
    with get_database_context() as cursor:
        cursor.execute('''
CREATE TABLE `entities` (
    `entity_uuid` BINARY(16) NOT NULL PRIMARY KEY,
    `kind` TEXT NOT NULL,
    `name` TEXT NOT NULL
)''')

        cursor.execute('''
CREATE TABLE `attributes` (
    `attribute_uuid` BINARY(16) NOT NULL PRIMARY KEY,
    `entity_uuid` BINARY(16) NOT NULL,
    `key` TEXT NOT NULL,
    `value` BLOB NOT NULL
)''')

        cursor.execute('''
CREATE TABLE `links` (
    `link_uuid` BINARY(16) NOT NULL PRIMARY KEY,
    `from_uuid` BINARY(16) NOT NULL,
    `to_uuid` BINARY(16) NOT NULL
)''')

        cursor.execute('''
CREATE TABLE `permissions` (
    `permission_uuid` BINARY(16) NOT NULL PRIMARY KEY,
    `role_uuid` BINARY(16) NOT NULL,
    `entity_uuid` BINARY(16) NOT NULL,
    `name` TEXT NOT NULL
)''')

    with get_database_context() as cursor:
        cursor.execute('CREATE INDEX `idx_entities_kind` ON `entities` (`kind`(3))')
        cursor.execute('CREATE INDEX `idx_entities_name` ON `entities` (`name`(3))')
        cursor.execute('CREATE INDEX `idx_attributes_key` on `attributes` (`key`(3))')
        cursor.execute('CREATE INDEX `idx_links_to_uuid` ON `links` (`to_uuid`)')
        cursor.execute('CREATE INDEX `idx_links_from_uuid` ON `links` (`from_uuid`)')

    with get_database_context() as cursor:
        # We have to manually create the first role and user because
        # new Entities require an owner role to be created.
        role_uuid = generate_uuid()
        user_uuid = generate_uuid()
        link_uuid = generate_uuid()
        cursor.execute('INSERT INTO `entities` (entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (role_uuid, 'role', 'root'))
        cursor.execute('INSERT INTO `entities` (entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (user_uuid, 'user', 'root'))
        cursor.execute('INSERT INTO `links` (link_uuid, from_uuid, to_uuid) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s))', (link_uuid, role_uuid, user_uuid))

    role = Entity(role_uuid)
    user = Entity(user_uuid)
    link = Link(link_uuid)

    for permission in kama.acl.DEFAULT_ACLS['all']:
        Permission._create(role, role, permission)
    for permission in kama.acl.DEFAULT_ACLS['all']:
        Permission._create(role, user, permission)
    
    return Entity(role_uuid), Entity(user_uuid)


class RequestContext(object):
    def __init__(self, user):
        self.user = user


class InternalContext(object):
    '''
    Instances of InternalContext bypass all permissions checks. These are used
    mostly for reading the permissions off an entity in order to determine if
    you should have permission to read it at all.
    '''
    pass


def require_permission(name):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            context = kwargs.get('context', None)
            if context is None:
                raise PermissionDeniedException('No context, no permission.')
            
            if isinstance(context, InternalContext):
                # Short circuit permissions test for calls that are used to test permissions
                return fn(self, *args, **kwargs)
            else:
                if context.user.has_permission(self, name):
                    return fn(self, *args, **kwargs)
                else:
                    raise PermissionDeniedException('%s does not have permission to %s %s' % (context.user, name, self))
        return wrapper
    return decorator


class Entity(object):
    def __init__(self, uuid, kind=None, name=None):
        self.uuid = uuid

        # If we don't already know the kind and name, query it.
        if kind is None or name is None:
            self.get()
        else:
            self.kind = kind
            self.name = name

    def __str__(self):
        return '%s/%s' % (self.kind, self.name)

    def __repr__(self):
        return '%s(%r, %r, %r)' % (self.__class__.__name__, self.uuid, self.kind, self.name)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def create(cls, kind, name, owner_role):
        with get_database_context() as cursor:
            entity_uuid = generate_uuid()
            cursor.execute('INSERT INTO entities(entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (entity_uuid, kind, name))
            self = cls(entity_uuid, kind, name)
            for permission in kama.acl.DEFAULT_ACLS['all']:
                Permission._create(owner_role, self, permission)
            return self

    @classmethod
    def get_by_name(self, kind, name):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities WHERE name=%s AND kind=%s', (name, kind))
            row = cursor.fetchone()
            if not row:
                return None
            else:
                return Entity(*row)

    @classmethod
    def get_by_kind(self, kind):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities WHERE kind=%s', (kind,))
            return [Entity(*x) for x in cursor]

    @classmethod
    def get_all(cls):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities')
            return [cls(*x) for x in cursor]

    def get(self):
        with get_database_context() as cursor:
            cursor.execute('SELECT kind, name FROM entities WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise EntityNotFoundException(self.uuid)
            self.kind, self.name = row

    @require_permission('entity.delete')
    def delete(self, context=None):
        with get_database_context() as cursor:
            cursor.execute('DELETE FROM entities WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            cursor.execute('DELETE FROM attributes WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            cursor.execute('DELETE FROM links WHERE to_uuid=UNHEX(%s) OR from_uuid=UNHEX(%s)', (self.uuid, self.uuid))
            cursor.execute('DELETE FROM permissions WHERE entity_uuid=UNHEX(%s) OR role_uuid=UNHEX(%s)', (self.uuid, self.uuid))

    @require_permission('entity.set_name')
    def set_name(self, name, context=None):
        with get_database_context() as cursor:
            cursor.execute('UPDATE entities SET name=%s WHERE entity_uuid=UNHEX(%s)', (name, self.uuid))
            self.name = name

    @require_permission('entity.add_attribute')
    def add_attribute(self, key, value, context=None):
        return Attribute._create(self.uuid, key, value)

    @require_permission('entity.delete_attribute')
    def delete_attributes(self, key, context=None):
        with get_database_context() as cursor:
            cursor.execute('DELETE FROM attributes WHERE entity_uuid=UNHEX(%s) AND `key`=%s', (self.uuid, key))
            if cursor.rowcount == 0:
                raise AttributeNotFoundException('No attributes with key=%s on %s' % (key, self))

    @require_permission('entity.read_attribute')
    def attributes(self, key=None, context=None):
        with get_database_context() as cursor:
            if key is not None:
                cursor.execute('SELECT HEX(attribute_uuid), `key`, `value` FROM attributes WHERE entity_uuid=UNHEX(%s) AND `key`=%s', (self.uuid, key))
            else:
                cursor.execute('SELECT HEX(attribute_uuid), `key`, `value` FROM attributes WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            return [Attribute(*x) for x in cursor]

    @require_permission('entity.add_link')
    def add_link(self, to_entity, context=None):
        return Link._create(self, to_entity)

    @require_permission('entity.delete_link')
    def delete_link(self, to_entity, context=None):
        with get_database_context() as cursor:
            cursor.execute('DELETE FROM links WHERE from_uuid=UNHEX(%s) AND to_uuid=UNHEX(%s)', (self.uuid, to_entity.uuid))
            if cursor.rowcount == 0:
                raise LinkNotFoundException('No link from %s to %s' % (self, to_entity))

    @require_permission('entity.read_link')
    def links_from(self, context=None):
        links = []
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(links.link_uuid), HEX(links.to_uuid), entities.kind, entities.name FROM links, entities WHERE from_uuid=UNHEX(%s) AND entities.entity_uuid=links.to_uuid', (self.uuid,))
            for link_uuid, to_uuid, to_entity_kind, to_entity_name in cursor:
                to_entity = Entity(to_uuid, to_entity_kind, to_entity_name)
                link = Link(link_uuid, self, to_entity)
                links.append(link)
        return links

    @require_permission('entity.read_link')
    def links_to(self, context=None):
        links = []
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(link_uuid), HEX(from_uuid), entities.kind, entities.name FROM links, entities WHERE to_uuid=UNHEX(%s) AND entities.entity_uuid=links.from_uuid', (self.uuid,))
            for link_uuid, from_uuid, from_entity_kind, from_entity_name in cursor:
                from_entity = Entity(from_uuid, from_entity_kind, from_entity_name)
                link = Link(link_uuid, from_entity, self)
                links.append(link)
        return links

    @require_permission('entity.read_link')
    def links(self, context=None):
        return self.links_from(context=context) + self.links_to(context=context)

    @require_permission('entity.add_permission')
    def add_permission(self, role, name, context=None):
        return Permission._create(role, self, name)

    @require_permission('entity.delete_permission')
    def delete_permission(self, role, name, context=None):
        with get_database_context() as cursor:
            cursor.execute('DELETE FROM permissions WHERE entity_uuid=UNHEX(%s) AND role_uuid=UNHEX(%s) AND name=%s', (self.uuid, role.uuid, name))

    @require_permission('entity.read_permission')
    def permissions(self, context=None):
        permissions = []
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(permission_uuid), HEX(role_uuid), entities.kind, entities.name, permissions.name FROM permissions, entities WHERE permissions.entity_uuid=UNHEX(%s) AND entities.entity_uuid=permissions.role_uuid', (self.uuid,))
            for permission_uuid, role_uuid, role_kind, role_name, name in cursor:
                role = Entity(role_uuid, role_kind, role_name)
                permission = Permission(permission_uuid, role, self, name)
                permissions.append(permission)
        return permissions

    def has_permission(self, entity, name):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(permissions.permission_uuid) FROM permissions, entities AS role, entities AS users, links WHERE permissions.entity_uuid=UNHEX(%s) AND permissions.name=%s AND role.entity_uuid=permissions.role_uuid AND links.from_uuid=role.entity_uuid AND links.to_uuid=users.entity_uuid AND users.entity_uuid=UNHEX(%s)', (entity.uuid, name, self.uuid))
            if cursor.rowcount > 0:
                return True
            else:
                return False

class Attribute(object):
    def __init__(self, uuid, entity_uuid=None, key=None, value=None):
        self.uuid = uuid

        if entity_uuid is None or key is None or value is None:
            self.get()
        else:
            self.entity_uuid = entity_uuid
            self.key = key
            self.value = value

    def __str__(self):
        return '%s %s=%s' % (self.entity(), self.key, self.value)

    def __repr__(self):
        return 'Attribute(%r, %r, %r, %r)' % (self.uuid, self.entity_uuid, self.key, self.value)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def _create(cls, entity_uuid, key, value):
        with get_database_context() as cursor:
            attribute_uuid = generate_uuid()
            cursor.execute('INSERT INTO attributes(attribute_uuid, entity_uuid, `key`, `value`) VALUES(UNHEX(%s), UNHEX(%s), %s, %s)',
                    (attribute_uuid, entity_uuid, key, value))
            return cls(attribute_uuid, entity_uuid, key, value)

    def get(self):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), `key`, `value` FROM attributes WHERE attribute_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise AttributeNotFoundException(self.uuid)
            self.entity_uuid, self.key, self.value = row

    def entity(self):
        return Entity(self.entity_uuid)


class Link(object):
    def __init__(self, uuid, from_entity=None, to_entity=None):
        self.uuid = uuid

        if from_entity is None or to_entity is None:
            self.get()
        else:
            self.from_entity = from_entity
            self.to_entity = to_entity

    def __str__(self):
        return 'Link %s -> %s' % (self.from_entity, self.to_entity)

    def __repr__(self):
        return 'Link(%r, %r, %r)' % (self.uuid, self.from_entity, self.to_entity)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def _create(cls, from_entity, to_entity):
        with get_database_context() as cursor:
            link_uuid = generate_uuid()
            cursor.execute('INSERT INTO links (link_uuid, from_uuid, to_uuid) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s))',
                    (link_uuid, from_entity.uuid, to_entity.uuid))
            return cls(link_uuid, from_entity, to_entity)

    def get(self):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(from_uuid), HEX(to_uuid) FROM links WHERE link_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise LinkNotFoundException(self.uuid)
            from_uuid, to_uuid = row
            self.from_entity = Entity(from_uuid)
            self.to_uuid = Entity(to_uuid)


class Permission(object):
    def __init__(self, uuid, role=None, entity=None, name=None):
        self.uuid = uuid

        if role is None or entity is None or name is None:
            self.get()
        else:
            self.role = role
            self.entity = entity
            self.name = name

    def __str__(self):
        return 'Permission %s has %s on %s' % (self.role, self.name, self.entity)

    def __repr__(self):
        return 'Permission(%r, %r, %r, %r)' % (self.uuid, self.role, self.entity, self.name)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def _create(cls, role, entity, name):
        with get_database_context() as cursor:
            permission_uuid = generate_uuid()
            cursor.execute('INSERT INTO permissions (permission_uuid, role_uuid, entity_uuid, name) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s), %s)',
                    (permission_uuid, role.uuid, entity.uuid, name))
            return cls(permission_uuid, role, entity, name)
    
    def get(self):
        with get_database_context() as cursor:
            cursor.execute('SELECT HEX(role_uuid), HEX(entity_uuid), name FROM permissions WHERE permission_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise PermissionNotFoundException(self.uuid)
            role_uuid, entity_uuid, self.name = row
            self.role = Entity(role_uuid)
            self.entity = Entity(entity_uuid)

    def users(self, context=None):
        return [x.from_entity for x in self.role.links_to(context=context)]
