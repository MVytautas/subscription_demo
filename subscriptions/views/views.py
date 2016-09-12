import transaction

from email_validator import validate_email, EmailNotValidError

from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError
from pyramid.security import (
    remember,
    forget,
)

from pyramid.view import (
    view_config,
    view_defaults,
    forbidden_view_config,
)

from ..models import Subscriber, Category
from ..security import (
    USERS,
    check_password,
)


@view_config(route_name='register_view',
             renderer='../templates/register.jinja2')
def register_view(request):
    categories = request.dbsession.query(Category)
    return {'categories': categories, 'errors': False, 'success': False}


@view_config(route_name='register_received_view',
             renderer='../templates/register.jinja2')
def register_received_view(request):
    categories = request.dbsession.query(Category).all()

    try:
        name = request.params['name']
        email = request.params['email']
        categories_chosen = request.params.getall('categories')
    except KeyError:
        return {'categories': categories, 'errors': False, 'success': False}

    # validate inputs
    errors = {}
    if len(name) < 1:
        errors['name'] = "You must provide a name longer than 1 character"
    if len(categories_chosen) < 1:
        errors['cats'] = "You must choose at least 1 category"

    try:
        v = validate_email(email)  # validate and get info
        email = v["email"]  # replace with normalized form
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        errors['email'] = "Enter a valid email"

    if errors != {}:
        # show the errors and retain the inputs
        return {'errors': errors, 'name': name, 'email': email,
                'categories_chosen': categories_chosen,
                'categories': categories}
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
            return Response(
                "Database error. We are instantly notified and  will fix it soon!",
                content_type='text/plain', status=500)
        return {'categories': categories, 'errors': False, 'success': True}


@view_config(route_name='edit_form', xhr=True, renderer='json')
def edit_form(request):
    try:
        name = request.params.get('changes[name]')
        email = request.params.get('changes[email]')
    except KeyError:
        return {'errors': False, 'success': False}

    # validate name
    errors = {}
    if len(name) < 1:
        errors['name'] = "You must provide a name longer than 1 character"

    try:
        v = validate_email(email)  # validate and get info
        email = v["email"]  # replace with normalized form
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        errors['email'] = "Enter a valid email"

    if errors != {}:
        # show the errors and retain the inputs
        return {'errors': errors, 'name': name, 'email': email}

    else:
        # if inputs correct, try to save subscription and load a fresh form
        try:
            # TODO add ID retrieval for any subscriber
            sub_id = request.params.get('changes[url]')

            # for testing purposes
            sub_id = 7

            query = request.dbsession.query(Subscriber)
            subscriber = query.filter(Subscriber.id == sub_id).first()

            subscriber.name = name
            subscriber.email = email

            request.dbsession.flush()
            transaction.commit()

        except DBAPIError:
            return Response(
                "Database error. We are instantly notified and  will fix it soon!",
                content_type='text/plain', status=500)
        return {'errors': False, 'success': True}


@view_config(route_name='list_view_unordered',
             renderer='../templates/list.jinja2')
def list_view_unordered(request):
    list_url = request.route_url('list_view_unordered')
    subscriptions = request.dbsession.query(Subscriber).all()

    return {'subscriptions': subscriptions, 'errors': False, 'success': False,
            'list_url': list_url}


@view_config(route_name='list_view', renderer='../templates/list.jinja2')
def list_view(request):
    list_url = request.route_url('list_view_unordered')
    orderBy = request.matchdict['orderBy']

    if orderBy == 'date':
        subscriptions = request.dbsession.query(Subscriber).order_by(
            "registered desc").all()
    elif orderBy == 'email':
        subscriptions = request.dbsession.query(Subscriber).order_by(
            "email").all()
    else:
        subscriptions = request.dbsession.query(Subscriber).order_by(
            "name").all()
    return {'subscriptions': subscriptions, 'errors': False, 'success': False,
            'orderBy': orderBy, 'list_url': list_url}


@view_config(route_name='delete', renderer='../templates/list.jinja2')
def delete(request):
    id_delete = request.matchdict['id']
    query = request.dbsession.query(Subscriber)
    sub = query.filter(Subscriber.id == id_delete).first()
    request.dbsession.delete(sub)
    subscriptions = request.dbsession.query(Subscriber).order_by("name").all()
    return HTTPFound(location=request.referrer)


@view_defaults(renderer='../templates/login.jinja2')
class UserViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @view_config(route_name='login', renderer='../templates/login.jinja2')
    @forbidden_view_config(renderer='../templates/login.jinja2')
    def login(self):
        request = self.request

        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']

            if check_password(password, USERS.get(login)):
                headers = remember(request, login)
                return HTTPFound(location=came_from,
                                 headers=headers)
            message = 'Failed login'

        return dict(
            name='Login',
            message=message,
            url=request.application_url + '/login',
            came_from=came_from,
            login=login,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url,
                         headers=headers)
