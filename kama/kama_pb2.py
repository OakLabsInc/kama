# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: kama.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='kama.proto',
  package='kama',
  syntax='proto3',
  serialized_pb=_b('\n\nkama.proto\x12\x04kama\x1a\x1bgoogle/protobuf/empty.proto\"\xbc\x01\n\x06\x45ntity\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04kind\x18\x03 \x01(\t\x12#\n\nattributes\x18\x04 \x03(\x0b\x32\x0f.kama.Attribute\x12\x1e\n\nlinks_from\x18\x05 \x03(\x0b\x32\n.kama.Link\x12\x1c\n\x08links_to\x18\x06 \x03(\x0b\x32\n.kama.Link\x12%\n\x0bpermissions\x18\x07 \x03(\x0b\x32\x10.kama.Permission\"S\n\tAttribute\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c\x12\x1c\n\x06\x65ntity\x18\x02 \x01(\x0b\x32\x0c.kama.Entity\x12\x0b\n\x03key\x18\x03 \x01(\t\x12\r\n\x05value\x18\x04 \x01(\x0c\"X\n\x04Link\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c\x12!\n\x0b\x66rom_entity\x18\x02 \x01(\x0b\x32\x0c.kama.Entity\x12\x1f\n\tto_entity\x18\x03 \x01(\x0b\x32\x0c.kama.Entity\"b\n\nPermission\x12\x0c\n\x04uuid\x18\x01 \x01(\x0c\x12\x1a\n\x04role\x18\x02 \x01(\x0b\x32\x0c.kama.Entity\x12\x1c\n\x06\x65ntity\x18\x03 \x01(\x0b\x32\x0c.kama.Entity\x12\x0c\n\x04name\x18\x04 \x01(\t\"U\n\x13\x43reateEntityRequest\x12\x1c\n\x06\x65ntity\x18\x01 \x01(\x0b\x32\x0c.kama.Entity\x12 \n\nowner_role\x18\x02 \x01(\x0b\x32\x0c.kama.Entity2\xb7\x04\n\x0cKamaDatabase\x12,\n\x0cListEntities\x12\x0c.kama.Entity\x1a\x0c.kama.Entity0\x01\x12\'\n\tGetEntity\x12\x0c.kama.Entity\x1a\x0c.kama.Entity\x12\x37\n\x0c\x43reateEntity\x12\x19.kama.CreateEntityRequest\x1a\x0c.kama.Entity\x12\x34\n\x0c\x44\x65leteEntity\x12\x0c.kama.Entity\x1a\x16.google.protobuf.Empty\x12*\n\x0cUpdateEntity\x12\x0c.kama.Entity\x1a\x0c.kama.Entity\x12\x30\n\x0c\x41\x64\x64\x41ttribute\x12\x0f.kama.Attribute\x1a\x0f.kama.Attribute\x12;\n\x10\x44\x65leteAttributes\x12\x0f.kama.Attribute\x1a\x16.google.protobuf.Empty\x12!\n\x07\x41\x64\x64Link\x12\n.kama.Link\x1a\n.kama.Link\x12\x30\n\nDeleteLink\x12\n.kama.Link\x1a\x16.google.protobuf.Empty\x12\x33\n\rAddPermission\x12\x10.kama.Permission\x1a\x10.kama.Permission\x12<\n\x10\x44\x65letePermission\x12\x10.kama.Permission\x1a\x16.google.protobuf.Emptyb\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,])




_ENTITY = _descriptor.Descriptor(
  name='Entity',
  full_name='kama.Entity',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='kama.Entity.uuid', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='kama.Entity.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='kind', full_name='kama.Entity.kind', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='attributes', full_name='kama.Entity.attributes', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='links_from', full_name='kama.Entity.links_from', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='links_to', full_name='kama.Entity.links_to', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='permissions', full_name='kama.Entity.permissions', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=50,
  serialized_end=238,
)


_ATTRIBUTE = _descriptor.Descriptor(
  name='Attribute',
  full_name='kama.Attribute',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='kama.Attribute.uuid', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='entity', full_name='kama.Attribute.entity', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='key', full_name='kama.Attribute.key', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='kama.Attribute.value', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=240,
  serialized_end=323,
)


_LINK = _descriptor.Descriptor(
  name='Link',
  full_name='kama.Link',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='kama.Link.uuid', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_entity', full_name='kama.Link.from_entity', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='to_entity', full_name='kama.Link.to_entity', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=325,
  serialized_end=413,
)


_PERMISSION = _descriptor.Descriptor(
  name='Permission',
  full_name='kama.Permission',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='kama.Permission.uuid', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='role', full_name='kama.Permission.role', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='entity', full_name='kama.Permission.entity', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='kama.Permission.name', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=415,
  serialized_end=513,
)


_CREATEENTITYREQUEST = _descriptor.Descriptor(
  name='CreateEntityRequest',
  full_name='kama.CreateEntityRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='entity', full_name='kama.CreateEntityRequest.entity', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='owner_role', full_name='kama.CreateEntityRequest.owner_role', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=515,
  serialized_end=600,
)

_ENTITY.fields_by_name['attributes'].message_type = _ATTRIBUTE
_ENTITY.fields_by_name['links_from'].message_type = _LINK
_ENTITY.fields_by_name['links_to'].message_type = _LINK
_ENTITY.fields_by_name['permissions'].message_type = _PERMISSION
_ATTRIBUTE.fields_by_name['entity'].message_type = _ENTITY
_LINK.fields_by_name['from_entity'].message_type = _ENTITY
_LINK.fields_by_name['to_entity'].message_type = _ENTITY
_PERMISSION.fields_by_name['role'].message_type = _ENTITY
_PERMISSION.fields_by_name['entity'].message_type = _ENTITY
_CREATEENTITYREQUEST.fields_by_name['entity'].message_type = _ENTITY
_CREATEENTITYREQUEST.fields_by_name['owner_role'].message_type = _ENTITY
DESCRIPTOR.message_types_by_name['Entity'] = _ENTITY
DESCRIPTOR.message_types_by_name['Attribute'] = _ATTRIBUTE
DESCRIPTOR.message_types_by_name['Link'] = _LINK
DESCRIPTOR.message_types_by_name['Permission'] = _PERMISSION
DESCRIPTOR.message_types_by_name['CreateEntityRequest'] = _CREATEENTITYREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Entity = _reflection.GeneratedProtocolMessageType('Entity', (_message.Message,), dict(
  DESCRIPTOR = _ENTITY,
  __module__ = 'kama_pb2'
  # @@protoc_insertion_point(class_scope:kama.Entity)
  ))
_sym_db.RegisterMessage(Entity)

Attribute = _reflection.GeneratedProtocolMessageType('Attribute', (_message.Message,), dict(
  DESCRIPTOR = _ATTRIBUTE,
  __module__ = 'kama_pb2'
  # @@protoc_insertion_point(class_scope:kama.Attribute)
  ))
_sym_db.RegisterMessage(Attribute)

Link = _reflection.GeneratedProtocolMessageType('Link', (_message.Message,), dict(
  DESCRIPTOR = _LINK,
  __module__ = 'kama_pb2'
  # @@protoc_insertion_point(class_scope:kama.Link)
  ))
_sym_db.RegisterMessage(Link)

Permission = _reflection.GeneratedProtocolMessageType('Permission', (_message.Message,), dict(
  DESCRIPTOR = _PERMISSION,
  __module__ = 'kama_pb2'
  # @@protoc_insertion_point(class_scope:kama.Permission)
  ))
_sym_db.RegisterMessage(Permission)

CreateEntityRequest = _reflection.GeneratedProtocolMessageType('CreateEntityRequest', (_message.Message,), dict(
  DESCRIPTOR = _CREATEENTITYREQUEST,
  __module__ = 'kama_pb2'
  # @@protoc_insertion_point(class_scope:kama.CreateEntityRequest)
  ))
_sym_db.RegisterMessage(CreateEntityRequest)



_KAMADATABASE = _descriptor.ServiceDescriptor(
  name='KamaDatabase',
  full_name='kama.KamaDatabase',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=603,
  serialized_end=1170,
  methods=[
  _descriptor.MethodDescriptor(
    name='ListEntities',
    full_name='kama.KamaDatabase.ListEntities',
    index=0,
    containing_service=None,
    input_type=_ENTITY,
    output_type=_ENTITY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetEntity',
    full_name='kama.KamaDatabase.GetEntity',
    index=1,
    containing_service=None,
    input_type=_ENTITY,
    output_type=_ENTITY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='CreateEntity',
    full_name='kama.KamaDatabase.CreateEntity',
    index=2,
    containing_service=None,
    input_type=_CREATEENTITYREQUEST,
    output_type=_ENTITY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteEntity',
    full_name='kama.KamaDatabase.DeleteEntity',
    index=3,
    containing_service=None,
    input_type=_ENTITY,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateEntity',
    full_name='kama.KamaDatabase.UpdateEntity',
    index=4,
    containing_service=None,
    input_type=_ENTITY,
    output_type=_ENTITY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='AddAttribute',
    full_name='kama.KamaDatabase.AddAttribute',
    index=5,
    containing_service=None,
    input_type=_ATTRIBUTE,
    output_type=_ATTRIBUTE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteAttributes',
    full_name='kama.KamaDatabase.DeleteAttributes',
    index=6,
    containing_service=None,
    input_type=_ATTRIBUTE,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='AddLink',
    full_name='kama.KamaDatabase.AddLink',
    index=7,
    containing_service=None,
    input_type=_LINK,
    output_type=_LINK,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeleteLink',
    full_name='kama.KamaDatabase.DeleteLink',
    index=8,
    containing_service=None,
    input_type=_LINK,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='AddPermission',
    full_name='kama.KamaDatabase.AddPermission',
    index=9,
    containing_service=None,
    input_type=_PERMISSION,
    output_type=_PERMISSION,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DeletePermission',
    full_name='kama.KamaDatabase.DeletePermission',
    index=10,
    containing_service=None,
    input_type=_PERMISSION,
    output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_KAMADATABASE)

DESCRIPTOR.services_by_name['KamaDatabase'] = _KAMADATABASE

# @@protoc_insertion_point(module_scope)
