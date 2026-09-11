import requests

class Auth0Client:
    def __init__(self, domain, client_id, client_secret, audience):
        self.url = f"https://{domain}/oauth/token"
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self._token = None

    def get_token(self):
        """Obtiene un Access Token usando Client Credentials Grant"""
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': self.audience,
            'grant_type': 'client_credentials'
        }
        headers = {'content-type': "application/json"}
        
        response = requests.post(self.url, json=payload, headers=headers)
        
        if response.status_code == 200:
            self._token = response.json().get("access_token")
            return self._token
        else:
            raise Exception(f"Error obteniendo token: {response.text}")

# --- USO DEL SCRIPT ---

DOMAIN = "tu-dominio.auth0.com"
CLIENT_ID = "TU_CLIENT_ID" #Machine to Machine Application
CLIENT_SECRET = "TU_CLIENT_SECRET"
AUDIENCE = "tu audiencia de API"

auth = Auth0Client(DOMAIN, CLIENT_ID, CLIENT_SECRET, AUDIENCE)
token = auth.get_token()

# Ahora haces la petición a tu API de FastAPI
api_url = "tu URL de API protegida"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(api_url, headers=headers)
print(response.json())