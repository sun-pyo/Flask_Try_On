from werkzeug.datastructures import FileStorage
from Flask_Try_On.flaskapp import app
import pytest

@pytest.fixture
def client():
    return app.test_client(app)

@pytest.fixture
def clothes_image():
    filename = 'c1.png'
    fileobj = open('Flask_Try_On/test/'+filename, 'rb')
    return FileStorage(stream=fileobj, filename=filename, content_type="image")

@pytest.fixture
def human_image1():
    filename = 'h1.png'
    fileobj = open('Flask_Try_On/test/'+filename, 'rb')
    return FileStorage(stream=fileobj, filename=filename, content_type="image")