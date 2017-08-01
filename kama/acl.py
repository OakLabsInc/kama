# -*- coding: utf-8 -*-

DEFAULT_ACLS = {
    'readonly': [
        'entity.read_attribute',
        'entity.read_link',
        'entity.read_permission',
    ],
    'readwrite': [
        'entity.read_attribute',
        'entity.add_attribute',
        'entity.delete_attribute',
        'entity.read_link',
        'entity.add_link',
        'entity.delete_link',
        'entity.read_permission',
        'entity.set_name',
    ],
    'all': [
        'entity.delete',
        'entity.read_attribute',
        'entity.add_attribute',
        'entity.delete_attribute',
        'entity.read_link',
        'entity.add_link',
        'entity.delete_link',
        'entity.read_permission',
        'entity.add_permission',
        'entity.delete_permission',
        'entity.set_name',
    ],
}
