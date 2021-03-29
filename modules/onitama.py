"""
Importations
"""

import numpy as np
from copy import deepcopy
import random

"""
Constants
"""

Empty = 0
White = 1
Black = -1
WhiteK = 9
BlackK = -9
ref_values = [Empty, White, Black, WhiteK, BlackK]

Dx = 5
Dy = 5

"""
List of all cards
"""

cards = {"Hahn":[(-1,1),(0,1), (0,-1),(1,-1)],
"Krabbe":[(0,-2), (-1,0),(0,2)],
"Wild-Schwein":[(0,-1), (-1,0),(0,1)],
"Drache":[(-1,-2), (-1,2),(1,-1),(1,1)],
"Affe":[(-1,-1), (-1,1),(1,-1),(1,1)],
"Elefant":[(-1,-1), (-1,1),(0,-1),(0,1)],
"Hase":[(1,-1), (-1,1),(0,2)],
"Gottes-Anbeterin":[(-1,-1), (-1,1),(1,0)],
"Pferd":[(0,-1), (-1,0),(1,0)],
"Aal":[(-1,-1), (1,-1),(0,1)],
"Tiger":[(-2,0), (1,0)],
"Gans":[(-1,-1), (1,1),(0,-1), (0,1)],
"Kobra":[(0,-1), (-1,1),(1,1)],
"Frosch":[(0,-2), (-1,-1),(1,1)],
"Kranich":[(-1,0), (1,-1),(1,1)],
"Ochse":[(-1,0), (1,0),(0,1)]}

"""
Board class
"""

class Board(object):

    def __init__(self):
        self.h = 0
        self.hashTable, self.hashTurn, self.hashCards = create_hash_tables()
        self.turn = White
        self.h = self.h ^ self.hashTurn
        self.board = np.zeros((Dx, Dy))

        for j in range (0, Dy):
            self.board[4][j] = White
            if j != 2: self.h = self.h ^ self.hashTable[White][4][j]
        self.board[4][2] = WhiteK
        self.h = self.h ^self. hashTable[WhiteK][4][2]

        for j in range (0, Dy):
            self.board[0][j] = Black
            if j != 2: self.h = self.h ^ self.hashTable[Black][0][j]
        self.board[0][2] = BlackK
        self.h = self.h ^ self.hashTable[BlackK][0][2]

        self.chosen_cards = np.random.choice(list(cards.keys()), size = 5, replace= False)
        self.w_cards = [0,1]
        self.h = self.h ^ self.hashCards[White][0]
        self.h = self.h ^ self.hashCards[White][1]
        self.b_cards = [3,4]
        self.h = self.h ^ self.hashCards[Black][3]
        self.h = self.h ^ self.hashCards[Black][4]
        self.m_card = 2
        self.h = self.h ^ self.hashCards[Empty][2]
        
        

    def legalMoves(self):
        moves = []
        for i in range(0, Dx):
            for j in range(0, Dy):
                if self.board[i][j] * self.turn > 0: ## on vérifie si c'est la meme couleur
                    if self.turn == White:
                        for ind_card in self.w_cards:
                            for move_card in cards[self.chosen_cards[ind_card]]:
                                x2, y2 = i + move_card[0], j + move_card[1]
                                m = Move(self.turn, i, j, x2, y2, ind_card)
                                if m.valid(self):
                                    moves += [m]


                    elif self.turn == Black:
                        for ind_card in self.b_cards:
                            for move_card in cards[self.chosen_cards[ind_card]]:
                                x2, y2 = i - move_card[0], j - move_card[1]
                                m = Move(self.turn, i, j, x2, y2, ind_card)
                                if m.valid(self):
                                    moves += [m]
                    
                    else:
                        pass
        return moves

    def score(self):
        """
        checking if the ennemy Sensei is on the protected square
        """
        if (self.board [0] [2] == WhiteK):
            return 1.0
        elif (self.board [Dx - 1] [2] == Black):
            return 0.0
        """
        Checking if one of the Sensei died
        """
        if abs(self.board.sum()) >= 5:
            if self.board.sum() > 0:
                return 1.0
            else:
                return 0.0
        return 0.5

    def terminal(self):
        """
        If the game is over, returns True
        """
        if self.score() == 0.5:
            return False
        return True

    def play(self, move):
        pass_turn = False
        if not move.valid(self):
            print("Trying to play invalid move. Passing")
            pass_turn = True
            
        if not pass_turn:
            in_spot = deepcopy(self.board[move.x2, move.y2])
            moving_out = self.board[move.x1, move.y1]
            if in_spot != Empty:
                self.h = self.h ^ self.hashTable[in_spot][move.x2][move.y2]
                
            self.h = self.h ^ self.hashTable[moving_out][move.x1][move.y1]
            self.h = self.h ^ self.hashTable[moving_out][move.x2][move.y2]
            self.board[move.x2, move.y2] = deepcopy(self.board[move.x1, move.y1])
            self.board[move.x1, move.y1] = Empty
        
        # Even if pass, cards still change, and also turn
        if move.color == White:
            self.w_cards.remove(move.card)            
            self.w_cards += [deepcopy(self.m_card)]
            self.turn = Black
        else:
            self.b_cards.remove(move.card)
            self.b_cards += [deepcopy(self.m_card)]
            self.turn = White
        self.h = self.h ^ self.hashCards[move.color][move.card]
        self.h = self.h ^ self.hashCards[move.color][self.m_card]
        self.h = self.h ^ self.hashCards[Empty][move.card]
        self.h = self.h ^ self.hashCards[Empty][self.m_card]
        self.h = self.h ^ self.hashTurn
        self.m_card = move.card
        return
        
        # print(self.board)
        # print(self.w_cards, self.m_card, self.b_cards)

    def playout (self):
        while (True):
            moves = self.legalMoves()
            if self.terminal():
                return self.score()
            n = random.randint (0, len (moves) - 1)
            self.play (moves [n])
            # input("Next ?")

    def play_random(self):
        moves = self.legalMoves()
        if self.terminal():
            return self.score()
        n = random.randint (0, len (moves) - 1)
        self.play (moves [n])

"""
Move class
"""

class Move(object):
    def __init__(self, color, x1, y1, x2, y2, card):
        self.color = color
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.card = card
    
    def __eq__(self, other):
        """
        Implémente l'égalité entre deux instances de la classe Move
        ?? Add the card to the move comparison?
        """
        if isinstance(other, Move):
            if self.color == other.color and self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2:
                return True
        return False

    def valid(self, board):
        # print(self.x1, self.y1, self.x2, self.y2)
        if self.x2 >= Dx or self.y2 >= Dy or self.x2 < 0 or self.y2 < 0:
            return False
        if board.board[self.x2][self.y2] * self.color > 0:
            # self.board[i][j] * self.turn > 0
            return False
        return True
    
    def move_index_in_card(self, board):
        look_for = (self.x1 - self.x2, self.x1 - self.x2)
        for k, move in enumerate(cards[board.chosen_cards[self.card]]):
            if look_for[0]==move[0] and look_for[1]==move[1]:
                return k
        return None
    
    def code(self, board):
        """
        Encode the moves: Depends on initial position, card used (0-4), movement used from the card (0,1,2,3,...m as cards have different possible moves), if it captures a pion or the sensei
        Maybe also if it is made by a pion or the sensei?
        """
        init_pos = Dy * self.x1 + self.y1 # 25 options
        card = self.card # 5 options
        move_index = self.move_index_in_card(board) # 4 options
        captures = 0 if board.board[self.x2,self.y2] == Empty else 1 # 2 options
        is_sensei = 1 if abs(board.board[self.x1,self.y1])>1 else 0 # 2 options
        color = 0 if self.color == White else 1
        # 25-position, 5-card, 4-move_per_card, 2-is_capture, 2-is_sensei
        # Total of 2000 options for each color
        # Order is
        # color -> is_sensei -> captures -> move_index -> card -> position
        return 2000*color + 1000*is_sensei + 500*captures + 125*move_index + 25*card + init_pos
        
    def __repr__(self):
        print("Card {}: ({},{}) -> ({},{})".format(self.card, self.x1, self.y1, self.x2, self.y2))

# test = Board()
# print(test.board)

def test_card(key):
    
    mat = np.zeros((5,5))
    mat[2,2] = -1
    moves = cards[key]
    for move in moves:
        mat[move[0] + 2, move[1] + 2] = 1
    print(mat)

# test_card("Ochse")
# print(np.random.choice(list(cards.keys()), size = 5, replace= False))

def flat (board, n):
    moves = board.legalMoves ()
    bestScore = 0
    bestMove = moves [0]
    for m in range (len(moves)):
        
        sum = 0
        for i in range (n):
            # print("coup = {}".format(i))
            b = deepcopy (board)
            b.play (moves [m])
            r = b.playout ()
            if board.turn == Black:
                r = 1 - r
            sum = sum + r
        if sum > bestScore:
            bestScore = sum
            bestMove = moves [m]
    return bestMove

def UCB (board, n):
    moves = board.legalMoves ()
    sumScores = [0.0 for x in range (len (moves))]
    nbVisits = [0 for x in range (len(moves))]
    for i in range (n):
        bestScore = 0
        bestMove = 0
        for m in range (len(moves)):
            score = 1000000
            if nbVisits [m] > 0:
                 score = sumScores [m] / nbVisits [m] + 0.4 * np.sqrt (np.log (i) / nbVisits [m])
            if score > bestScore:
                bestScore = score
                bestMove = m
        b = deepcopy (board)
        b.play (moves [bestMove])
        r = b.playout ()
        if board.turn == Black:
            r = 1.0 - r
        sumScores [bestMove] += r
        nbVisits [bestMove] += 1
    bestScore = 0
    bestMove = moves [0]
    for m in range (len(moves)):
        score = nbVisits [m]
        if score > bestScore:
            bestScore = score
            bestMove = moves [m]
    return bestMove

"""
Hashtables
"""
def create_hash_tables():
    hashTable = dict()
    # ?? Empty has to be considered?
    for k in ref_values: ##5 possble par cases, empty, rouge roi ou pion, bleu roi ou pion
        l = []
        for i in range (Dx):
            l1 = []
            for j in range (Dy):
                l1.append (random.randint (0, 2 ** 64))
            l.append (l1)
        hashTable[k] = deepcopy(l)
        
    hashTurn = random.randint (0, 2 ** 64) ##le tour
    
    hashCards = dict()
    values= [Empty, White, Black]
    for k in values: ##3 emplacements de cartes possible, bleu, rouge ou milieu
        l = []
        for i in range (5): ## 5 cartes
            l.append (random.randint (0, 2 ** 64))
        hashCards[k] = deepcopy(l)
    return hashTable, hashTurn, hashCards

"""
main
"""

if __name__ == "__main__":
    obj = Board()
    print(obj.board)
    obj.playout()    