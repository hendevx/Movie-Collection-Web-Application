import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from time import sleep

def fetch_movies(page=1, retries=3):
    """Fetch movies from the external API with retries."""
    url = f'{settings.EXTERNAL_API_URL}?page={page}'
    
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(settings.EXTERNAL_API_USERNAME, settings.EXTERNAL_API_PASSWORD),
                verify=False
            )

            response.raise_for_status()
            data = response.json()
            results = data.get('results', [])

            if not isinstance(results, list):
                raise ValueError("'results' key should be a list")
            
            return {
                'count': data.get('count', 0),
                'next': data.get('next', None),
                'previous': data.get('previous', None),
                'data': results
            }
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            sleep(2)
        except ValueError as e:
            print(f"Data format error: {e}")
            return None
    
    return None