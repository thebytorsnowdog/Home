# Scotland Asset Map

A Flask web application to visualize infrastructure asset status across Scotland on an interactive Leaflet map. Upload CSV files with asset data, which are stored in SQLite and displayed as color-coded markers with filtering capabilities.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000

## Usage

1. **Upload**: Go to `/upload` and upload a CSV file with asset data
2. **View**: The dashboard at `/` shows all assets on an interactive map
3. **Filter**: Use the sidebar to filter by condition, asset type, or search by name/ID

## CSV Format

| asset_id | name              | asset_type | latitude | longitude | condition | last_inspected |
|----------|-------------------|------------|----------|-----------|-----------|----------------|
| BR-001   | Forth Road Bridge | Bridge     | 56.0005  | -3.4053   | good      | 2024-01-15     |

- **condition**: `good`, `moderate`, or `poor`
- **last_inspected**: `YYYY-MM-DD` format (optional)

## Running Tests

```bash
pytest --cov=. --cov-report=term-missing tests/
```

## API

- `GET /api/assets` - Returns all assets as JSON
  - Query params: `condition`, `asset_type`, `search`
