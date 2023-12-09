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
    pwd = req.get_json().get('password')
    name = req.get_json().get('username')
    if not pwd or not name:
        return func.HttpResponse(json.dumps({'result': False, 'msg': 'Username or password incorrect'}))
    else:
        resp = list(player.query_items(query='select * from player where player.username = @username',
                                  parameters=[{'name': '@username', 'value': name}],
                                  enable_cross_partition_query=True))
        if resp and resp[0].get('password') == pwd:
            return func.HttpResponse(json.dumps({'result': True, 'msg': 'OK'}))
        else:
            return func.HttpResponse(json.dumps({'result': False, 'msg': 'Username or password incorrect'}))
