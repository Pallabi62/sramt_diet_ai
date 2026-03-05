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
    response = client.post('/scanner', data=data, content_type='multipart/form-data')
    print(response.status_code)
    html = response.data.decode('utf-8')
    import re
    img_src = re.search(r'<img src="([^"]+)" alt="Uploaded Food"', html)
    if img_src:
        url = img_src.group(1)
        print("Found URL:", url)
        img_resp = client.get(url)
        print("Image fetch status:", img_resp.status_code)
    else:
        print("Image tag not found")
