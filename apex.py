import requests
import json
import config


def req(x, y=None):
    return requests.get(f'https://api.mozambiquehe.re/{x}?{y}&auth={config.ApexToken}').json() if y else requests.get(f'https://api.mozambiquehe.re/{x}?auth={config.ApexToken}').json()

def alplayer(player, platform):
    return requests.get(f'https://api.mozambiquehe.re/bridge?auth={config.BotToken}&player={player}&platform={platform}').json()


