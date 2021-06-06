from Flask_Try_On.test import conftest

# 정상적인 이미지 확인
def test_human_post(client, human_image1):
    data = {
        'image':human_image1
    }
    headers = {'content_type': 'multipart/form-data'}
    response = client.post(
        '/human',
        data = data,
        headers = headers
    )
    
    json = response.get_json()
    
    assert response.status_code == 200
    assert json['msg'] == "Success"

# 이미지가 아닌 잘못된 데이터 전송
def test_human_post_NotImage(client):
    data = {
        'image' : 'None'
    }
    response = client.post(
        '/human',
        data = data
    )

    json = response.get_json()

    assert response.status_code == 200
    assert json['msg'] == "Fail"

# 사람이 없는 이미지 데이터 전송
def test_human_post_NotHuman(client, clothes_image2):
    data = {
        'image' : clothes_image2
    }
    response = client.post(
        '/human',
        data = data
    )

    json = response.get_json()

    assert response.status_code == 200
    assert json['msg'] == "Fail"

def test_human_delete(client, human_image1):
    data = {
        'image':human_image1
    }
    headers = {'content_type': 'multipart/form-data'}
    response = client.post(
        '/human',
        data = data,
        headers = headers
    )

    json = response.get_json()
    
    assert response.status_code == 200
    assert json['msg'] == "Success"
    filename = json['filename']

    response = client.delete('/human/' + filename)
    json = response.get_json()

    assert response.status_code == 200
    assert json['msg'] == "Delete"

def test_clothes_delete_None(client):
    response = client.delete('/human/None')

    assert response.status_code == 200
    json = response.get_json()
    
    assert json['msg'] == "Delete"