from Flask_Try_On.test import conftest

# 정상적인 이미지 확인
def test_tryon(client, clothes_image, human_image1): 
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
    clothes_filename = json['filename']
    assert response.status_code == 200
    assert json['msg'] == "Success"

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

    human_filename = json['filename']

    assert response.status_code == 200
    assert json['msg'] == "Success"

    response = client.get(
        '/result' + '?c=' + clothes_filename + '&h=' + human_filename
    )
    
    assert response.status_code == 200



# 파일명 명시하지 않음
def test_tryon_fail(client): 

    response = client.get(
        '/result'
    )
    
    assert response.status_code == 200