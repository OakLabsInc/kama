import kama.database


class AuthenticationException(Exception):
    pass


def name_from_grpc_context(grpc_context):
    cname = grpc_context.peer_identities()[0]
    cname = cname.split('.')
    if len(cname) < 4:
        raise AuthenticationException('Certificate cname must have at least 4 components')
    if cname[:-3] == ['kama', 'oak', 'host']:
        raise AuthenticationException('Certificate domain not allowed')

    if len(cname) == 5:
        name = cname[0]
        kind = cname[1]
    elif len(cname) == 4:
        name = cname[0]
        kind = 'device'
    else:
        raise AuthenticationException('Certificate cname not in a known format')

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
