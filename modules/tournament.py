import numpy as np
import pandas as pd
import play_functions as PLAYERS
import onitama as GAME
from itertools import combinations
import transposition_table as T
import time
import elo
import matplotlib.pyplot as plt
from random import shuffle

pd.options.mode.chained_assignment = None  # default='warn'


# Set transposition table info here
White = GAME.White
Black = GAME.Black
T.T_Table.MaxLegalMoves = GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 5

T.T_Table.MaxTotalLegalMoves = 2 * GAME.Dx * GAME.Dy * GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 2 * 2



class Bot:

    def __init__(self, name, play_func, **kwargs):
        self.name = name
        self.play_func = play_func        
        self.params = kwargs
        

    def play(self, board):
        return self.play_func(board=board, **self.params)

def bot1_vs_bot2(white_bot, black_bot, verbose = False):
    board= GAME.Board()
    while (True):
        moves = board.legalMoves()
        if board.terminal():
            # if board.score() == 1.0:
            return board.score()
            # elif board.score() == 0:
            #     return black_bot.name
        if board.turn == White:
            board.play(white_bot.play(board))
        else:
            # n = random.randint (0, len (moves) - 1)
            board.play (black_bot.play(board))
        if verbose:
            print(board.board)  

# class Test:
#     def __init__(self, name, play_func, **kwargs):
#         self.name = name
#         self.play_func = play_func
#         # self.nb_playouts = nb_playouts
#         self.params = kwargs

#     def play(self, first):
#         return self.play_func(first, **self.params)

# def du_sal(first, x,y,z):
#     return first*(x+y+z)

# new = Test("lol",du_sal ,x= 1 ,y = 2,z = 4)
# print(new.play(4))

n_tot = 1000

# shu1000_c4 = Bot("SHUSS_1000_C4", PLAYERS.SHUSS, n=n_tot, c = 4, Table = T.T_Table())
# shu1000_c16 = Bot("SHUSS_1000_C16", PLAYERS.SHUSS, n=n_tot, c = 16, Table = T.T_Table())
# shu1000_c64 = Bot("SHUSS_1000_C64", PLAYERS.SHUSS, n=n_tot, c = 64, Table = T.T_Table())
# shu1000_c128 = Bot("SHUSS_1000_C128", PLAYERS.SHUSS, n=n_tot, c = 128, Table = T.T_Table())
# shu1000_c256 = Bot("SHUSS_1000_C256", PLAYERS.SHUSS, n=n_tot, c = 256, Table = T.T_Table())

uct1000 = Bot("UCT_1000", PLAYERS.BestMoveUCT, n=n_tot, Table = T.T_Table())
# sh1000 = Bot("SH_1000", PLAYERS.SequentialHalving, n=n_tot, Table = T.T_Table())
gr1000 = Bot("GRAVE_1000", PLAYERS.BestMoveGRAVE, n=n_tot, Table = T.T_Table())
r1000 = Bot("RAVE_1000", PLAYERS.BestMoveRAVE, n=n_tot, Table = T.T_Table())
ucb1000 = Bot("UCB_1000", PLAYERS.UCB, n=n_tot)
flat1000 = Bot("FLAT_1000", PLAYERS.flat, n=n_tot)

# r500 = Bot("RAVE_500", PLAYERS.BestMoveRAVE, n=500, Table = T.T_Table())
# ucb500 = Bot("UCB_500", PLAYERS.UCB, n=500)
# flat500 = Bot("FLAT_500", PLAYERS.flat, n=500)


# r50= Bot("RAVE_50", PLAYERS.BestMoveRAVE, n=50, Table = T.T_Table())
# ucb50 = Bot("UCB_50", PLAYERS.UCB, n=50)
# flat50 = Bot("FLAT_50", PLAYERS.flat, n=50)

# uct100 = Bot("UCT_100", PLAYERS.BestMoveUCT, n=100)
# sh100 = Bot("SH_100", PLAYERS.SequentialHalving, n=100)
# gr100 = Bot("GRAVE_100", PLAYERS.BestMoveGRAVE, n=100)
# r100 = Bot("RAVE_100", PLAYERS.BestMoveRAVE, n=100)
# ucb100 = Bot("UCB_100", PLAYERS.UCB, n=100)
# flat100 = Bot("FLAT_100", PLAYERS.UCB, n=100)
# shu100_c128 = Bot("SHUSS_100_C128", BtEngine.SHUSS, n=100, c = 128)

# all_bots = [shu1000_c16, shu1000_c64, shu1000_c128, shu1000_c256, uct1000, sh1000, gr1000, r1000, ucb1000, flat1000]
all_bots = [uct1000,  gr1000, r1000, ucb1000, flat1000]

# all_bots = [r500, ucb500, flat500]
# all_bots = [r50, ucb50, flat50]

"""
Fichier bots.csv avec les elos et les wins
"""

try:
    df = pd.read_csv("data/bots.csv", index_col="bot")
    for b in all_bots:
        if not b in df.columns:
            raise Exception('New bot. Reseting table')
except:
    df = pd.DataFrame(columns = ["bot", "elo", "nb_played"] + [bot.name for bot in all_bots])
    for i, bot in enumerate(all_bots):
        df.loc[i] = [bot.name, 1200, 0] + ["0/0"]*len(all_bots)
    df.set_index("bot", inplace=True)
    df.to_csv("data/bots.csv")

"""
Fichier matches_history.csv avec l'historique des parties
"""

try:
    df_hist = pd.read_csv("data/matches_history.csv")    
except:
    df_hist = pd.DataFrame(columns = ["White", "Black", "Winner", "Elo White Before", "Elo Black Before", "Elo White After","Elo Black After"])
    df_hist.to_csv("data/matches_history.csv")



"""
main
"""

all_matches = list(combinations(all_bots, 2))

simple_table = pd.DataFrame(columns = ['white_bot','black_bot', 'score','time'])
counter = 0
for round in range(2):
    shuffle(all_matches)
    print("-"*20)
    print("ROUND {}".format(round))
    for i in range(len(all_matches)):
        print("MATCH {} on {}".format(i + 1, len(all_matches)))
        white_bot, black_bot = all_matches[i][0], all_matches[i][1]
        print("*"*20)
        print("MATCH {} VS {}".format(white_bot.name, black_bot.name))
        start = time.process_time()
        res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = False)
        
        simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
        counter += 1
        print("Winner: {}".format(white_bot.name if res >0.5 else black_bot.name))
        
        hist = elo.updateTable(df, df_hist, white_bot, black_bot, res)
        df_hist = df_hist.append(hist, ignore_index = True)
        df.to_csv("data/bots.csv")
        df_hist.to_csv("data/matches_history.csv", index = False)

        white_bot, black_bot = all_matches[i][1], all_matches[i][0]
        # print("*"*20)
        print("SWITCHING SIDES")
        start = time.process_time()
        res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = False)
        
        simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
        counter += 1
        print("Winner: {}".format(white_bot.name if res >0.5 else black_bot.name))
      
        hist = elo.updateTable(df, df_hist, white_bot, black_bot, res)
        df_hist = df_hist.append(hist, ignore_index = True)
        df.to_csv("data/bots.csv")
        df_hist.to_csv("data/matches_history.csv", index = False)

simple_table.to_csv("data/simple_table.csv", index = False)




# white_bot, black_bot = sh1000, shu1000_c64
# res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = True)
# print(res)
# hist = updateTable(df, df_hist, white_bot, black_bot, res)
# df_hist = df_hist.append(hist, ignore_index = True)
# print(df)
# print(df_hist)
# # df_hist.reset_index(inplace = True)
# df.to_csv("GUI/modules/bots.csv", index = False)
# df_hist.to_csv("GUI/modules/matches_history.csv", index = False)


# list_res = df[black_bot.name][white_bot.name].split("/")
# list_res[0] = int(list_res[0])
# list_res[1] = int(list_res[1])
# if res == 1.0:
#     df[white_bot.name][black_bot.name][1]
# print(df[black_bot.name][white_bot.name].split("/"))