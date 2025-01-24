from django.core.exceptions import ValidationError
import requests
from typing import Dict, Any
from django.conf import settings

GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'


def google_get_access_token(code: str, redirect_uri: str) -> str:
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)
    if not response.ok:
        raise ValidationError('Could not get access token from Google.')

    return response.json().get('access_token')


def google_get_user_info(access_token: str) -> Dict[str, Any]:
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )

    if not response.ok:
        raise ValidationError('Could not get user info from Google.')

    return response.json()


def get_user_data(validated_data):
    code = validated_data.get('code')
    redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI

    # Получаем access token
    access_token = google_get_access_token(code, redirect_uri)

    # Получаем данные пользователя из Google
    user_info = google_get_user_info(access_token)

    return user_info
