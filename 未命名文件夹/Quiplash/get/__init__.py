import json
import config
import uuid

import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client


HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
db = client.get_database_client('quiplash')
player = db.get_container_client('player')
prompt = db.get_container_client('prompt')


def main(req: func.HttpRequest) -> func.HttpResponse:
    players = req.get_json().get('players')
    language = req.get_json().get('language')

    query = 'select * from prompt where prompt.username in (' + ', '.join(
        ['"' + player + '"' for player in players]) + ')'
    items = list(prompt.query_items(query, enable_cross_partition_query=True))
    if len(items) == 0:
        return func.HttpResponse(json.dumps([]))
    res = []
    for item in items:
        for text_per in item['texts']:
            if text_per['language'] == language:
                res.append(
                    {"id": item['id'], "text": text_per['text'], "username": item['username']})
    return func.HttpResponse(json.dumps(res))
