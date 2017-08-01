# -*- coding: utf-8 -*-
import MySQLdb as dbapi
import functools
import uuid
import sys
import os

import kama.acl
import kama.log


log = kama.log.get_logger('kama.database')


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

def getenv(keys, default=None):
    for key in keys:
        if key in os.environ:
            return os.environ[key]
    return default

class DatabaseContext(object):
    def __init__(self):
        self.database = None

    def __enter__(self):
        params = {
            'host': getenv(['MYSQL_SERVICE_HOST', 'MYSQL_PORT_3306_TCP_ADDR']),
            'port': int(getenv(['MYSQL_SERVICE_PORT', 'MYSQL_PORT_3306_TCP_PORT'])),
            'user': getenv(['MYSQL_SERVICE_USER'], 'kama'),
            'db': getenv(['MYSQL_SERVICE_DATABASE'], 'kama'),
            'connect_timeout': int(getenv(['MYSQL_CONNECT_TIMEOUT'], 5)),
        }
        log.debug('Connecting to database with params: %r', params)

        params['passwd'] = getenv(['MYSQL_SERVICE_PASSWORD'])
        if params['passwd'] is None:
            del params['passwd']

        self.database = dbapi.connect(**params)

        with self.database as cursor:
            cursor.execute('SET NAMES utf8mb4')
            cursor.execute('SET CHARACTER SET utf8mb4')
            cursor.execute('SET character_set_connection=utf8mb4')
        return self.database.__enter__()

    def __exit__(self, *args):
        log.debug('Closing database connection')
        self.database.__exit__(*args)
        self.database.commit()
        self.database.close()


def schema_init():
    with DatabaseContext() as cursor:
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

    with DatabaseContext() as cursor:
        cursor.execute('CREATE INDEX `idx_entities_kind` ON `entities` (`kind`(3))')
        cursor.execute('CREATE INDEX `idx_entities_name` ON `entities` (`name`(3))')
        cursor.execute('CREATE INDEX `idx_attributes_key` on `attributes` (`key`(3))')
        cursor.execute('CREATE INDEX `idx_links_to_uuid` ON `links` (`to_uuid`)')
        cursor.execute('CREATE INDEX `idx_links_from_uuid` ON `links` (`from_uuid`)')

    with DatabaseContext() as cursor:
        # We have to manually create the first role and user because
        # new Entities require an owner role to be created.
        role_uuid = generate_uuid()
        user_uuid = generate_uuid()
        link_uuid = generate_uuid()
        cursor.execute('INSERT INTO `entities` (entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (role_uuid, 'role', 'root'))
        cursor.execute('INSERT INTO `entities` (entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (user_uuid, 'user', 'root'))
        cursor.execute('INSERT INTO `links` (link_uuid, from_uuid, to_uuid) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s))', (link_uuid, role_uuid, user_uuid))
        for permission in kama.acl.DEFAULT_ACLS['all']:
            Permission._create(role_uuid, role_uuid, permission)
        for permission in kama.acl.DEFAULT_ACLS['all']:
            Permission._create(role_uuid, user_uuid, permission)
    
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


def has_permission(user, entity, name):
    internal = InternalContext()
    for permission in entity.permissions(context=internal):
        if permission.name == name and user.uuid in permission.users(context=internal):
            log.debug('ALLOW %s %s %s', user, name, entity)
            return True
    log.debug('DENY  %s %s %s', user, name, entity)
    return False

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
                if has_permission(context.user, self, name):
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
        with DatabaseContext() as cursor:
            entity_uuid = generate_uuid()
            cursor.execute('INSERT INTO entities(entity_uuid, kind, name) VALUES(UNHEX(%s), %s, %s)', (entity_uuid, kind, name))
            self = cls(entity_uuid, kind, name)
            for permission in kama.acl.DEFAULT_ACLS['all']:
                Permission._create(owner_role.uuid, self.uuid, permission)
            return self

    @classmethod
    def get_by_name(self, kind, name):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities WHERE name=%s AND kind=%s', (name, kind))
            row = cursor.fetchone()
            if not row:
                return None
            else:
                return Entity(*row)

    @classmethod
    def get_by_kind(self, kind):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities WHERE kind=%s', (kind,))
            return [Entity(*x) for x in cursor]

    @classmethod
    def get_all(cls):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), kind, name FROM entities')
            return [cls(*x) for x in cursor]

    def get(self):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT kind, name FROM entities WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise EntityNotFoundException(self.uuid)
            self.kind, self.name = row

    @require_permission('entity.delete')
    def delete(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('DELETE FROM entities WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            cursor.execute('DELETE FROM attributes WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            cursor.execute('DELETE FROM links WHERE to_uuid=UNHEX(%s) OR from_uuid=UNHEX(%s)', (self.uuid, self.uuid))
            cursor.execute('DELETE FROM permissions WHERE entity_uuid=UNHEX(%s) OR role_uuid=UNHEX(%s)', (self.uuid, self.uuid))

    @require_permission('entity.set_name')
    def set_name(self, name, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('UPDATE entities SET name=%s WHERE entity_uuid=UNHEX(%s)', (name, self.uuid))
            self.name = name

    @require_permission('entity.add_attribute')
    def add_attribute(self, key, value, context=None):
        return Attribute._create(self.uuid, key, value)

    @require_permission('entity.delete_attribute')
    def delete_attributes(self, key, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('DELETE FROM attributes WHERE entity_uuid=UNHEX(%s) AND `key`=%s', (self.uuid, key))
            if cursor.rowcount == 0:
                raise AttributeNotFoundException('No attributes with key=%s on %s' % (key, self))

    @require_permission('entity.read_attribute')
    def attributes(self, key=None, context=None):
        with DatabaseContext() as cursor:
            if key is not None:
                cursor.execute('SELECT HEX(attribute_uuid), `key`, `value` FROM attributes WHERE entity_uuid=UNHEX(%s) AND `key`=%s', (self.uuid, key))
            else:
                cursor.execute('SELECT HEX(attribute_uuid), `key`, `value` FROM attributes WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            return [Attribute(*x) for x in cursor]

    @require_permission('entity.add_link')
    def add_link(self, to_entity, context=None):
        return Link._create(self.uuid, to_entity.uuid)

    @require_permission('entity.delete_link')
    def delete_link(self, to_entity, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('DELETE FROM links WHERE from_uuid=UNHEX(%s) AND to_uuid=UNHEX(%s)', (self.uuid, to_entity.uuid))
            if cursor.rowcount == 0:
                raise LinkNotFoundException('No link from %s to %s' % (self, to_entity))

    @require_permission('entity.read_link')
    def links_from(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(link_uuid), HEX(from_uuid), HEX(to_uuid) FROM links WHERE from_uuid=UNHEX(%s)', (self.uuid,))
            return [Link(*x) for x in cursor]

    @require_permission('entity.read_link')
    def links_to(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(link_uuid), HEX(from_uuid), HEX(to_uuid) FROM links WHERE to_uuid=UNHEX(%s)', (self.uuid,))
            return [Link(*x) for x in cursor]

    @require_permission('entity.read_link')
    def links(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(link_uuid), HEX(from_uuid), HEX(to_uuid) FROM links WHERE from_uuid=UNHEX(%s) OR to_uuid=UNHEX(%s)', (self.uuid, self.uuid))
            return [Link(*x) for x in cursor]

    @require_permission('entity.add_permission')
    def add_permission(self, role, name, context=None):
        return Permission._create(role.uuid, self.uuid, name)

    @require_permission('entity.delete_permission')
    def delete_permission(self, role, name, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('DELETE FROM permissions WHERE entity_uuid=UNHEX(%s) AND role_uuid=UNHEX(%s) AND name=%s', (self.uuid, role.uuid, name))

    @require_permission('entity.read_permission')
    def permissions(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(permission_uuid), HEX(role_uuid), HEX(entity_uuid), name FROM permissions WHERE entity_uuid=UNHEX(%s)', (self.uuid,))
            return [Permission(*x) for x in cursor]


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
        with DatabaseContext() as cursor:
            attribute_uuid = generate_uuid()
            cursor.execute('INSERT INTO attributes(attribute_uuid, entity_uuid, `key`, `value`) VALUES(UNHEX(%s), UNHEX(%s), %s, %s)',
                    (attribute_uuid, entity_uuid, key, value))
            return cls(attribute_uuid, entity_uuid, key, value)

    def get(self):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(entity_uuid), `key`, `value` FROM attributes WHERE attribute_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise AttributeNotFoundException(self.uuid)
            self.entity_uuid, self.key, self.value = row

    def entity(self):
        return Entity(self.entity_uuid)


class Link(object):
    def __init__(self, uuid, from_uuid=None, to_uuid=None):
        self.uuid = uuid

        if from_uuid is None or to_uuid is None:
            self.get()
        else:
            self.from_uuid = from_uuid
            self.to_uuid = to_uuid

    def __str__(self):
        return 'Link %s -> %s' % (self.from_entity(), self.to_entity())

    def __repr__(self):
        return 'Link(%r, %r, %r)' % (self.uuid, self.from_uuid, self.to_uuid)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def _create(cls, from_uuid, to_uuid):
        with DatabaseContext() as cursor:
            link_uuid = generate_uuid()
            cursor.execute('INSERT INTO links (link_uuid, from_uuid, to_uuid) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s))',
                    (link_uuid, from_uuid, to_uuid))
            return cls(link_uuid, from_uuid, to_uuid)

    def get(self):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(from_uuid), HEX(to_uuid) FROM links WHERE link_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise LinkNotFoundException(self.uuid)
            self.from_uuid, self.to_uuid = row

    def from_entity(self):
        return Entity(self.from_uuid)

    def to_entity(self):
        return Entity(self.to_uuid)


class Permission(object):
    def __init__(self, uuid, role_uuid=None, entity_uuid=None, name=None):
        self.uuid = uuid

        if role_uuid is None or entity_uuid is None or name is None:
            self.get()
        else:
            self.role_uuid = role_uuid
            self.entity_uuid = entity_uuid
            self.name = name

    def __str__(self):
        return 'Permission %s has %s on %s' % (self.role(), self.name, self.entity())

    def __repr__(self):
        return 'Permission(%r, %r, %r, %r)' % (self.uuid, self.role_uuid, self.entity_uuid, self.name)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return self.uuid != other.uuid

    def __cmp__(self, other):
        return int(self.uuid, 16) - int(other.uuid, 16)

    @classmethod
    def _create(cls, role_uuid, entity_uuid, name):
        with DatabaseContext() as cursor:
            permission_uuid = generate_uuid()
            cursor.execute('INSERT INTO permissions (permission_uuid, role_uuid, entity_uuid, name) VALUES(UNHEX(%s), UNHEX(%s), UNHEX(%s), %s)',
                    (permission_uuid, role_uuid, entity_uuid, name))
            return cls(permission_uuid, role_uuid, entity_uuid, name)
    
    def get(self):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(role_uuid), HEX(entity_uuid), name FROM permissions WHERE permission_uuid=UNHEX(%s)', (self.uuid,))
            row = cursor.fetchone()
            if row is None:
                raise PermissionNotFoundException(self.uuid)
            self.role_uuid, self.entity_uuid, self.name = row

    def entity(self):
        return Entity(self.entity_uuid)

    def role(self):
        return Entity(self.role_uuid)
    
    def users(self, context=None):
        with DatabaseContext() as cursor:
            cursor.execute('SELECT HEX(to_uuid) FROM links WHERE from_uuid=UNHEX(%s)', (self.role_uuid,))
            return [x[0] for x in cursor.fetchall()]
