from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, StringField


class CSVUploadForm(FlaskForm):
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only.'),
    ])


class FilterForm(FlaskForm):
    class Meta:
        csrf = False

    condition = SelectField('Condition', choices=[
        ('', 'All Conditions'),
        ('good', 'Good'),
        ('moderate', 'Moderate'),
        ('poor', 'Poor'),
    ], default='')

    asset_type = SelectField('Asset Type', choices=[
        ('', 'All Types'),
    ], default='')

    search = StringField('Search')
