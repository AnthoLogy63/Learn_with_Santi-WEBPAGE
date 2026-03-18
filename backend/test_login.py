import requests

# URL real del render (basado en ALLOWED_HOSTS)
url = 'https://learn-with-santi-webp-age.onrender.com/api/users/login/'
data = {
    'username': 'PEOPLEADMIN',
    'dni': 'admin123'
}

print(f"Probando login en: {url}")
print(f"Datos: {data}")

try:
    response = requests.post(url, json=data)
    print(f'Status Code: {response.status_code}')
    print(f'Response Body: {response.text}')
except Exception as e:
    print(f'Error: {e}')
