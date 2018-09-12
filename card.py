#coding=UTF-8

class Card:

    # Takes in strings of the format: "As", "Tc", "6d"
    def __init__(self, card_string):
        #print card_string
        self.suit_value_dict = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9}
        self.suit_index_dict = {"S": 0, "C": 1, "H": 2, "D": 3}
        self.val_string = "AKQJT98765432"
        value, self.suit = card_string[0], card_string[1]
        self.value = self.suit_value_dict[value]
        self.suit_index = self.suit_index_dict[self.suit]

    def __str__(self):
        return self.val_string[14 - self.value] + self.suit

    def toString(self):
        return self.val_string[14 - self.value] + self.suit

    def __repr__(self):
        return self.val_string[14 - self.value] + self.suit

    def __eq__(self, other):
        if self is None:
            return other is None
        elif other is None:
            return False
        return self.value == other.value and self.suit == other.suit

    def __hash__(self):
        return hash(self.value.__hash__()+self.suit.__hash__())

    def score(self):
        if 2 == self.suit_index:
            return 1
        elif 0 == self.suit_index and 12 == self.value:
            return 13
        else:
            return 0

    def scoreMultiple(self):
        if 1 == self.suit_index and 10 == self.value:
            return 2
        else:
            return 1

    def cardIndex(self):
        return self.suit_index*13+self.value-2

    @classmethod
    def getCard(cls, suit, value):
        suitDict = {0:"S", 1:"C", 2:"H", 3:"D"}
        valueDict = {2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"T", 11:"J", 12:"Q", 13:"K", 14:"A"}
        return Card(valueDict[value]+suitDict[suit])