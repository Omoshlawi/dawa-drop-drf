from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

"""
In web development, middleware is software that lies between an 
operating system and the applications running on it. In the context of web
 frameworks, a middleware is a function that is invoked in between the client 
 and the server to perform some kind of processing on the incoming request or 
 outgoing response. In other words, it's a piece of code that acts as a bridge 
 between the server and the application and performs some action before or after
  the request is processed by the application.

In the case of Django, middleware is a framework-level component that provides a way 
to modify the request or response globally for all requests that pass through it.
 Middleware functions can be used for various purposes, such as authentication, 
 caching, rate limiting, compression, and more. It's a powerful tool that can be
  used to add or remove functionality from a Django application.
"""

from channels.db import database_sync_to_async


@database_sync_to_async
def get_user(token):
    try:
        token = Token.objects.get(key=token)
        user = token.user
    except Token.DoesNotExist:
        user = AnonymousUser()
    return user


class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope['query_string'].decode())
        token_key = query_params.get('token', [None])[0]
        if token_key:
            scope['user'] = await get_user(token_key)
        return await self.inner(scope, receive, send)


"""
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope['query_string'].decode())
        token_key = query_params.get('token', [None])[0]
        if token_key:
            try:
                token = Token.objects.get(key=token_key)
                scope['user'] = token.user
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return await self.inner(scope, receive, send)

"""
