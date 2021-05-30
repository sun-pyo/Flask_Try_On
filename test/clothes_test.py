from . import conftest

# 정상적인 이미지 확인
def test_clothes_post(client, clothes_image):
    data = {
        'image':clothes_image
    }
    headers = {'content_type': 'multipart/form-data'}
    response = client.post(
        '/clothes',
        data = data,
        headers = headers
    )
    
    json = response.get_json()
    
    assert response.status == 200
    assert json['msg'] == "Success"

# 잘못된 데이터 전송
def test_clothes_post_None(client):
    data = None
    response = client.post(
        '/clothes',
        data = data
    )

    json = response.get_json()

    assert response.status == 200
    assert json['msg'] == "Fail"

def test_clothes_delete(client, clothes_image):
    data = {
        'image':clothes_image
    }
    headers = {'content_type': 'multipart/form-data'}
    response = client.post(
        '/clothes',
        data = data,
        headers = headers
    )

    json = response.get_json()
    
    assert response.status == 200
    assert json['msg'] == "Success"


    response = client.delete('/clothes/img_c0')
    json = response.get_json()

    assert response.status == 200
    assert json['msg'] == "Delete"

def test_clothes_delete_None(client):
    response = client.delete('/clothes/None')

    assert response.status == 200
    json = response.get_json()
    
    assert json['msg'] == "Delete"
