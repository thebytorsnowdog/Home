import io
import json
from models import Asset
from tests.conftest import SAMPLE_CSV, SAMPLE_CSV_MINIMAL


def test_dashboard_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Scotland Asset Map' in response.data


def test_upload_page_get(client):
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload Asset Data' in response.data


def test_upload_csv_success(client, db):
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully imported' in response.data
    assert Asset.query.count() == 3


def test_upload_csv_upsert(client, db):
    # First upload
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    client.post('/upload', data=data, content_type='multipart/form-data')
    assert Asset.query.count() == 3

    # Second upload updates existing
    updated_csv = (
        'asset_id,name,asset_type,latitude,longitude,condition,last_inspected\n'
        'BR-001,Forth Road Bridge Updated,Bridge,56.0005,-3.4053,moderate,2024-06-01\n'
    )
    data = {
        'file': (io.BytesIO(updated_csv.encode('utf-8')), 'assets.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert Asset.query.count() == 3  # No new assets created
    asset = Asset.query.filter_by(asset_id='BR-001').first()
    assert asset.name == 'Forth Road Bridge Updated'
    assert asset.condition == 'moderate'


def test_upload_missing_columns(client):
    bad_csv = 'name,latitude\nTest,56.0\n'
    data = {
        'file': (io.BytesIO(bad_csv.encode('utf-8')), 'bad.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'Missing required columns' in response.data


def test_upload_invalid_coordinates(client, db):
    csv_data = (
        'asset_id,name,asset_type,latitude,longitude,condition\n'
        'BAD-001,Bad Asset,Bridge,abc,def,good\n'
    )
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'bad.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'Invalid coordinates' in response.data


def test_upload_invalid_condition(client, db):
    csv_data = (
        'asset_id,name,asset_type,latitude,longitude,condition\n'
        'BAD-002,Bad Asset,Bridge,56.0,-3.0,excellent\n'
    )
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'bad.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'Invalid condition' in response.data


def test_upload_missing_required_fields(client, db):
    csv_data = (
        'asset_id,name,asset_type,latitude,longitude,condition\n'
        ',Missing ID,Bridge,56.0,-3.0,good\n'
    )
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'bad.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'asset_id and name are required' in response.data


def test_upload_invalid_date(client, db):
    csv_data = (
        'asset_id,name,asset_type,latitude,longitude,condition,last_inspected\n'
        'DT-001,Date Test,Bridge,56.0,-3.0,good,not-a-date\n'
    )
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'bad.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'Invalid date format' in response.data


def test_upload_outside_scotland_warning(client, db):
    csv_data = (
        'asset_id,name,asset_type,latitude,longitude,condition\n'
        'OUT-001,Outside Asset,Bridge,51.5,-0.1,good\n'
    )
    data = {
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'assets.csv'),
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert b'outside Scotland bounds' in response.data
    # Asset should still be imported
    assert Asset.query.count() == 1


def test_api_assets_all(client, db):
    # Upload some data first
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    client.post('/upload', data=data, content_type='multipart/form-data')

    response = client.get('/api/assets')
    assert response.status_code == 200
    assets = json.loads(response.data)
    assert len(assets) == 3


def test_api_assets_filter_condition(client, db):
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    client.post('/upload', data=data, content_type='multipart/form-data')

    response = client.get('/api/assets?condition=good')
    assets = json.loads(response.data)
    assert len(assets) == 1
    assert assets[0]['condition'] == 'good'


def test_api_assets_filter_type(client, db):
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    client.post('/upload', data=data, content_type='multipart/form-data')

    response = client.get('/api/assets?asset_type=Bridge')
    assets = json.loads(response.data)
    assert len(assets) == 1
    assert assets[0]['asset_type'] == 'Bridge'


def test_api_assets_search(client, db):
    data = {
        'file': (io.BytesIO(SAMPLE_CSV.encode('utf-8')), 'assets.csv'),
    }
    client.post('/upload', data=data, content_type='multipart/form-data')

    response = client.get('/api/assets?search=forth')
    assets = json.loads(response.data)
    assert len(assets) == 1
    assert 'Forth' in assets[0]['name']


def test_api_assets_empty(client):
    response = client.get('/api/assets')
    assets = json.loads(response.data)
    assert assets == []


def test_404(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404


def test_upload_no_file(client):
    response = client.post('/upload', data={}, content_type='multipart/form-data')
    assert response.status_code == 200  # Re-renders form with errors
