from app import app
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'test'

    with open('static/test.jpg', 'wb') as f:
        f.write(b'test image data')

    data = {
        'file': (open('static/test.jpg', 'rb'), 'test.jpg')
    }
    response = client.post('/scanner', data=data, content_type='multipart/form-data', headers={'Accept': 'application/json'})
    print("Status:", response.status_code)
    print("Response Body:", response.data.decode('utf-8'))
