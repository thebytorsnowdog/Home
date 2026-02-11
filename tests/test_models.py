from datetime import date
from models import Asset


def test_asset_creation(app, db):
    asset = Asset(
        asset_id='BR-001',
        name='Test Bridge',
        asset_type='Bridge',
        latitude=56.0,
        longitude=-3.4,
        condition='good',
        last_inspected=date(2024, 1, 15),
    )
    db.session.add(asset)
    db.session.commit()

    result = Asset.query.first()
    assert result.asset_id == 'BR-001'
    assert result.name == 'Test Bridge'
    assert result.condition == 'good'


def test_to_dict(app, db):
    asset = Asset(
        asset_id='BR-001',
        name='Test Bridge',
        asset_type='Bridge',
        latitude=56.0,
        longitude=-3.4,
        condition='good',
        last_inspected=date(2024, 1, 15),
    )
    db.session.add(asset)
    db.session.commit()

    d = asset.to_dict()
    assert d['asset_id'] == 'BR-001'
    assert d['latitude'] == 56.0
    assert d['last_inspected'] == '2024-01-15'


def test_to_dict_no_inspection_date(app, db):
    asset = Asset(
        asset_id='BR-002',
        name='Test Bridge 2',
        asset_type='Bridge',
        latitude=56.0,
        longitude=-3.4,
        condition='moderate',
    )
    db.session.add(asset)
    db.session.commit()

    d = asset.to_dict()
    assert d['last_inspected'] is None


def test_validate_coordinates_inside_scotland():
    assert Asset.validate_coordinates(56.49, -4.2) is True


def test_validate_coordinates_outside_scotland():
    assert Asset.validate_coordinates(51.5, -0.1) is False  # London


def test_unique_asset_id(app, db):
    a1 = Asset(asset_id='X-001', name='A', asset_type='Bridge', latitude=56.0, longitude=-3.0, condition='good')
    db.session.add(a1)
    db.session.commit()

    a2 = Asset(asset_id='X-001', name='B', asset_type='Road', latitude=57.0, longitude=-4.0, condition='poor')
    db.session.add(a2)
    import sqlalchemy
    import pytest
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()


def test_repr(app, db):
    asset = Asset(asset_id='BR-001', name='Test', asset_type='Bridge', latitude=56.0, longitude=-3.4, condition='good')
    assert 'BR-001' in repr(asset)
