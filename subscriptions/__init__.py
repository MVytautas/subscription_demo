from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from .security import groupfinder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory='.resources.Root')
    config.include('pyramid_chameleon')
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.include("pyramid_scss")

    # Security policies
    authn_policy = AuthTktAuthenticationPolicy(
        settings['subscriptions.secret'], callback=groupfinder,
        hashalg='sha512')
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan('.views')
    return config.make_wsgi_app()

