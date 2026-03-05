import requests

with open('app.py', 'rb') as f:
    r = requests.post('http://127.0.0.1:5000/scanner', files={'file': ('app.py', f)})
    print(r.status_code)
