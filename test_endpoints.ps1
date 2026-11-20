& "C:\Users\kingez\Desktop\ice_project\env\Scripts\python.exe" -c "
import sys
sys.path.insert(0, '..')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=True)

# Test public key
print('=== Test GET /give/public-key ===')
resp = client.get('/give/public-key')
print(f'Status: {resp.status_code}')
print(f'Body: {resp.json()}')
print()

# Test donations list
print('=== Test GET /donations/ ===')
resp = client.get('/donations/')
print(f'Status: {resp.status_code}')
body = resp.json()
print(f'Body count: {len(body) if isinstance(body, list) else body}')
print()

# Test auth routes
print('=== Test POST /auth/register ===')
resp = client.post('/auth/register', json={'username': 'testadmin', 'password': 'testpass123'})
print(f'Status: {resp.status_code}')
print(f'Body: {resp.json()}')
print()

print('=== Test POST /auth/login ===')
resp = client.post('/auth/login', data={'username': 'testadmin', 'password': 'testpass123'})
print(f'Status: {resp.status_code}')
print(f'Body: {resp.json()}')
"