
import random

from heartsBot import HeartsBot
from card import Card

HAS_OUT = 5
UNKNOWN_OWNER = 0

class SearchPlayBot(HeartsBot):

    def __init__(self,name, logger):
        super(SearchPlayBot, self).__init__(name,logger)
        self.my_hand_cards = []
        self.expose_card = False
        self.my_pass_card = []
        self.system_log = logger
        self.allCards = [[UNKNOWN_OWNER for col in range(13)] for row in range(4)]
        self.playerIndex = {}
        self.emptyColor = {}
        self.candidateCount = 13
        self.selfScore = 0

    def receive_cards(self,data):
        self.my_hand_cards = self.get_cards(data)

        self.playerIndex = {}
        idx = 0
        for p in data['players']:
            if p['playerName'] == self.player_name or idx > 0:
                idx += 1
                self.playerIndex[p['playerName']] = idx
        for p in data['players']:
            if p['playerName'] == self.player_name:
                break
            idx += 1
            self.playerIndex[p['playerName']] = idx

        self.allCards = [[UNKNOWN_OWNER for col in range(13)] for row in range(4)]
        for c in self.my_hand_cards:
            self.allCards[c.suit_index][c.value-2] = self.playerIndex[self.player_name]

        self.emptyColor = {}
        self.candidateCount = 13
        self.selfScore = 0

    def pass_cards(self,data):
        receiver = data['receiver']

        cards = data['self']['cards']
        self.my_hand_cards = []
        for card_str in cards:
            card = Card(card_str)
            self.my_hand_cards.append(card)
        pass_cards=[]
        count=0
        for i in range(len(self.my_hand_cards)):
            card=self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
            if card==Card("QS"):
                pass_cards.append(card)
                count+=1
            elif card==Card("TC"):
                pass_cards.append(card)
                count += 1
        for i in range(len(self.my_hand_cards)):
            card = self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
            if card.suit_index==2:
                pass_cards.append(card)
                count += 1
                if count ==3:
                    break
        if count <3:
            for i in range(len(self.my_hand_cards)):
                card = self.my_hand_cards[len(self.my_hand_cards) - (i + 1)]
                if card not in self.game_score_cards:
                    pass_cards.append(card)
                    count += 1
                    if count ==3:
                        break
        return_values=[]
        for card in pass_cards:
            return_values.append(card.toString())
            self.allCards[card.suit_index][card.value-2] = self.playerIndex[receiver]

        message="Pass Cards:{}".format(return_values)
        self.system_log.show_message(message)
        self.system_log.save_logs(message)
        self.my_pass_card=return_values
        return return_values

    def pick_card(self,data):
        cadidate_cards=data['self']['candidateCards']
        cards = data['self']['cards']
        self.my_hand_cards = []
        for card_str in cards:
            card = Card(card_str)
            self.my_hand_cards.append(card)
        '''message = "My Cards:{}".format(self.my_hand_cards)
        self.system_log.show_message(message)
        card_index=0
        message = "Pick Card Event Content:{}".format(data)
        self.system_log.show_message(message)
        message = "Candidate Cards:{}".format(cadidate_cards)
        self.system_log.show_message(message)
        self.system_log.save_logs(message)
        message = "Pick Card:{}".format(cadidate_cards[card_index])
        self.system_log.show_message(message)
        self.system_log.save_logs(message)'''

        roundPlayers = data['roundPlayers']
        players = data['players']
        playersDict = {}
        previousCards = []
        for player in players:
            playersDict[player['playerName']] = player
        for i in xrange(len(roundPlayers)):
            p = roundPlayers[i]
            if '' != playersDict[p]['roundCard']:
                card = Card(playersDict[p]['roundCard'])
                previousCards.append(card)

                self.allCards[card.suit_index][card.value - 2] = HAS_OUT

        for i in xrange(len(previousCards)):
            if 0 == i:
                continue
            if previousCards[i].suit_index != previousCards[0].suit_index:
                pn = self.playerIndex[roundPlayers[i]]
                if pn not in self.emptyColor:
                    self.emptyColor[pn] = {}
                if previousCards[0].suit_index not in self.emptyColor[pn]:
                    self.emptyColor[pn][previousCards[0].suit_index] = 0

        cadidate = []
        for c in cadidate_cards:
            cadidate.append(Card(c))

        self.candidateCount = len(cadidate)
        self.selfScore = -data['self']['dealScore']

        card_index = self.pickCard(cadidate, previousCards, self.shootMoonStatus(players))

        print cadidate_cards[card_index]

        return cadidate_cards[card_index]

    def expose_my_cards(self,yourcards):
        expose_card=[]
        for card in self.my_hand_cards:
            if card==Card("AH"):
                expose_card.append(card.toString())
        message = "Expose Cards:{}".format(expose_card)
        self.system_log.show_message(message)
        self.system_log.save_logs(message)
        return expose_card

    def expose_cards_end(self,data):
        players = data['players']
        expose_player=None
        expose_card=None
        for player in players:
            try:
                if player['exposedCards']!=[] and len(player['exposedCards'])>0 and player['exposedCards']!=None:
                    expose_player=player['playerName']
                    expose_card=player['exposedCards']
            except Exception, e:
                self.system_log.show_message(e.message)
                self.system_log.save_logs(e.message)
        if expose_player!=None and expose_card!=None:
            message="Player:{}, Expose card:{}".format(expose_player,expose_card)
            self.system_log.show_message(message)
            self.system_log.save_logs(message)
            self.expose_card=True

            for c in expose_card:
                card = Card(c)
                self.allCards[card.suit_index][card.value - 2] = self.playerIndex[expose_player]
        else:
            message="No player expose card!"
            self.system_log.show_message(message)
            self.system_log.save_logs(message)
            self.expose_card=False

    def receive_opponent_cards(self,data):
        self.my_hand_cards = self.get_cards(data)
        players = data['players']
        for player in players:
            player_name = player['playerName']
            if player_name == self.player_name:
                picked_cards = player['pickedCards']
                receive_cards = player['receivedCards']
                receivedFrom = player['receivedFrom']
                message = "User Name:{}, Picked Cards:{}, Receive Cards:{}".format(player_name, picked_cards,receive_cards)
                self.system_log.show_message(message)
                self.system_log.save_logs(message)

                for c in receive_cards:
                    card = Card(c)
                    self.allCards[card.suit_index][card.value - 2] = self.playerIndex[self.player_name]

    def round_end(self,data):
        try:
            round_scores=self.get_round_scores(self.expose_card, data)
            for key in round_scores.keys():
                message = "Player name:{}, Round score:{}".format(key, round_scores.get(key))
                self.system_log.show_message(message)
                self.system_log.save_logs(message)

            roundPlayers = data['roundPlayers']
            players = data['players']

            playersDict = {}
            previousCards = []
            for player in players:
                playersDict[player['playerName']] = player
            for i in xrange(len(roundPlayers)):
                p = roundPlayers[i]
                if '' != playersDict[p]['roundCard']:
                    card = Card(playersDict[p]['roundCard'])
                    previousCards.append(card)

                    self.allCards[card.suit_index][card.value - 2] = HAS_OUT

            for i in xrange(len(previousCards)):
                if 0 == i:
                    continue
                if previousCards[i].suit_index != previousCards[0].suit_index:
                    pn = self.playerIndex[roundPlayers[i]]
                    if pn not in self.emptyColor:
                        self.emptyColor[pn] = {}
                    if previousCards[0].suit_index not in self.emptyColor[pn]:
                        self.emptyColor[pn][previousCards[0].suit_index] = 0
        except Exception, e:
            self.system_log.show_message(e.message)

    def deal_end(self,data):
        self.my_hand_cards=[]
        self.expose_card = False
        deal_scores,initial_cards,receive_cards,picked_cards=self.get_deal_scores(data)
        message = "Player name:{}, Pass Cards:{}".format(self.player_name, self.my_pass_card)
        self.system_log.show_message(message)
        self.system_log.save_logs(message)
        for key in deal_scores.keys():
            message = "Player name:{}, Deal score:{}".format(key,deal_scores.get(key))
            self.system_log.show_message(message)
            self.system_log.save_logs(message)
        for key in initial_cards.keys():
            message = "Player name:{}, Initial cards:{}, Receive cards:{}, Picked cards:{}".format(key, initial_cards.get(key),receive_cards.get(key),picked_cards.get(key))
            self.system_log.show_message(message)
            self.system_log.save_logs(message)

    def game_over(self,data):
        game_scores = self.get_game_scores(data)
        for key in game_scores.keys():
            message = "Player name:{}, Game score:{}".format(key, game_scores.get(key))
            self.system_log.show_message(message)
            self.system_log.save_logs(message)

    def pick_history(self,data,is_timeout,pick_his):
        for key in pick_his.keys():
            message = "Player name:{}, Pick card:{}, Is timeout:{}".format(key,pick_his.get(key),is_timeout)
            self.system_log.show_message(message)
            self.system_log.save_logs(message)

    def shootMoonStatus(self, players):
        selfScore = 0
        otherScore = 0
        for p in players:
            sc = p['scoreCards']
            if len(sc) > 0:
                if 1 == len(sc) and 'TC' == sc[0]:
                    continue
                if p['playerName'] == self.player_name:
                    selfScore += 1
                else:
                    otherScore += 1
        if 0 == selfScore+otherScore:
            return 0
        elif selfScore+otherScore >= 2: # heart broken
            return 1
        elif otherScore > 0:
            return 2   # someone can shoot moon
        else:
            return 3   # I can shoot moon

    def canShootMoon(self):
        return False

    def pickCard(self, candidate, previous, shootStatus):
        shoot = self.canShootMoon()

        if 0 == shootStatus or 3 == shootStatus:
            if shoot:
                return self.pickCardShootMoon(candidate, previous)
            else:
                return self.pickCardEvadeScore(candidate, previous)
        elif 1 == shootStatus:  # heart broken
            return self.pickCardEvadeScore(candidate, previous)
        elif 2 == shootStatus:
            return self.pickCardBlockShootMoon(candidate, previous)

    def pickCardEvadeScore(self, candidate, previous):
        resIdx = 0
        gotOdds, averageScore = self.getOdds(previous+[candidate[0]], False)

        msg = "Expected score of :{} is {}".format(candidate[0], averageScore)
        self.system_log.save_logs(msg)

        for i in xrange(len(candidate)-1):
            idx = i+1
            odds, average = self.getOdds(previous+[candidate[idx]], False)

            msg = "Expected score of :{} is {}".format(candidate[idx], average)
            self.system_log.save_logs(msg)

            if average < averageScore or (average == averageScore and candidate[idx].value > candidate[resIdx].value):
                resIdx = idx
                averageScore = average

        return resIdx

    def pickCardBlockShootMoon(self, candidate, previous):
        resIdx = 0
        gotOdds, scoreOdds = self.getOdds(previous + [candidate[0]], True)

        for i in xrange(len(candidate) - 1):
            idx = i + 1
            o1, o2 = self.getOdds(previous + [candidate[idx]], True)
            if o2 > scoreOdds or (o2 == scoreOdds and candidate[idx].value < candidate[resIdx].value):
                resIdx = idx
                scoreOdds = o2
        return resIdx

    def pickCardShootMoon(self, candidate, previous):
        pass

    def getCardPosition(self, card):
        total = 0
        low = 0
        high = 0
        for i in xrange(13):
            c = self.allCards[card.suit_index][i]
            if self.playerIndex[self.player_name] == c or HAS_OUT == c:
                continue
            total += 1
            if i+2 < card.value:
                low += 1
            elif i+2 > card.value:
                high += 1
        return total, low, high

    def getVirtualCards(self, allCards, vPlayerCount):
        cardsOfPlayer = [[] for i in xrange(5)]
        for s in xrange(4):
            for v in xrange(13):
                if HAS_OUT != allCards[s][v]:
                    cardsOfPlayer[allCards[s][v]].append(Card.getCard(s, v+2))
        random.shuffle(cardsOfPlayer[UNKNOWN_OWNER])
        targetLen = len(cardsOfPlayer[1])
        baseIdx = 0
        for i in xrange(vPlayerCount):
            l = len(cardsOfPlayer[i+2])
            if l < targetLen:
                cardsOfPlayer[i + 2] += cardsOfPlayer[UNKNOWN_OWNER][baseIdx:baseIdx+(targetLen-l)]
                baseIdx += (targetLen-l)

        return cardsOfPlayer

    def virtualPickCard(self, suit, vCards, needScore, vPlayerCount):
        res = []
        for i in xrange(vPlayerCount):
            candidates = []
            for c in vCards[i+2]:
                if c.suit_index == suit:
                    candidates.append(c)
            if 0 == len(candidates):
                candidates = vCards[i+2]

            cc = candidates[0]
            for c in candidates:
                if suit == candidates[0].suit_index:
                    if c.value > cc.value and needScore:
                        cc = c
                    if c.value < cc.value and not needScore:
                        cc = c
                else:
                    if c.score() < cc.score() and needScore:
                        cc = c
                    if c.score() > cc.score() and not needScore:
                        cc = c
            res.append(cc)
        return res


    def simulateByMC(self, previousCards, needScore):
        times = 4000/self.candidateCount
        prevLen = len(previousCards)
        vPlayerCount = 4 - prevLen
        winScore = 0
        winCard = 0
        for i in xrange(times):
            vCards = self.getVirtualCards(self.allCards, vPlayerCount)
            vPickCards = self.virtualPickCard(previousCards[0].suit_index, vCards, needScore, vPlayerCount)
            if prevLen-1 == self.whoGotCards(previousCards+vPickCards):
                winCard += 1
                winScore += ((self.selfScore + self.howManyScores(previousCards+vPickCards)) * self.howManyMultiple(previousCards+vPickCards))
        return winCard*1.0/times, winScore*1.0/times

    def whoGotCards(self, cards):
        maxIdx = 0
        for i in xrange(len(cards)):
            if cards[i].suit_index == cards[0].suit_index and cards[i].value > cards[0].value:
                maxIdx = i
        return maxIdx

    def howManyScores(self, cards):
        res = 0
        for c in cards:
            res += c.score()
        return res

    def howManyMultiple(self, cards):
        res = 1
        for c in cards:
            res *= c.scoreMultiple()
        return res

    def getOdds(self, previousCards, needScore):
        prevLen = len(previousCards)
        if 4 == prevLen:
            if prevLen-1 == self.whoGotCards(previousCards):
                sc = (self.selfScore + self.howManyScores(previousCards)) * self.howManyMultiple(previousCards)
                return 1.0, sc
            else:
                return 0.0, 0.0
        else:
            return self.simulateByMC(previousCards, needScore)
