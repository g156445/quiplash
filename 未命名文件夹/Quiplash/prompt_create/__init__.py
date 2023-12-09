import azure.functions as func
import azure.functions as func
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import requests
import uuid
import json
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']

client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
db = client.get_database_client('quiplash')
player = db.get_container_client('player')
prompt = db.get_container_client('prompt')
key = config.settings['translate_key']
endpoint = config.settings['translate_endpoint']
location = config.settings['translate_localtion']

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}
support_language = config.settings['language_supported']

def main(req: func.HttpRequest) -> func.HttpResponse:
    text = req.get_json().get('text')
    username = req.get_json().get('username')
    if not username:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Player does not exist'}))
    if not text or len(text) > 80 or len(text) < 15:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Prompt less than 15 characters or more than 80 characters'}))
    resp = list(player.query_items(query='select * from player where player.username = @username',
                                   parameters=[
                                       {'name': '@username', 'value': username}],
                                   enable_cross_partition_query=True))
    if not resp:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Player does not exist'}))

    # 检测语言
    request = requests.post(endpoint + '/detect?api-version=3.0', headers=headers, json=[{'text': text}])
    response = request.json()
    if response[0]['score'] < 0.3 or response[0]['language'] not in support_language:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Unsupported language'}))
    
    # 翻译数据
    translate_url = endpoint + '/translate?api-version=3.0&from=' + response[0]['language']

    for lan in support_language:
        if lan != response[0]['language']:
            translate_url += f'&to={lan}'
    request = requests.post(translate_url, headers=headers, json=[{'text':text}])
    translations = request.json()[0]['translations']
    texts = [{'language':response[0]['language'],'text':text}]
    for translation in translations:
        texts.append({'language':translation['to'],'text':translation['text']})
    # 插入数据
    prompt.create_item(
        body={'id': str(uuid.uuid4()), 'username': username, 'texts': texts})
    return func.HttpResponse(json.dumps({'result': True, 'msg': 'OK'}))
