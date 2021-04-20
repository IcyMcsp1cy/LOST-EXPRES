from json import dumps, loads
from . import *
from ..userClass import User

get_rv = {
    "output": "2d-spec-download-data.data",
    "outputs": {
        "id": "2d-spec-download-data",
        "property": "data"
        },
    "inputs": [
        {"id": "2d-spec-download",
            "property": "n_clicks"},
        {"id": "click-data",
            "property": "children","value": "Sun_200902.1101.fits"}
    ],
    "changedPropIds": ["click-data.children"]
}

rv_out = {'multi': True, 'response': {'2d-spec-download-data': {'data': None}}}


def test_dash(server):
    with server.test_client() as client:
        with server.app_context():
            response = client.post('/data/_dash-update-component', data=dumps(get_rv), content_type='application/json')
            assert loads(response.get_data()) == rv_out
