"""Test the validation for the core configuration schema."""

import json
import pytest

from flask_jsondash import charts_builder as app


def _schema(**vals):
    """Default schema."""
    data = dict(
        id='a-b-c-d-e',
        date="2016-08-23 15:03:49.178000",
        layout="grid",
        name="testlayout",
        modules=[],
    )
    data.update(**vals)
    return json.dumps(data)


@pytest.mark.schema
def test_validate_raw_json_valid_empty_modules():
    assert app.validate_raw_json(_schema())


@pytest.mark.schema
def test_validate_raw_json_valid_freeform():
    d = _schema(
        layout='freeform',
        modules=[
            dict(guid='a-b-c-d-e', name='foo', dataSource='foo',
                 width=1, height=1, type='line',
                 family='C3')]
    )
    assert app.validate_raw_json(d)


@pytest.mark.schema
def test_validate_raw_json_valid_fixed():
    d = _schema(
        layout='freeform',
        modules=[
            dict(guid='a-b-c-d-e', name='foo', dataSource='foo',
                 width='1', height=1, type='line',
                 family='C3')]
    )
    assert app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'type',
    'family',
    'width',
    'height',
    'dataSource',
])
def test_validate_raw_json_missing_required_module_keys(field):
    module = dict(
        guid='a-b-c-d-e',
        name='foo', dataSource='foo',
        width='col-1', height=1, type='line',
        family='C3')
    del module[field]
    d = _schema(
        layout='grid',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError):
        app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'row',
])
def test_validate_raw_json_missing_required_fixedgrid_module_keys(field):
    module = dict(
        guid='a-b-c-d-e',
        name='foo', dataSource='foo',
        width='col-1', height=1, type='line',
        row=1, family='C3')
    del module[field]
    d = _schema(
        layout='grid',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError):
        app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'row',
])
def test_validate_raw_json_missing_optional_freeform_module_keys(field):
    # Ensure that required fields for fixed grid
    # are not required for freeform layouts.
    module = dict(
        guid='a-b-c-d-e',
        name='foo', dataSource='foo',
        width=1, height=1, type='line',
        row=1, family='C3')
    del module[field]
    d = _schema(
        layout='freeform',
        modules=[module]
    )
    assert app.validate_raw_json(d)


@pytest.mark.schema
@pytest.mark.parametrize('field', [
    'id',
    'layout',
    'name',
    'modules',
])
def test_validate_raw_json_invalid_missing_toplevel_keys(field):
    module = dict(
        guid='a-b-c-d-e',
        layout='freeform',
        name='foo', dataSource='foo',
        width=1, height=1, type='line', family='C3',
    )
    config = _schema(
        layout='freeform',
        modules=[module]
    )
    config = json.loads(config)
    del config[field]
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(json.dumps(config))
    assert "{'" + field + "': ['required field']}" in str(exc.value)


@pytest.mark.schema
def test_validate_raw_json_invalid_mixed_use_freeform_with_rows():
    # Ensure `row` in modules and layout `freeform` cannot be mixed.
    module = dict(
        guid='a-b-c-d-e',
        name='foo', dataSource='foo',
        width=1, height=1, type='line',
        row=1, family='C3',
    )
    config = _schema(
        layout='freeform',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(config)
    assert 'Cannot mix' in str(exc.value)


@pytest.mark.schema
def test_validate_raw_json_missing_row_for_layout_grid():
    module = dict(
        guid='a-b-c-d-e',
        name='foo', dataSource='foo',
        width='col-1', height=1, type='line', layout='grid', family='C3',
    )
    config = _schema(
        layout='grid',
        modules=[module]
    )
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(config)
    assert 'Invalid row value for module "foo"' in str(exc.value)


@pytest.mark.schema
def test_validate_raw_json_invalid_grid_nonconsencutive_rows():
    # Ensure row numbers can't "skip", e.g. [1, 2, 10]
    config = _schema(
        layout='grid',
        modules=[
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=1, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=2, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=10, height=1, family='C3', type='line'),
        ]
    )
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(config)
    assert 'Row order is not consecutive' in str(exc.value)


@pytest.mark.schema
def test_validate_raw_json_invalid_grid_consecutive_but_duplicate_rows():
    # Ensure duplicate row numbers are consecutive, IF they were unique.
    # e.g. [1, 1, 2, 2, 3] is valid.
    config = _schema(
        layout='grid',
        id='a-b-c-d-e',
        modules=[
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=1, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=1, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=2, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=2, height=1, family='C3', type='line'),
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=3, height=1, family='C3', type='line'),
        ]
    )
    assert app.validate_raw_json(config)


@pytest.mark.schema
def test_validate_raw_json_invalid_family():
    config = _schema(
        layout='grid',
        modules=[
            dict(guid='a-b-c-d-e', name='f', dataSource='f', width='col-1',
                 row=1, height=1, family='LOLWUT', type='line'),
        ]
    )
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(config)
    assert 'unallowed value LOLWUT' in str(exc.value)


@pytest.mark.schema
def test_validate_raw_json_invalid_width_string_cols_for_freeform_type():
    config = _schema(
        layout='freeform',
        modules=[
            dict(guid='a-b-c-d-e',
                 name='f',
                 dataSource='f',
                 width='col-12',
                 height=1,
                 family='C3',
                 type='line'),
        ]
    )
    with pytest.raises(app.InvalidSchemaError) as exc:
        app.validate_raw_json(config)
    err = str(exc.value)
    assert 'Invalid value for width in `freeform` layout.' in err
