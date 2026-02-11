from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

SCOTLAND_BOUNDS = {
    'lat_min': 54.5,
    'lat_max': 61.0,
    'lon_min': -8.0,
    'lon_max': -0.7,
}


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    asset_type = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    last_inspected = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    VALID_CONDITIONS = ('good', 'moderate', 'poor')

    def to_dict(self):
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'asset_type': self.asset_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'condition': self.condition,
            'last_inspected': self.last_inspected.isoformat() if self.last_inspected else None,
        }

    @staticmethod
    def validate_coordinates(lat, lon):
        """Return True if coordinates are within Scotland bounding box."""
        return (
            SCOTLAND_BOUNDS['lat_min'] <= lat <= SCOTLAND_BOUNDS['lat_max']
            and SCOTLAND_BOUNDS['lon_min'] <= lon <= SCOTLAND_BOUNDS['lon_max']
        )

    def __repr__(self):
        return f'<Asset {self.asset_id}: {self.name}>'
