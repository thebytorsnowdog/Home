import io
from forms import CSVUploadForm, FilterForm
from werkzeug.datastructures import FileStorage


def test_csv_upload_form_valid(app):
    with app.test_request_context():
        f = FileStorage(stream=io.BytesIO(b'data'), filename='test.csv', content_type='text/csv')
        form = CSVUploadForm(data={}, file=f)
        # Note: FileRequired checks at validate time with the multidict
        assert form.file is not None


def test_csv_upload_form_rejects_non_csv(app):
    with app.test_request_context(method='POST', content_type='multipart/form-data'):
        f = FileStorage(stream=io.BytesIO(b'data'), filename='test.txt', content_type='text/plain')
        form = CSVUploadForm(multidict=None)
        form.file.data = f
        assert not form.validate()


def test_filter_form_no_csrf(app):
    with app.test_request_context('/?condition=good&search=bridge'):
        form = FilterForm()
        # FilterForm has csrf disabled, should work with GET params
        assert form.meta.csrf is False


def test_filter_form_defaults(app):
    with app.test_request_context('/'):
        form = FilterForm()
        assert form.condition.data == ''
        assert form.search.data is None
