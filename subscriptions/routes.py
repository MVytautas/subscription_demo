def includeme(config):
    config.add_route('css', '/static/{css_path:.*}.css')
    config.add_view(route_name='css', view='pyramid_scss.controller.get_scss', renderer='scss', request_method='GET')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('register_received_view', '/register_received')
    config.add_route('register', '/register')
    config.add_route('home', '/')

