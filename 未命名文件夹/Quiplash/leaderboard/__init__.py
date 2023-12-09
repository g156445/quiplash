import json
import config

import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client


HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
db = client.get_database_client('quiplash')
player = db.get_container_client('player')
prompt = db.get_container_client('prompt')


def main(req: func.HttpRequest) -> func.HttpResponse:
    top = req.get_json().get('top')
    players = list(player.query_items(
        f'select top {top} * from player order by player.total_score desc,player.games_played,player.username', enable_cross_partition_query=True))
    return func.HttpResponse(json.dumps([{"username": player['username'], "games_played": player['games_played'], "total_score": player['total_score']} for player in players]))
