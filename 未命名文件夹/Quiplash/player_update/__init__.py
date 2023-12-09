import json
import config

import azure.functions as func
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
db = client.get_database_client('quiplash')
player = db.get_container_client('player')


def main(req: func.HttpRequest) -> func.HttpResponse:

    username = req.get_json().get('username')
    password = req.get_json().get('password')

    if username:
        resp = list(player.query_items(query='select * from player where player.username = @username',
                                       parameters=[{'name': '@username', 'value': username}],
                                       enable_cross_partition_query=True))
        if not resp:
            return func.HttpResponse(json.dumps({'result': False, 'msg': 'Player does not exist'}))
        else:
            try:
                add_to_games_played = int(req.get_json().get('add_to_games_played'))
                add_to_score = int(req.get_json().get('add_to_score'))
                newGamePlayed = add_to_games_played + resp[0].get('games_played')
                resp[0]['games_played'] = newGamePlayed
                newScore = add_to_score + resp[0].get('total_score')
                resp[0]['total_score'] = newScore
                player.upsert_item(body=resp[0])
                return func.HttpResponse(json.dumps({'result' : True, 'msg': 'OK' }))
            except Exception:
                return func.HttpResponse(json.dumps({'result': False, 'msg': 'Invalid integer input'}))
    else:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Player does not exist'}))
