#coding=UTF-8

import sys
import os
import json
from card import Card

def processOneGame(strData):
    data = json.loads(strData)
    events = data['events']

    for e in events:
        if 'new_deal' == e['eventName']:
            pass
        elif 'pass_cards' == e['eventName']:
            pass
        elif 'receive_opponent_cards' == e['eventName']:
            pass
        elif 'expose_cards' == e['eventName']:
            pass
        elif 'expose_cards_end' == e['eventName']:
            pass
        elif 'your_turn' == e['eventName']:
            pass
        elif 'turn_end' == e['eventName']:
            pass
        elif 'round_end' == e['eventName']:
            pass
        elif 'deal_end' == e['eventName']:
            players = e['data']['players']
            for p in players:
                feature = ['0' for i in xrange(52+1)]
                for c in p['initialCards']:
                    feature[Card(c).cardIndex()] = '1'
                if p['shootingTheMoon']:
                    feature[52] = '1'
                print ','.join(feature)
        elif 'game_end' == e['eventName']:
            pass

if __name__ == "__main__":
    argv_count = len(sys.argv)
    if argv_count > 1:
        dataPath = sys.argv[1]
        files = os.listdir(dataPath)
        for file in files:
            if not os.path.isdir(file):
                f = open(dataPath + "/" + file)
                iter_f = iter(f)
                str = ""
                for line in iter_f:
                    str = str + line
                processOneGame(str)