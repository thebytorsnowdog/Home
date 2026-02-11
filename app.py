import csv
import io
import os
from datetime import date, datetime, timezone

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from forms import CSVUploadForm, FilterForm
from models import Asset, db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///assets.db')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_csv(file_storage):
    """Parse uploaded CSV and return (assets_list, errors_list)."""
    stream = io.StringIO(file_storage.read().decode('utf-8-sig'))
    reader = csv.DictReader(stream)

    required = {'asset_id', 'name', 'asset_type', 'latitude', 'longitude', 'condition'}
    if not required.issubset(set(reader.fieldnames or [])):
        missing = required - set(reader.fieldnames or [])
        return [], [f'Missing required columns: {", ".join(sorted(missing))}']

    assets = []
    errors = []
    for i, row in enumerate(reader, start=2):
        try:
            lat = float(row['latitude'])
            lon = float(row['longitude'])
        except (ValueError, TypeError):
            errors.append(f'Row {i}: Invalid coordinates')
            continue

        condition = row['condition'].strip().lower()
        if condition not in Asset.VALID_CONDITIONS:
            errors.append(f'Row {i}: Invalid condition "{row["condition"]}"')
            continue

        if not row.get('asset_id', '').strip() or not row.get('name', '').strip():
            errors.append(f'Row {i}: asset_id and name are required')
            continue

        last_inspected = None
        if row.get('last_inspected', '').strip():
            try:
                last_inspected = date.fromisoformat(row['last_inspected'].strip())
            except ValueError:
                errors.append(f'Row {i}: Invalid date format for last_inspected')
                continue

        if not Asset.validate_coordinates(lat, lon):
            errors.append(f'Row {i}: Coordinates outside Scotland bounds (warning)')

        assets.append({
            'asset_id': row['asset_id'].strip(),
            'name': row['name'].strip(),
            'asset_type': row.get('asset_type', '').strip(),
            'latitude': lat,
            'longitude': lon,
            'condition': condition,
            'last_inspected': last_inspected,
        })

    return assets, errors


@app.route('/')
def dashboard():
    form = FilterForm(request.args)
    # Populate asset_type choices dynamically
    types = db.session.query(Asset.asset_type).distinct().order_by(Asset.asset_type).all()
    form.asset_type.choices = [('', 'All Types')] + [(t[0], t[0]) for t in types]
    return render_template('dashboard.html', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = CSVUploadForm()
    if form.validate_on_submit():
        assets_data, errors = parse_csv(form.file.data)

        if errors and not assets_data:
            for error in errors:
                flash(error, 'danger')
            return render_template('upload.html', form=form)

        count_new = 0
        count_updated = 0
        for data in assets_data:
            existing = Asset.query.filter_by(asset_id=data['asset_id']).first()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                count_updated += 1
            else:
                asset = Asset(**data)
                db.session.add(asset)
                count_new += 1

        db.session.commit()

        flash(f'Successfully imported {count_new} new and updated {count_updated} existing assets.', 'success')
        for error in errors:
            flash(error, 'warning')

        return redirect(url_for('dashboard'))

    return render_template('upload.html', form=form)


@app.route('/api/assets')
def api_assets():
    query = Asset.query

    condition = request.args.get('condition', '').strip()
    if condition:
        query = query.filter(Asset.condition == condition)

    asset_type = request.args.get('asset_type', '').strip()
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    search = request.args.get('search', '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Asset.name.ilike(like),
                Asset.asset_id.ilike(like),
            )
        )

    assets = query.all()
    return jsonify([a.to_dict() for a in assets])


@app.errorhandler(404)
def not_found(e):
    return render_template('base.html', content='<h2>Page not found</h2>'), 404


@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'danger')
    return redirect(url_for('upload'))


@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', content='<h2>Internal server error</h2>'), 500


if __name__ == '__main__':
    app.run(debug=True)
