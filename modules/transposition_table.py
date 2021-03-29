# -*- coding: utf-8 -*-

class T_Table(object):
    MaxLegalMoves = None
    MaxTotalLegalMoves = None
    
    def __init__(self):
        if T_Table.MaxLegalMoves is None or T_Table.MaxTotalLegalMoves is None:
            raise Exception("Before creating a Transposition table, class variables 'MaxLegalMoves' and 'MaxTotalLegalMoves' must be set. Use game constants to define these values")
            
        self.MaxLegalMoves = T_Table.MaxLegalMoves
        self.MaxTotalLegalMoves = T_Table.MaxTotalLegalMoves
        self.Table = {}
    
    def look(self, board):
        return self.Table.get(board.h, None)
    
    def add(self, board):
        nbplayouts = [0.0 for x in range(self.MaxLegalMoves)]
        nwins = [0.0 for x in range(self.MaxLegalMoves)]
        self.Table[board.h] = [0, nbplayouts, nwins]
    
    
    def addAMAF(self, board):
        nbplayouts = [0.0 for x in range(self.MaxLegalMoves)]
        nwins = [0.0 for x in range(self.MaxLegalMoves)]
        nbplayoutsAMAF = [0.0 for x in range(self.MaxTotalLegalMoves)]
        nwinsAMAF = [0.0 for x in range(self.MaxTotalLegalMoves)]
        self.Table[board.h] = [1, nbplayouts, nwins, nbplayoutsAMAF, nwinsAMAF]
    
    '''
    This function can be called over an instance of the class, but is more like a class method for now
    '''
    def updateAMAF(self, t, played, res):
        for i in range(len(played)):
            code = played[i]
            seen = False
            for j in range(i):
                if played[j] == code:
                    seen = True
            if not seen:
                t[3][code] += 1
                t[4][code] += res