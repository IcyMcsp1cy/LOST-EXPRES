from . import *
from ..userClass import User

newUser = User('uno', 'dos', 'anew@email.com', 'nau', 'respass', 'researcher')


def test_insert(server):
    with server.test_client() as client:
        with server.app_context():
            entry = collection('user').find_one({'email': 'anew@email.com'})
            assert entry is None

            collection('user').insert_one(newUser.to_json())

            entry = collection('user').find_one({'email': 'anew@email.com'})
            assert entry is not None