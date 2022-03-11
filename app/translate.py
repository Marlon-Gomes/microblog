# Imports from standard libraries
import json, requests
# Imports from downloaded libraries
from flask import current_app
from flask_babel import _
# Imports from local libraries

def translate(text, source_language, dest_language):
    # Verify system is configured and authentication key is stored
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
        not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured.')
    # Authentication
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'eastus'
    }
    # Requests.post() returns a response object in .json format
    response = requests.post(
        'https://api.cognitive.microsofttranslator.com/'
        'translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language),
        headers = auth,
        json=[{'Text': text}]
    )
    # Successful requests return status code 200
    if response.status_code != 200:
        return _('Error: the translation service failed.')
    # use .json() to convert from .json to python string
    return response.json()[0]['translations'][0]['text']
