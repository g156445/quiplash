import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://quiplash-11.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'qgIRndMciAEKLOg5QbJdi99Agf3sIXZinM8YK1ALouNCYIPXmsTAASObVT7kcVr8hJIDnMoQVrG2ACDb0Li3Jw=='),
    'translate_key':os.environ.get('TRANSLATE_KEY', '816922a59ab64d78a05288474313f4c1'),
    'translate_endpoint':os.environ.get('TRANSLATE_ENDPOINT', 'https://api.cognitive.microsofttranslator.com'),
    'translate_localtion':os.environ.get('TRANSLATE_LOCALTION', 'uksouth'),
    'language_supported':['en','es','it','sv','ru','id','bg','zh-Hans']
}