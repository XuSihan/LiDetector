import json

from flask import url_for

from pyquery import PyQuery as pq

import pytest

from conftest import (
    get_json_config,
    auth_valid,
    read,
    setup_dashboard,
    make_chart,
)

from flask_jsondash import charts_builder
from flask_jsondash import settings
from flask_jsondash.utils import adapter

REDIRECT_MSG = 'You should be redirected automatically'


def test_app_redirects(client):
    _, test = client
    res = test.get('/charts')
    assert REDIRECT_MSG in str(res.data)


@pytest.mark.parametrize('url, expected', [
    ('jsondash.dashboard', '/charts/'),
    ('jsondash.create', '/charts/create'),
])
def test_basic_routes(client, url, expected):
    assert url_for(url) == expected


@pytest.mark.parametrize('url, expected', [
    ('jsondash.view', '/charts/foo'),
    ('jsondash.update', '/charts/foo/update'),
    ('jsondash.clone', '/charts/foo/clone'),
    ('jsondash.delete', '/charts/foo/delete'),
])
def test_chart_routes(client, url, expected):
    assert url_for(url, c_id='foo') == expected


def test_get_dashboard_contains_all_chart_types_list(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    assert res.status_code == 200
    for family, config in settings.CHARTS_CONFIG.items():
        for chart in config['charts']:
            _, label = chart
            assert label in str(res.data)


def test_get_dashboard_contains_no_chart_msg(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = str(test.get(url_for('jsondash.dashboard')).data)
    assert 'No dashboards exist. Create one below to get started.' in res


def test_dashboards_override_perpage_pagination(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    for i in range(10):
        data = dict(name=i, modules=[])
        res = test.post(url_for('jsondash.create'), data=data)
    res = test.get(url_for('jsondash.dashboard') + '?per_page=2')
    # Ensure 10 exist, but only 5 are shown
    assert len(read()) == 10
    dom = pq(res.data)
    assert len(dom.find('.pagination').find('li:not(.active)')) == 5


def test_create_dashboards_check_index_count(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    for i in range(10):
        data = dict(name=i, modules=[])
        res = test.post(url_for('jsondash.create'), data=data)
    res = test.get(url_for('jsondash.dashboard'))
    assert len(read()) == 10
    heading = pq(res.data).find('h1.lead').text()
    assert 'Showing 10 dashboards with 0 charts' in heading


def test_get_view_valid_id_invalid_config(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(modules=[dict(foo='bar')])
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    with pytest.raises(ValueError):
        res = test.get(url_for('jsondash.view', c_id='123'))
        assert 'Invalid config!' in str(res.data)


def test_get_view_valid_id_invalid_modules(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(id='123')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(
        url_for('jsondash.view', c_id='123'),
        follow_redirects=True)
    assert 'Invalid configuration - missing modules.' in str(res.data)


def test_get_view_valid_id_ensure_id_popped(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    view = dict(view)
    view.update(_id='foo')
    readfunc = read(override=view)
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert len(dom.find('.item')) == len(view['modules'])


def test_view_valid_dashboard_count_and_inputs(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert len(dom.find('.item')) == len(view['modules'])
    assert len(dom.find('.charts-input-icon')) == 1


def test_view_valid_dashboard_inputs_form(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    charts_with_inputs = [m for m in view['modules'] if 'inputs' in m]
    num_config_inputs = len(charts_with_inputs[0]['inputs']['options'])
    assert num_config_inputs == 5  # Sanity check
    assert len(charts_with_inputs) == 1
    assert len(dom.find('.chart-inputs')) == 1
    assert dom.find('.chart-inputs').hasClass('collapse')
    # There are 7 input fields generated for this particular json file.
    assert len(dom.find('.chart-inputs form input')) == 7


def test_view_valid_dashboard_inputs_form_counts(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    charts_with_inputs = [m for m in view['modules'] if 'inputs' in m]
    input_options = charts_with_inputs[0]['inputs']['options']
    radio_opts = [o for o in input_options if o['type'] == 'radio'][0]
    radio_opts = radio_opts['options']
    assert len(dom.find('.chart-inputs form .input-radio')) == len(radio_opts)
    select = [o for o in input_options if o['type'] == 'select']
    assert len(dom.find('.chart-inputs form select')) == len(select)
    options = select[0]['options']
    assert len(dom.find('.chart-inputs form select option')) == len(options)
    numbers = [inp for inp in input_options if inp['type'] == 'number']
    assert len(dom.find('.chart-inputs [type="number"]')) == len(numbers)
    text = [inp for inp in input_options if inp['type'] == 'text']
    assert len(dom.find('.chart-inputs [type="text"]')) == len(text)
    checkbox = [inp for inp in input_options if inp['type'] == 'checkbox']
    assert len(dom.find('.chart-inputs [type="checkbox"]')) == len(checkbox)


def test_get_view_valid_modules_valid_dash_title(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.get(url_for('jsondash.view', c_id=view['id']))
    dom = pq(res.data)
    assert dom.find('.dashboard-title').text() == view['name']


def test_create_valid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(
        url_for('jsondash.create'),
        data=dict(name='mydash-valid'),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Created new dashboard "mydash-valid"'
    assert dom.find('.alert-info').text() == flash_msg


@pytest.mark.invalid_id_redirect
def test_get_view_invalid_id_redirect(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.get(url_for('jsondash.view', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


@pytest.mark.invalid_id_redirect
def test_clone_invalid_id_redirect(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(url_for('jsondash.clone', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


@pytest.mark.invalid_id_redirect
def test_delete_invalid_id_redirect(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(
        url_for('jsondash.delete', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


@pytest.mark.update_raw
@pytest.mark.invalid_id_redirect
def test_update_invalid_id_redirect(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    res = test.post(url_for('jsondash.update', c_id='123'))
    assert REDIRECT_MSG in str(res.data)


def test_clone_valid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert len(read()) == 0
    res = test.post(url_for('jsondash.create'),
                    data=dict(name='mydash', modules=[]),
                    follow_redirects=True)
    dom = pq(res.data)
    new_id = read()[0]['id']
    assert read()[0]['name'] == 'mydash'
    flash_msg = 'Created new dashboard "mydash"'
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1
    assert read()[0]['name'] == 'mydash'
    res = test.post(
        url_for('jsondash.clone', c_id=new_id),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Created new dashboard clone "Clone of mydash"'
    assert flash_msg in dom.find('.alert').text()
    assert len(read()) == 2


def test_delete_valid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = dict(name='mydash', modules=[])
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    assert not read()
    # Create first one.
    res = test.post(url_for('jsondash.create'),
                    data=view,
                    follow_redirects=True)
    assert len(read()) == 1
    view_id = read()[0]['id']
    dom = pq(res.data)
    flash_msg = 'Created new dashboard "mydash"'
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1
    res = test.post(url_for('jsondash.delete', c_id=view_id),
                    follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Deleted dashboard "{}"'.format(view_id)
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 0


@pytest.mark.update_raw
def test_update_edit_raw_invalid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    view = get_json_config('inputs.json')
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.post(
        url_for('jsondash.update', c_id=view['id']),
        data={'edit-raw': 'on'},
        follow_redirects=True)
    dom = pq(res.data)
    assert 'Error: Invalid JSON config.' in dom.find('.alert-danger').text()


@pytest.mark.schema
@pytest.mark.update_raw
@pytest.mark.parametrize('field', [
    'type',
    'family',
])
def test_update_edit_raw_invalidschema_missing_x(field, monkeypatch,
                                                 client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    module = dict(
        name='foo', width=1, height=1,
        guid='a-b-c-d-e', dataSource='...',
        family='C3', type='line',
    )
    view = dict(id='a-b-c-d-e', name='foo', modules=[module])
    del module[field]
    readfunc = read(override=dict(view))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.post(
        url_for('jsondash.update', c_id=view['id']),
        data={'edit-raw': 'on', 'config': json.dumps(view)},
        follow_redirects=True)
    dom = pq(res.data)
    err_msg = "{'" + field + "': ['required field']"
    assert err_msg in dom.find('.alert-danger').text()


@pytest.mark.update_raw
def test_update_edit_raw_valid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert not read()
    res = test.post(
        url_for('jsondash.create'),
        data=dict(
            id='a-b-c-d-e',
            layout='freeform',
            name='newname', date='', modules=[]),
        follow_redirects=True)
    assert len(read()) == 1
    view_id = read()[0]['id']
    data = {
        'date': '',
        'layout': 'freeform',
        'id': 'a-b-c-d-e',
        'name': 'foo', 'modules': []}
    view = json.dumps(data)
    readfunc = read(override=dict(data))
    monkeypatch.setattr(adapter, 'read', readfunc)
    res = test.post(
        url_for('jsondash.update', c_id=view_id),
        data={'config': view, 'edit-raw': 'on'},
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Updated view "{}"'.format(view_id)
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1


@pytest.mark.update
def test_update_valid(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert not read()
    res = test.post(
        url_for('jsondash.create'),
        data=dict(mode='grid', name='newname', modules=[]),
        follow_redirects=True)
    assert res.status_code == 200
    assert len(read()) == 1
    view_id = read()[0]['id']
    res = test.post(
        url_for('jsondash.update', c_id=view_id),
        data=dict(mode='grid', name='newname'),
        follow_redirects=True)
    dom = pq(res.data)
    flash_msg = 'Updated view "{}"'.format(view_id)
    assert dom.find('.alert-info').text() == flash_msg
    assert len(read()) == 1


@pytest.mark.update
def test_update_invalid_swap_freeform_to_grid_no_row(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    assert not read()
    dash_data = dict(
        name='newname',
        mode='freeform',
        module_foo=json.dumps(
            dict(dataSource='...', width=1, height=1,
                 name='foo', family='C3', type='line')),
        module_bar=json.dumps(
            dict(dataSource='...', width=1, height=1,
                 name='foo', family='C3', type='line')),
    )
    res = test.post(url_for('jsondash.create'),
                    data=dash_data,
                    follow_redirects=True)
    assert res.status_code == 200
    assert len(read()) == 1
    view_id = read()[0]['id']
    dash_data.update(mode='grid')
    res = test.post(url_for('jsondash.update', c_id=view_id),
                    data=dash_data,
                    follow_redirects=True)
    dom = pq(res.data)
    flash_msg = ('Cannot use grid layout without specifying row(s)! '
                 'Edit JSON manually to override this.')
    assert flash_msg in dom.find('.alert-danger').text()
    assert len(read()) == 1


def test_no_demo_mode(monkeypatch, client):
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    data = dict(name='newname', modules=[])
    test.post(url_for('jsondash.create'), data=data, follow_redirects=True)
    view_id = read()[0]['id']
    url = url_for('jsondash.view', c_id=view_id)
    res = test.get(url)
    dom = pq(res.data)
    assert dom.find('.chart-header small > .btn')
    assert dom.find('.chart-header small > .btn').text().strip() == 'Back'
    assert dom.find('.chart-header .dropdown-toggle')


def test_demo_mode(monkeypatch, client):
    # Test that certain UI elements are removed when in demo mode.
    _, test = client
    monkeypatch.setattr(charts_builder, 'auth', auth_valid)
    data = dict(name='newname', modules=[])
    test.post(url_for('jsondash.create'), data=data, follow_redirects=True)
    view_id = read()[0]['id']
    url = url_for('jsondash.view', c_id=view_id) + '?jsondash_demo_mode=1'
    res = test.get(url)
    dom = pq(res.data)
    assert not dom.find('.chart-header > small .btn')
    assert not dom.find('.chart-header .dropdown-toggle')


def test_correct_charts_count(monkeypatch, client):
    app, test = client
    data = dict(
        mode='grid',
        name='Some dashboard - lots of cols and rows',
    )
    data.update({
        'module_{}'.format(i): make_chart(row=1) for i in range(5)
    })
    dom = setup_dashboard(monkeypatch, app, test, data)
    container = dom.find('#container')
    assert len(container.find('.item.widget')) == 5
    assert len(container.find('.item.widget').find('.widget-title-text')) == 5
