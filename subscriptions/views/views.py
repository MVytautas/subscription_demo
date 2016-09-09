from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import Subscriber, Category

from email_validator import validate_email, EmailNotValidError
from pyramid.httpexceptions import HTTPFound

@view_config(route_name='register_view', renderer='../templates/register.jinja2')
def register_view(request):
    
    categories = request.dbsession.query(Category)
    return {'categories': categories, 'errors':False, 'success':False}

@view_config(route_name='register_received_view', renderer='../templates/register.jinja2')
def register_received_view(request):
    
    categories = request.dbsession.query(Category).all() 

    try:
        name = request.params['name']
        email = request.params['email'] 
        categories_chosen = request.params.getall('categories') 
    except KeyError:
        return {'categories': categories, 'errors':False, 'success':False}

    #validate inputs
    errors = {}
    if len(name)<1:
        errors['name']="You must provide a name longer than 1 character"
    if len(categories_chosen)<1:
        errors['cats']="You must choose at least 1 category"

    try:
        v = validate_email(email) # validate and get info
        email = v["email"] # replace with normalized form
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        errors['email']="Enter a valid email" 

    if errors!={}:
        # show the errors and retain the inputs
        return {'errors': errors, 'name': name, 'email':email, 'categories_chosen':categories_chosen, 'categories': categories }
    else:
        # if inputs correct, try to save subscription and load a fresh form

        try: 
            new_subscriber = Subscriber(name=name, email=email) 
            for cat in categories_chosen:
                query = request.dbsession.query(Category) 
                category = query.filter(Category.name == cat).first() 
                new_subscriber.categories.append(category)
            request.dbsession.add(new_subscriber)
        except DBAPIError:

            return Response(db_err_msg, content_type='text/plain', status=500)
        return {'categories': categories, 'errors':False, 'success':True}

@view_config(route_name='list_view_unordered', renderer='../templates/list.jinja2')
def list_view_unordered(request):
    subscriptions = request.dbsession.query(Subscriber).all()
    return {'subscriptions': subscriptions, 'errors':False, 'success':False}

@view_config(route_name='list_view', renderer='../templates/list.jinja2')
def list_view(request):
    orderBy = request.matchdict['orderBy']
    if orderBy=='date':
        subscriptions = request.dbsession.query(Subscriber).order_by("registered desc").all()
    elif orderBy=='email':
        subscriptions = request.dbsession.query(Subscriber).order_by("email").all()
    else:
        subscriptions = request.dbsession.query(Subscriber).order_by("name").all()
    return {'subscriptions': subscriptions, 'errors':False, 'success':False, 'orderBy':orderBy}

@view_config(route_name='delete', renderer='../templates/list.jinja2')
def delete(request):
    id_delete = request.matchdict['id']
    query = request.dbsession.query(Category) 
    sub = query.filter(Subscriber.id == id_delete).first() 
    print (sub)
    print ('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    request.dbsession.delete(sub)
    subscriptions = request.dbsession.query(Subscriber).order_by("name").all()
    return HTTPFound(location='/list')
    return {'subscriptions': subscriptions, 'errors':False, 'success':False}




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
