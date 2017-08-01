import kama.database


class Device(kama.database.Entity):
    @classmethod
    def from_entity(cls, entity):
        return cls(entity.uuid, entity.kind, entity.name)

    @classmethod
    def get_by_serial(cls, serial, context=None):
        for device in cls.all():
            if device.serial(context=context) == serial:
                return device
        return None

    def serial(self, context=None):
        a = self.attributes('serial', context=context)
        if not a:
            return None
        else:
            return a[0].value

    @classmethod
    def create(cls, name, owner_role):
        entity = kama.database.Entity.create('device', name, owner_role)
        owner_role.add_link(entity, context=kama.database.InternalContext())
        return cls.from_entity(entity)

    @classmethod
    def all(cls):
        return [cls.from_entity(x) for x in cls.get_by_kind('device')]
