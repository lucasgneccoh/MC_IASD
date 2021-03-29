"""
Algorithmes MCTS, cours de Tristan CAZENAVE (https://www.lamsade.dauphine.fr/~cazenave/MonteCarloSearch.html)
"""

##Importations

import numpy as np
import random
import copy
import tqdm

##Constantes

Dx = 5
Dy = 5
Empty = 0
White = 1
Black = -1
WhiteK = 9
BlackK = -9

ONITAMA_MAX_MOVES_CARD = 4
ONITAMA_CARDS_IN_GAME = 5
ONITAMA_DIFFER_CAPTURE = 1 # 2 if capture/no capture makes the same move different
'''
Just number of actions, independent from board state (like len(moves)):
    num_actions = # cards * # moves in card (5 * 4)
    ¿? Include "is_capture" here??
All possible actions considering state, is capture, etc:
    num_all_actions = num_actions * (Dx*Dy) * is_capture * is_sensei (2000)
'''
MaxLegalMoves = ONITAMA_MAX_MOVES_CARD * ONITAMA_CARDS_IN_GAME
MaxTotalLegalMoves = MaxLegalMoves * 2 * 2 * Dx*Dy
Table = {}

"""
HashTable pour les tables de transposition
"""

hashTable = []
for k in range (3):
    l = []
    for i in range (Dx):
        l1 = []
        for j in range (Dy):
            l1.append (random.randint (0, 2 ** 64))
        l.append (l1)
    hashTable.append (l)
hashTurn = random.randint (0, 2 ** 64)

"""
Fonctions utiles hors classes pour les algorithmes
"""

def look(Table, board):
    return Table.get(board.h, None)

def add(Table, board):
    nbplayouts = [0.0 for x in range(MaxLegalMoves)]
    nwins = [0.0 for x in range(MaxLegalMoves)]
    Table[board.h] = [0, nbplayouts, nwins]


def addAMAF(Table, board):
    nbplayouts = [0.0 for x in range(MaxLegalMoves)]
    nwins = [0.0 for x in range(MaxLegalMoves)]
    nbplayoutsAMAF = [0.0 for x in range(MaxTotalLegalMoves)]
    nwinsAMAF = [0.0 for x in range(MaxTotalLegalMoves)]
    Table[board.h] = [1, nbplayouts, nwins, nbplayoutsAMAF, nwinsAMAF]

"""
Shuss
"""

def updateAMAF(t, played, res):
    for i in range(len(played)):
        code = played[i]
        seen = False
        for j in range(i):
            if played[j] == code:
                seen = True
        if not seen:
            t[3][code] += 1
            t[4][code] += res

def SHUSS(board, budget, c = 128):
    Table = {}
    addAMAF(Table, board)
    t = look(Table, board)
    moves = board.legalMoves()
    total = len(moves)
    nbplayouts = [0.0 for x in range(MaxTotalLegalMoves)]
    nbwins = [0.0 for x in range(MaxTotalLegalMoves)]
    while len(moves) > 1:
        for m in moves:
            for i in range(int(budget / (len(moves) * np.log2(total)))):
                b = copy.deepcopy(board)
                b.play(m)
                played = [m.code(board)]
                res = GRAVE(Table, b, played, t)
                updateAMAF(t, played, res)
                nbplayouts[m.code(board)] += 1
                if board.turn == White:
                    nbwins[m.code(board)] += res
                else:
                    nbwins[m.code(board)] += 1.0 - res
        moves = bestHalfSHUSS(t, board, moves, nbwins, nbplayouts, c)
    return moves[0]

def bestHalfSHUSS(t, board, moves, nbwins, nbplayouts, c = 128):
    half = []
    notused = [True for x in range(MaxTotalLegalMoves)]
    # c = 128 ##initialement 128
    for i in range(len(moves) //2):
        best = -1.0
        bestMove = moves[0]
        for m in moves:
            code = m.code(board)
            if notused[code]:
                AMAF = t[4][code] / t[3][code]
                if board.turn == Black:
                    AMAF = 1 - AMAF
                mu = nbwins[code]/nbplayouts[code] + c*AMAF/nbplayouts[code]
                if mu > best:
                    best = mu
                    bestMove = m
        notused[bestMove.code(board)] = False
        half += [bestMove]
    return half

"""
SequentialHalving
"""

def SequentialHalving(board, budget):
    Table = {}
    
    moves = board.legalMoves()
    total = len(moves)
    nbplayouts = [0.0 for x in range(MaxTotalLegalMoves)]
    nbwins = [0.0 for x in range(MaxTotalLegalMoves)]
    while len(moves) > 1:
        for m in moves:
            for i in range(int(budget / (len(moves)*np.log2(total)))):
                b = copy.deepcopy(board)
                b.play(m)
                res = UCT(Table, b)
                nbplayouts[m.code(board)] += 1
                if board.turn == White:
                    nbwins[m.code(board)] += res
                else:
                    nbwins[m.code(board)] += 1.0 - res
        moves = bestHalf(board, moves, nbwins, nbplayouts)
    return moves[0]

def bestHalf(board, moves, nbwins, nbplayouts):
    half = []
    notused = [True for x in range(MaxTotalLegalMoves)]
    for i in range(len(moves) // 2):
        best = -1.0
        bestMove = moves[0]
        for m in moves:
            code = m.code(board)
            if notused[code]:
                # mu = nbwins[code]
                # nbplayouts[code] += 1
                mu = nbwins[code] / nbplayouts[code]
                if mu > best:
                    best = mu
                    bestMove = m
        notused[bestMove.code(board)] = False
        half += [bestMove]
    return half

"""
Grave
"""

def GRAVE(Table, board, played, tref):
    if (board.terminal()):
        return board.score()
    t = look(Table, board)
    if t != None:
        tr = tref
        if t[0] > 50:
            tr = t
        bestValue = -100000.0
        best = 0
        moves = board.legalMoves()
        bestcode = moves[0].code(board)
        for i in range(0, len(moves)):
            val = 100000.0
            code = moves[i].code(board)
            if tr[3][code] > 0:
                beta = tr[3][code] / (t[1][i] + tr[3][code] + 1e-5*t[1][i] * t[3][code])
                Q = 1
                if t[1][i] > 0:
                    Q = t[2][i] / t[1][i]
                    if board.turn == Black:
                        Q = 1 - Q
                AMAF = tr[4][code] / tr[3][code]
                if board.turn == Black:
                    AMAF = 1 - AMAF
                val = (1.0 - beta) * Q + beta * AMAF
            if val > bestValue:
                bestValue = val
                best = i
                bestcode = code
        board.play(moves[best])
        played += [bestcode]
        res = GRAVE(Table, board, played, tr)
        t[0] += 1
        t[1][best] += 1
        t[2][best] += res
        for i in range(len(played)):
            code = played[i]
            seen = False
            for j in range(i):
                if played[j] == code:
                    seen = True
            if not seen:
                t[3][code] += 1
                t[4][code] += res
        return res
    else:
        addAMAF(Table, board)
        return board.playoutAMAF(played)

    
def BestMoveGRAVE(board, n):
    Table = {}
    for i in range(n):
        t = look(Table, board)
        b1 = copy.deepcopy(board)
        res = GRAVE(Table, b1, [], t)
    t = look(Table, board)
    moves = board.legalMoves()
    best = moves[0]
    bestValue = t[1][0]
    for i in range(1, len(moves)):
        if (t[1][i] > bestValue):
            bestValue = t[1][i]
            best = moves[i]
    return best

"""
RAVE
"""

def RAVE(Table, board, played):
    if (board.terminal()):
        return board.score()
    t = look(Table, board)
    if t!=None:
        bestValue = -10000000.0
        best = 0
        moves = board.legalMoves()
        bestCode = moves[0].code(board)
        for i in range(0, len(moves)):
            val = 1000000.0
            code = moves[i].code(board)
            # print(t[3])
            if t[3][code] > 0:
                beta = t[3][code] / (t[1][i] + t[3][code] + 1e-5 * t[1][i] * t[3][code])
                Q = 1
                if t[1][i] > 0:
                    Q = t[2][i] / t[1][i]
                    if board.turn == Black:
                        Q = 1 - Q
                AMAF = t[4][code] / t[3][code]
                if board.turn == Black:
                    AMAF = 1 - AMAF
                val = (1.0 - beta) * Q + beta * AMAF
            if val > bestValue:
                bestValue = val
                best = i
                bestCode = code
        board.play(moves[best])
        res = RAVE(Table, board, played)
        t[0] += 1
        t[1][best] += 1
        t[2][best] += res
        played.insert(0, bestCode)
        for k in range(len(played)):
            code = played[k]
            seen = False
            for j in range(k):
                if played[j] == code:
                    seen = True
            if not seen:
                t[3][code] += 1
                t[4][code] += res
        # played.insert(0, moves[best])
        return res
    else:
        addAMAF(Table, board)
        return board.playoutAMAF(played)



def BestMoveRAVE(board, n):
    Table = {}
    for i in range(n):
        b1 = copy.deepcopy(board)
        res = RAVE(Table, b1, [])
    t = look(Table, board)
    moves = board.legalMoves()
    best = moves[0]
    bestValue = t[1][0]
    for i in range(1, len(moves)):
        if (t[1][i] > bestValue):
            bestValue = t[1][i]
            best = moves[i]

    ##Enlever les commentaires pour print les statistiques AMAF
    # print("t3")
    # print(t[3])
    # print("t4")
    # print(t[4])
    return best

"""
UCT
"""

def UCT(Table, board):
    if board.terminal():
        return board.score()
    t = look(Table, board)
    if t != None:
        bestValue = -10000000.0
        best = 0
        moves = board.legalMoves()
        for i in range(0, len(moves)):
            val = 10000000.0
            if t[1][i] > 0:
                Q = t[2][i] / t[1][i]
                if board.turn == Black:
                    Q = 1 - Q
                val = Q + 0.4*np.sqrt(np.log(t[0])/t[1][i])
            if val > bestValue :
                bestValue = val
                best = i
        board.play(moves[best])
        res = UCT(Table, board)
        t[0] += 1
        t[1][best] += 1
        t[2][best] += res
        return res
    else:
        add(Table, board)
        return board.playout()

def BestMoveUCT(board, n):
    Table = {}
    for i in range(n):
        b1 = copy.deepcopy(board)
        res = UCT(Table, b1)
    t = look(Table, board)
    moves = board.legalMoves()
    best = moves[0]
    bestValue = t[1][0]
    for i in range(1, len(moves)):
        if (t[1][i] > bestValue):
            bestValue = t[1][i]
            best = moves[i]
    return best



"""
Flat Monte Carlo
"""

def flat (board, n):
    moves = board.legalMoves ()
    bestScore = 0
    bestMove = moves [0]
    for m in range (len(moves)):
        sum = 0
        for i in range (n):
            b = copy.deepcopy (board)
            b.play (moves [m])
            r = b.playout ()
            if board.turn == Black:
                r = 1 - r
            sum = sum + r
        if sum > bestScore:
            bestScore = sum
            bestMove = moves [m]
    return bestMove

# c = 0.4

"""
UCB
"""

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
        b = copy.deepcopy (board)
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
Board Class
"""

class Board(object):
    def __init__(self):
        self.h = 0
        self.turn = White
        self.board = np.zeros((Dx, Dy))
        for i in range (0, 2):
            for j in range (0, Dy):
                self.board[i][j] = White
        for i in range (Dx - 2, Dx):
            for j in range (0, Dy):
                self.board[i][j] = Black

    def play (self, move):
        col = int (self.board [move.x2] [move.y2])
        if col != Empty:
            self.h = self.h ^ hashTable [col] [move.x2] [move.y2]
        self.h = self.h ^ hashTable [move.color] [move.x2] [move.y2]
        self.h = self.h ^ hashTable [move.color] [move.x1] [move.y1]
        self.h = self.h ^ hashTurn
        self.board [move.x2] [move.y2] = move.color
        self.board [move.x1] [move.y1] = Empty
        if (move.color == White):
            self.turn = Black
        else:
            self.turn = White

    
    
    
    
    """
    Fonctions de base pour le Breaktrough
    """

    def legalMoves(self):
        """
        Liste des coups autorisés
        """
        moves = []
        for i in range (0, Dx):
            for j in range (0, Dy):
                if self.board [i] [j] == self.turn:
                    for k in [-1, 0, 1]:
                        for l in [-1, 0, 1]:
                            m = Move (self.turn, i, j, i + k, j + l)
                            if m.valid (self):
                                moves.append (m)
        return moves

    def score (self):
        """
        Renvoie le score, 1 si blanc gagne, 0 si noir gagne, 0.5 si la partie n'est pas finie
        """
        for i in range (0, Dy):
            if (self.board [Dx - 1] [i] == White):
                return 1.0
            elif (self.board [0] [i] == Black):
                return 0.0
        l = self.legalMoves ()
        if len (l) == 0:
            if self.turn == Black:
                return 1.0
            else:
                return 0.0
        return 0.5
 
    def terminal (self):
        """
        Si la partie est finie, renvoie True
        """
        if self.score () == 0.5:
            return False
        return True

    """
    Playout aléatoires
    """

    def playout (self):
        while (True):
            moves = self.legalMoves()
            if self.terminal():
                return self.score()
            n = random.randint (0, len (moves) - 1)
            self.play (moves [n])
            # print(self.board)

    def playoutAMAF(self, played):
        while(True):
            moves = []
            moves = self.legalMoves()
            if len(moves) == 0 or self.terminal():
                return self.score()
            n = random.randint(0, len(moves) - 1)
            played += [moves[n].code(self)]
            self.play(moves[n])
            

    """
    Fonctions faisant s'affronter deux algorithmes
    """

    def playflat_vs_random(self):
        while (True):
            moves = self.legalMoves()
            if self.terminal():
                return self.score()
            if self.turn == White:
                self.play(flat (board, 10))
            else:
                n = random.randint (0, len (moves) - 1)
                self.play (moves [n])
            # print(self.board)

    def RAVE_vs_UCB(self, nb_coups = 10, verbose = True):
        while (True):
            moves = self.legalMoves()
            if self.terminal():
                return self.score()
            if self.turn == Black:
                self.play(BestMoveRAVE (board, nb_coups))
            else:
                # n = random.randint (0, len (moves) - 1)
                self.play (UCB (board, nb_coups))
            if verbose:
                print(self.board)  

"""
Move Class
"""

class Move(object):
    def __init__(self, color, x1, y1, x2, y2):
        self.color = color
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __eq__(self, other):
        """
        Implémente l'égalité entre deux instances de la classe Move
        """
        if isinstance(other, Move):
            if self.color == other.color and self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2:
                return True
        return False

    def valid (self, board):
        """
        Le move est-il valide ?
        """
        if self.x2 >= Dx or self.y2 >= Dy or self.x2 < 0 or self.y2 < 0:
            return False
        if self.color == White:
            if self.x2 != self.x1 + 1:
                return False
            if board.board [self.x2] [self.y2] == Black:
                if self.y2 == self.y1 + 1 or self.y2 == self.y1 - 1:
                    return True
                return False
            elif board.board [self.x2] [self.y2] == Empty:
                if self.y2 == self.y1 + 1 or self.y2 == self.y1 - 1 or self.y2 == self.y1:
                    return True
                return False
        elif self.color == Black:
            if self.x2 != self.x1 - 1:
                return False
            if board.board [self.x2] [self.y2] == White:
                if self.y2 == self.y1 + 1 or self.y2 == self.y1 - 1:
                    return True
                return False
            elif board.board [self.x2] [self.y2] == Empty:
                if self.y2 == self.y1 + 1 or self.y2 == self.y1 - 1 or self.y2 == self.y1:
                    return True
                return False
        return False


    def code(self, board):
        """
        Code les moves
        """
        direction = 1
        if self.y2 > self.y1:
            if board.board[self.x2][self.y2] == Empty:
                direction = 0
            else:
                direction = 3
        if self.y2 < self.y1:
            if board.board[self.x2][self.y2] == Empty:
                direction = 2
            else:
                direction = 4
        if self.color == White:
            return 5* (Dy * self.x1 + self.y1) + direction
        else:
            return 5*Dx*Dy+5*(Dy*self.x1 + self.y1) + direction

if __name__=="__main__":
    res = 0

    board = Board()
    res += board.RAVE_vs_UCB(nb_coups = 1000, verbose=True)
    print(board.board)

    print(res)



