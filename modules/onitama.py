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
        self.turn = White
        self.board = np.zeros((Dx, Dy))

        for j in range (0, Dy):
            self.board[4][j] = White
        self.board[4][2] = WhiteK

        for j in range (0, Dy):
            self.board[0][j] = Black
        self.board[0][2] = BlackK

        self.chosen_cards = np.random.choice(list(cards.keys()), size = 5, replace= False)
        self.w_cards = [0,1]
        self.b_cards = [3,4]
        self.m_card = 2

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
        self.board[move.x2, move.y2] = deepcopy(self.board[move.x1, move.y1])
        self.board[move.x1, move.y1] = Empty
        if move.color == White:
            self.w_cards.remove(move.card)
            self.w_cards += [deepcopy(self.m_card)]
            self.turn = Black
        else:
            self.b_cards.remove(move.card)
            self.b_cards += [deepcopy(self.m_card)]
            self.turn = White
        self.m_card = move.card
        
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

hashTable = []
for k in range (5): ##5 possble par cases, empty, rouge roi ou pion, bleu roi ou pion
    l = []
    for i in range (Dx):
        l1 = []
        for j in range (Dy):
            l1.append (random.randint (0, 2 ** 64))
        l.append (l1)
    hashTable.append (l)
hashTurn = random.randint (0, 2 ** 64) ##le tour

for k in range (3): ##3 emplacements de cartes possible, bleu, rouge ou milieu
    l = []
    for i in range (5): ## 5 cartes
        l.append (random.randint (0, 2 ** 64))
    hashTable.append (l)

if __name__ == "__main__":
    obj = Board()
    print(obj.board)
    obj.playout()