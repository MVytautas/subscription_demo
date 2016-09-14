import os
import sys

import random
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import Admin, Subscriber, Category, User


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        editor = User(name='editor', role='editor')
        editor.set_password('editor')
        dbsession.add(editor)

        categories = [
            'Politics',
            'Celebrities',
            'Sports',
            'Economy',
            'Entertainment',
        ]

        for category in categories:
            entry = Category(name=category)
            dbsession.add(entry)

        # for development

        for i in range(5):

            name = 'Test Name {}'.format(i)
            email = 'test.email{}@test.com'.format(i)

            new_user = Subscriber(name=name, email=email)

            # number of categories
            cat_num = random.randint(1, 5)

            # categories indexes
            cat_ind = random.sample(range(0, 5), cat_num)

            chosen_categories = []
            for index in cat_ind:
                chosen_categories.append(categories[index])

            for cat in chosen_categories:
                query = dbsession.query(Category)
                category = query.filter(Category.name == cat).first()
                new_user.categories.append(category)

                dbsession.add(new_user)
