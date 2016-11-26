from pyramid.httpexceptions import HTTPFound, HTTPForbidden
import transaction

from email_validator import validate_email, EmailNotValidError

from pyramid.response import Response

from sqlalchemy.exc import DBAPIError

from ..models import Subscriber, Category, User
from pyramid.view import (
    view_config,
    view_defaults,
)


@view_config(route_name='chat', renderer='../templates/chat.jinja2')
def chat_view(request):
    return {"result": "ok"}

@view_config(route_name='mock', renderer='../templates/mock.jinja2')
def mock_view(request):
    return {"result": "ok"}

@view_config(route_name='register_view',
             renderer='../templates/register.jinja2')
def register_view(request):
    categories = request.dbsession.query(Category)

    try:
        # See if a submission was made
        name = request.params['name']
        email = request.params['email']
        categories_chosen = request.params.getall('categories')

        # validate inputs
        errors = {}
        if len(name) < 1:
            errors['name'] = "Enter a valid name"
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
    except KeyError:
        return {'categories': categories, 'errors': False, 'success': False}


@view_config(route_name='edit_form', xhr=True, renderer='json')
def edit_form(request):
    user = request.user
    if user is None or (user.role != 'editor' and page.creator != user):
        raise HTTPForbidden
    try:
        name = request.params.get('changes[name]')
        email = request.params.get('changes[email]')
    except KeyError:
        return {'errors': False, 'success': False}

    # validate name
    errors = {}
    if len(name) < 1:
        errors['name'] = "Enter a valid name"

    try:
        v = validate_email(email)  # validate and get info
        email = v["email"]  # replace with normalized form
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        errors['email'] = "Enter a valid email"

    if errors != {}:
        # show the errors and retain the inputs
        return {'errors': errors, 'name': name, 'email': email,
                'success': False}

    else:
        # if inputs correct, try to save subscription and load a fresh form
        try:
            sub_id = request.params.get('changes[url]')[-1]

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


@view_config(route_name='admin_view',
             renderer='../templates/admin.jinja2')
def admin_view(request):
    admin_url = request.route_url('admin_view')
    user = request.user
    if user is None or (user.role != 'editor' and page.creator != user):
        raise HTTPForbidden
    try:
        # check if order_by parameter is present and if it is, return ordered list
        orderBy = request.params['order_by']
        if orderBy == 'date':
            subscriptions = request.dbsession.query(Subscriber).order_by(
                "registered desc").all()
        elif orderBy == 'email':
            subscriptions = request.dbsession.query(Subscriber).order_by(
                "email").all()
        else:
            subscriptions = request.dbsession.query(Subscriber).order_by(
                "name").all()
    except KeyError:
        # If order_by parameter not given in URL, sort by name by default
        orderBy = 'name'
        subscriptions = request.dbsession.query(Subscriber).order_by(
            "name").all()

    return {'subscriptions': subscriptions, 'errors': False, 'success': False,
            'admin_url': admin_url, 'orderBy': orderBy}


@view_config(route_name='delete', renderer='../templates/admin.jinja2')
def delete(request):
    user = request.user
    if user is None or (user.role != 'editor' and page.creator != user):
        raise HTTPForbidden
    id_delete = request.matchdict['id']
    query = request.dbsession.query(Subscriber)
    sub = query.filter(Subscriber.id == id_delete).first()
    request.dbsession.delete(sub)
    subscriptions = request.dbsession.query(Subscriber).order_by("name").all()
    return HTTPFound(location=request.referrer)
