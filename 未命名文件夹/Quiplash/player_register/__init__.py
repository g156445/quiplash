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

def main(req: func.HttpRequest) -> func.HttpResponse:
    pwd = req.get_json().get('password')
    name = req.get_json().get('username')

    if (not name or len(name) < 4 or len(name) > 14):
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Username less than 4 characters or more than 14 characters'}))
    if (not pwd or len(pwd) < 10 or len(pwd) > 20):
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Password less than 10 characters or more than 20 characters'}))

    resp = player.query_items(query='select * from player where player.username = @username',
                              parameters=[{'name': '@username', 'value': name}],
                              enable_cross_partition_query=True)

    if list(resp):
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Username already exists'}))
    else:
        player.create_item(
            body={'id':str(uuid.uuid4()),'username': name, 'password': pwd, 'games_played': 0, 'total_score': 0})
        return func.HttpResponse(json.dumps({'result': True, 'msg': 'OK'}))
