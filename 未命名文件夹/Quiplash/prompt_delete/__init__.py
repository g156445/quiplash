import json
import config
import uuid

import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client


HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
db = client.get_database_client('quiplash')
players = db.get_container_client('player')
prompts = db.get_container_client('prompt')


def main(req: func.HttpRequest) -> func.HttpResponse:
    player = req.get_json().get('player')
    word = req.get_json().get('word')

    query = "SELECT * FROM prompt"
    if player:
        items = list(prompts.query_items(query, partition_key=player))
        if len(items) == 0:
            return func.HttpResponse(json.dumps({'msg': 'no change in the collection', 'result': True}))
        for item in items:
            prompts.delete_item(item, partition_key=player)
        return func.HttpResponse(json.dumps({'msg': f'{len(items)} prompts deleted', 'result': True}))

    if word:
        count = 0
        items = list(prompts.query_items(
            query, enable_cross_partition_query=True))
        for item in items:
            for text_per in item['texts']:
                if text_per['language'] == 'en':
                    words = text_per['text'].split()
                    for w in words:
                        if w == word:
                            count = count + 1
                            prompts.delete_item(item,partition_key=items['username'])

        if count == 0:
            return func.HttpResponse(json.dumps({'msg': 'no change in the collection', 'result': True}))
        else:
            return func.HttpResponse(json.dumps({'msg': f'{count} prompts deleted', 'result': True}))
