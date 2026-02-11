import io
import pytest
from app import app as flask_app
from models import db as _db


@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


SAMPLE_CSV = (
    'asset_id,name,asset_type,latitude,longitude,condition,last_inspected\n'
    'BR-001,Forth Road Bridge,Bridge,56.0005,-3.4053,good,2024-01-15\n'
    'RD-042,A9 Highland Section,Road,57.4778,-4.2247,moderate,2024-03-20\n'
    'PP-010,Inverness Pump Station,Pump Station,57.4819,-4.2244,poor,2023-11-01\n'
)

SAMPLE_CSV_MINIMAL = (
    'asset_id,name,asset_type,latitude,longitude,condition\n'
    'TEST-001,Test Asset,Bridge,56.0,-4.0,good\n'
)


@pytest.fixture
def sample_csv():
    return SAMPLE_CSV


@pytest.fixture
def sample_csv_file(sample_csv):
    return (io.BytesIO(sample_csv.encode('utf-8')), 'assets.csv')
