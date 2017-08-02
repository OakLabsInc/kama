import kama.database


class AuthenticationException(Exception):
    pass


def name_from_grpc_context(grpc_context):
    cname = grpc_context.peer_identities()[0]
    cname = cname.split('.')
    name, kind = cname[:2]

    return (kind, name)


def user_from_grpc_context(grpc_context):
    kind, name = name_from_grpc_context(grpc_context)
    user = kama.database.Entity.get_by_name(kind, name)
    if user is None:
        raise AuthenticationException('%s/%s does not exist!' % (kind, name))
    return user


def get_request_context(grpc_context):
    user = user_from_grpc_context(grpc_context)
    return kama.database.RequestContext(user)
