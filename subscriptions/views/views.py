from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Subscriber, Category

@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    
    categories = request.dbsession.query(Category).all()  
    return {'categories': categories}

@view_config(route_name='register_received_view')
def register_received_view(request):
    name = request.params['name']
    email = request.params['email'] 
    categories = request.params.getall('categories') 
    try:
        new_subscriber = Subscriber(name=name, email=email)
        for cat in categories:
            query = request.dbsession.query(Category)
            category = query.filter(Category.name == cat).first()
            new_subscriber.categories.append(category)
        request.dbsession.add(new_subscriber)
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return Response('OK')


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    return {'one': 'one', 'project': 'subscriptions'}


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_subscriptions_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
