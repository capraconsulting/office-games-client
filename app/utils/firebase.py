from pyrebase import pyrebase

from app.settings import (FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
                          FIREBASE_AUTH_URI, FIREBASE_CLIENT_EMAIL, FIREBASE_CLIENT_ID, FIREBASE_CLIENT_X509_CERT_URL,
                          FIREBASE_DATABASE_URL, FIREBASE_PRIVATE_KEY, FIREBASE_PRIVATE_KEY_ID, FIREBASE_STORAGE_BUCKET,
                          FIREBASE_TOKEN_URI, FIREBASE_TYPE)


def get_firebase():
    return pyrebase.initialize_app({
        'apiKey': FIREBASE_API_KEY,
        'databaseURL': FIREBASE_DATABASE_URL,
        'storageBucket': FIREBASE_STORAGE_BUCKET,
        'authDomain': FIREBASE_AUTH_DOMAIN,
        'serviceAccount': {
            'type': FIREBASE_TYPE,
            'private_key_id': FIREBASE_PRIVATE_KEY_ID,
            'private_key': FIREBASE_PRIVATE_KEY.replace('\\n', '\n'),
            'client_email': FIREBASE_CLIENT_EMAIL,
            'client_id': FIREBASE_CLIENT_ID,
            'auth_uri': FIREBASE_AUTH_URI,
            'token_uri': FIREBASE_TOKEN_URI,
            'auth_provider_x509_cert_url': FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            'client_x509_cert_url': FIREBASE_CLIENT_X509_CERT_URL
        }
    })
