import pytest
from flask import request, current_app
from .. import create_app
from ..extensions import collection
from ..userClass import User

adminUser = User('admin', 'admin', 'admin@email.com', 'lowell', 'adminpass', 'admin')
resUser = User('uno', 'dos', 'e@mail.com', 'nau', 'respass', 'researcher')
nonUser = User('no', 'no', 'n@o.o', 'no', 'no', 'no')

researchers = [
    User(
        'fRes'+str(num), 
        'lRes'+str(num), 
        'researcher'+str(num)+'@email.com', 
        'institution', 
        'password'+str(num), 
        'researcher') for num in range(5)
]

taken = User('taken', 'taken', 'taken@email.com', 'taken', 'taken', 'researcher')


def clean_db(server):
    if 'TESTING' in current_app.config:
        if current_app.config['TESTING']:
            for tag in ['user', 'glossary', 'news', 'rv']:
                for entry in collection(tag).find():
                    collection(tag).remove({'_id': entry['_id']})

        else:
            print('test_config.TESTING set to False')
            raise ValueError
    else:
        print('test_config.TESTING not set')
        raise ValueError

def populate_db(server):
    if 'TESTING' in current_app.config:
        if current_app.config['TESTING']:
            for user in researchers+[taken]:
                collection('user').insert_one(user.to_json())

        else:
            print('test_config.TESTING set to False')
            raise ValueError
    else:
        print('test_config.TESTING not set')
        raise ValueError

@pytest.fixture(scope='session')
def server(): 
    server = create_app('unittest/test_config.py')
    with server.app_context():
        server.config['WTF_CSRF_ENABLED'] = False
        clean_db(server)
        populate_db(server)
    yield server
    # p.terminate()


