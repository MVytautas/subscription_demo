def includeme(config):
    config.add_route('css', '/static/{css_path:.*}.css')
    config.add_view(route_name='css', view='pyramid_scss.controller.get_scss',
                    renderer='scss', request_method='GET')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('login', '/login')
    config.add_route('chat', '/')
    config.add_route('logout', '/logout')
    config.add_route('delete', '/admin/remove/{id}')
    config.add_route('edit_form', '/admin/edit/{id}')
    config.add_route('admin_view', '/admin')
    config.add_route('register_view', '/register')

    config.add_route('mock', '/mock')
