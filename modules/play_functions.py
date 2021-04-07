"""
Algorithmes MCTS, cours de Tristan CAZENAVE (https://www.lamsade.dauphine.fr/~cazenave/MonteCarloSearch.html)
"""

##Importations

import numpy as np
import copy
import sys

##Constantes
MAX_RECURSION_DELTA = 100 

"""
Shuss
"""

def SHUSS(Table, board, n, c = 128):
    '''
    Take game information from the Transposition Table
    '''
    White, Black = Table.__class__.White, Table.__class__.Black
    MTLM = Table.__class__.MaxTotalLegalMoves
    
    Table.addAMAF(board)
    t = Table.look(board)
    moves = board.legalMoves()
    total = len(moves)
    nbplayouts = [0.0 for x in range(MTLM)]
    nbwins = [0.0 for x in range(MTLM)]
    
    while len(moves) > 1:
        M = int(n / (len(moves) * np.log2(total)))
        for m in moves:          
            for i in range(max(M,1)):
                b = copy.deepcopy(board)
                b.play(m)
                played = [m.code(board)]
                res = GRAVE(Table, b, played, t) 
                # Doesn't GRAVE do the updateAMAF already?
                Table.updateAMAF(t, played, res)
                nbplayouts[m.code(board)] += 1
                if board.turn == White:
                    nbwins[m.code(board)] += res
                else:
                    nbwins[m.code(board)] += 1.0 - res
        moves = bestHalfSHUSS(t, board, moves, nbwins, nbplayouts, c, MTLM , Black)
    return moves[0]

def bestHalfSHUSS(t, board, moves, nbwins, nbplayouts, c = 128, MaxTotalLegalMoves=None, Black = None):
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
                bias = AMAF/nbplayouts[code]
                
                mu = nbwins[code]/nbplayouts[code] + c*bias
                if mu > best:
                    best = mu
                    bestMove = m
        notused[bestMove.code(board)] = False
        half += [bestMove]
    return half

"""
SequentialHalving
"""

def SequentialHalving(Table, board, n): 
    '''
    Take game information from the Transposition Table
    '''
    MTLM = Table.__class__.MaxTotalLegalMoves
  
    moves = board.legalMoves()
    total = len(moves)
    nbplayouts = [0.0 for x in range(MTLM)]
    nbwins = [0.0 for x in range(MTLM)]
    while len(moves) > 1:
        M = int(n / (len(moves)*np.log2(total)))
        for m in moves:
            for i in range(max(M,1)):
                b = copy.deepcopy(board)
                b.play(m)
                res = UCT(Table, b)
                nbplayouts[m.code(board)] += 1
                if board.turn == Table.__class__.White:
                    nbwins[m.code(board)] += res
                else:
                    nbwins[m.code(board)] += 1.0 - res
        moves = bestHalf(board, moves, nbwins, nbplayouts, MTLM)
    return moves[0]

def bestHalf(board, moves, nbwins, nbplayouts, MaxTotalLegalMoves):
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
    if len(played) >= sys.getrecursionlimit()-MAX_RECURSION_DELTA:
      return board.score()
    t = Table.look(board)
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
                    if board.turn == Table.__class__.Black:
                        Q = 1 - Q
                AMAF = tr[4][code] / tr[3][code]
                if board.turn == Table.__class__.Black:
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
        Table.addAMAF(board)
        return board.playoutAMAF(played)

    
def BestMoveGRAVE(Table, board, n):    
    for i in range(n):
        t = Table.look(board)
        b1 = copy.deepcopy(board)
        _ = GRAVE(Table, b1, [], t)
    t = Table.look(board)
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
    if len(played) >= sys.getrecursionlimit()-MAX_RECURSION_DELTA :
      return board.score()
    t = Table.look(board)
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
                    if board.turn == Table.__class__.Black:
                        Q = 1 - Q
                AMAF = t[4][code] / t[3][code]
                if board.turn == Table.__class__.Black:
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
        Table.addAMAF(board)
        return board.playoutAMAF(played)



def BestMoveRAVE(Table, board, n):    
    for i in range(n):
        b1 = copy.deepcopy(board)
        _ = RAVE(Table, b1, [])
    t = Table.look(board)
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

def UCT(Table, board, depth=0):
    if board.terminal():
        return board.score()
    if depth >= sys.getrecursionlimit()-MAX_RECURSION_DELTA :
        return board.score()
    t = Table.look(board)
    if t != None:
        bestValue = -10000000.0
        best = 0
        moves = board.legalMoves()
        for i in range(0, len(moves)):
            val = 10000000.0
            if t[1][i] > 0:
                Q = t[2][i] / t[1][i]
                if board.turn == Table.__class__.Black:
                    Q = 1 - Q
                val = Q + 0.4*np.sqrt(np.log(t[0])/t[1][i])
            if val > bestValue :
                bestValue = val
                best = i
        board.play(moves[best])
        res = UCT(Table, board, depth+1)
        t[0] += 1
        t[1][best] += 1
        t[2][best] += res
        return res
    else:
        Table.add(board)
        return board.playout()

def BestMoveUCT(Table, board, n):    
    for i in range(n):
        b1 = copy.deepcopy(board)
        _ = UCT(Table, b1)
    t = Table.look(board)
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

def flat (Table, board, n):
    moves = board.legalMoves ()
    bestScore = 0
    bestMove = moves [0]
    M = len(moves)
    for m in range (M):
        s = 0
        for i in range (n//M):
            b = copy.deepcopy (board)
            b.play (moves [m])
            r = b.playout ()
            if board.turn == Table.__class__.Black:
                r = 1 - r
            s = s + r
        if s > bestScore:
            bestScore = s
            bestMove = moves [m]
    return bestMove

# c = 0.4

"""
UCB
"""

def UCB (Table, board, n):
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
        if board.turn == Table.__class__.Black:
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
Random player
"""

def random_bot(Table, board):
    return np.random.choice(board.legalMoves ())

"""
Same move player
"""

def same_move(Table, board):
    return board.legalMoves ()[0]


if __name__=="__main__":
    print('play_functions')