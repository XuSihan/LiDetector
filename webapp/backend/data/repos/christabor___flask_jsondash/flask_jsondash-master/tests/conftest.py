import json
import os

import pytest

from flask import Flask, url_for
from pyquery import PyQuery as pq

from flask_jsondash import charts_builder, utils
from flask_jsondash import db

URL_BASE = 'http://127.0.0.1:80'
app = Flask('test_flask_jsondash',
            template_folder='../flask_jsondash/example_app/templates')
app.config.update(
    # Required to fix context errors.
    # See https://github.com/jarus/flask-testing/issues/21
    PRESERVE_CONTEXT_ON_EXCEPTION=False,
    SECRET_KEY='123',
)
app.debug = True
app.register_blueprint(charts_builder.charts)

fake_db = []


def _username():
    return 'Username'


def auth_valid(**kwargs):
    return True


def auth_invalid(**kwargs):
    return False


def get_json_config(name):
    parent = os.getcwd().replace('tests/', '')
    path = '{0}/example_app/examples/config/{1}'.format(parent, name)
    view = json.load(open(path, 'r'))
    return view


def read(*args, **kwargs):
    if 'override' in kwargs:
        newkwargs = kwargs.pop('override')

        def _read(*args, **kwargs):
            return dict(**newkwargs)
        return _read
    if 'c_id' not in kwargs:
        return fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == kwargs.get('c_id'):
            return dash


def delete(c_id, **kwargs):
    global fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == c_id:
            del fake_db[i]
            break


def create(*args, **kwargs):
    global fake_db
    fake_db.append(dict(**kwargs.get('data')))


def update(c_id, **kwargs):
    global fake_db
    for i, dash in enumerate(fake_db):
        if dash['id'] == c_id:
            fake_db[i].update(**kwargs)
            break


def setup_dashboard(monkeypatch, app, test, data):
    """Helper function to setup dashboard, redirect, and get its html."""
    assert len(read()) == 0
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    test.post(url_for('jsondash.create'), data=data, follow_redirects=True)
    view_id = read()[0]['id']
    assert len(read()) == 1
    url = url_for('jsondash.view', c_id=view_id)
    res = test.get(url)
    dom = pq(res.data)
    return dom


def make_chart(**kwargs):
    """Create a fake chart."""
    data = dict(
        name='somechart',
        width=1,
        height=1,
        family='C3',
        type='line',
        row=1,
        dataSource='...',
    )
    data.update(**kwargs)
    return json.dumps(data)


@pytest.yield_fixture(autouse=True)
def ctx(monkeypatch, request):
    with app.test_request_context() as req_ctx:
        global fake_db
        fake_db = []
        monkeypatch.setattr(utils.adapter, 'read', read)
        monkeypatch.setattr(utils.adapter, 'create', create)
        monkeypatch.setattr(utils.adapter, 'delete', delete)
        monkeypatch.setattr(utils.adapter, 'update', update)
        monkeypatch.setattr(utils.adapter, 'filter', read)
        yield req_ctx


@pytest.fixture()
def adapter():
    return db.get_db_handler()


@pytest.fixture()
def client():
    app.config.update(
        JSONDASH_GLOBALDASH=False,
        JSONDASH_FILTERUSERS=False,
        JSONDASH_GLOBAL_USER='global-test',
    )
    app.config['JSONDASH'] = dict(
        metadata=dict(
            created_by=_username,
            username=_username,
        ),
        static=dict(
            js_path='js/vendor/',
            css_path='css/vendor/',
        ),
        auth=dict(
            edit_others=auth_invalid,
            edit_global=auth_invalid,
            create=auth_invalid,
            view=auth_invalid,
            clone=auth_invalid,
            delete=auth_invalid,
        )
    )
    return app, app.test_client()
