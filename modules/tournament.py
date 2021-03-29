import numpy as np
import pandas as pd
import play_functions as bot_players
import onitama as ONI
from itertools import combinations
pd.options.mode.chained_assignment = None  # default='warn'

# bots = {"SHUSS1000":}

White = 1

class Bot:

    def __init__(self, name, play_func, nb_playouts, **kwargs):
        self.name = name
        self.play_func = play_func
        self.nb_playouts = nb_playouts
        self.params = kwargs

    def play(self, board):
        return self.play_func(board, self.nb_playouts, **self.params)

def bot1_vs_bot2(white_bot, black_bot, verbose = False):
    board= ONI.Board()
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

# shu1000_c4 = Bot("SHUSS_1000_C4", BtEngine.SHUSS, 1000, c = 4)
shu1000_c16 = Bot("SHUSS_1000_C16", bot_players.SHUSS, 1000, c = 16)
shu1000_c64 = Bot("SHUSS_1000_C64", bot_players.SHUSS, 1000, c = 64)
shu1000_c128 = Bot("SHUSS_1000_C128", bot_players.SHUSS, 1000, c = 128)
shu1000_c256 = Bot("SHUSS_1000_C256", bot_players.SHUSS, 1000, c = 256)

uct1000 = Bot("UCT_1000", bot_players.BestMoveUCT, 1000)
sh1000 = Bot("SH_1000", bot_players.SequentialHalving, 1000)
gr1000 = Bot("GRAVE_1000", bot_players.BestMoveGRAVE, 1000)
r1000 = Bot("RAVE_1000", bot_players.BestMoveRAVE, 1000)
ucb1000 = Bot("UCB_1000", bot_players.UCB, 1000)
flat1000 = Bot("FLAT_1000", bot_players.UCB, 1000)

# uct100 = Bot("UCT_100", BtEngine.BestMoveUCT, 100)
# sh100 = Bot("SH_100", BtEngine.SequentialHalving, 100)
# gr100 = Bot("GRAVE_100", BtEngine.BestMoveGRAVE, 100)
# r100 = Bot("RAVE_100", BtEngine.BestMoveRAVE, 100)
# ucb100 = Bot("UCB_100", BtEngine.UCB, 100)
# flat100 = Bot("FLAT_100", BtEngine.UCB, 100)
# shu100_c128 = Bot("SHUSS_100_C128", BtEngine.SHUSS, 100, c = 128)

all_bots = [shu1000_c16, shu1000_c64, shu1000_c128, shu1000_c256, uct1000, sh1000, gr1000, r1000, ucb1000, flat1000]

"""
Fichier bots.csv avec les elos et les wins
"""

try:
    df = pd.read_csv("GUI/modules/bots.csv", index_col="bot")
except:
    df = pd.DataFrame(columns = ["bot", "elo", "nb_played"] + [bot.name for bot in all_bots])
    for i, bot in enumerate(all_bots):
        df.loc[i] = [bot.name, 1200, 0] + ["0/0"]*len(all_bots)
    df.set_index("bot", inplace=True)
    df.to_csv("GUI/modules/bots.csv")

"""
Fichier matches_history.csv avec l'historique des parties
"""

try:
    df_hist = pd.read_csv("GUI/modules/matches_history.csv")

except:
    df_hist = pd.DataFrame(columns = ["White", "Black", "Winner", "Elo White Before", "Elo Black Before", "Elo White After","Elo Black After"])
    df_hist.to_csv("GUI/modules/matches_history.csv")

# import numpy as np

"""
Fonctions elo
"""

import matplotlib.pyplot as plt
from random import shuffle

def p(D):
    return 1.0/(1.0 + 10.0**(-D/400))

def K(nb_played):
    # if nb_played < 10:
    #     return 40
    # elif 10 <= nb_played < 20:
    #     return 30
    # else:
    #     return 20
    return 40

def updateElo(W, bot1, bot2):
    """
    W = 1 si bot1 gagne, 0.5 si match nul, 0 si bot2 gagne
    """
    D = df["elo"][bot1.name] - df["elo"][bot2.name]
    df["elo"][bot1.name] = int(df["elo"][bot1.name] + K(df["nb_played"][bot1.name])*(W - p(D)))
    df["elo"][bot2.name] = int(df["elo"][bot2.name] + K(df["nb_played"][bot2.name])*(1.0 - W - p(-D)))
    # played[bot1] += 1
    # played[bot2] += 1

def updateTable(df, df_hist, white_bot, black_bot, res):
    hist = {"White":white_bot.name, "Black":black_bot.name,
    "Elo White Before":df["elo"][white_bot.name],
    "Elo Black Before":df["elo"][black_bot.name]}

    if res == 1.0:
        list_res = df[black_bot.name][white_bot.name].split("/")
        list_res[0] = int(list_res[0])
        list_res[1] = int(list_res[1])
        list_res[0] += 1
        df[black_bot.name][white_bot.name] = "/".join([str(res) for res in list_res])
        hist["Winner"] = white_bot.name
        # df[black_bot.name][white_bot.name][0] += 1

    else:
        list_res = df[white_bot.name][black_bot.name].split("/")
        list_res[0] = int(list_res[0])
        list_res[1] = int(list_res[1])
        list_res[1] += 1
        df[white_bot.name][black_bot.name] = "/".join([str(res) for res in list_res])
        hist["Winner"] = black_bot.name

    updateElo(W = res, bot1 = white_bot, bot2 = black_bot)

    df["nb_played"][black_bot.name] +=1
    df["nb_played"][white_bot.name] +=1
    hist["Elo White After"] = df["elo"][white_bot.name]
    hist["Elo Black After"] = df["elo"][black_bot.name]
    # df_hist = df_hist.append(hist, ignore_index = True)
    return hist
    

"""
main
"""

all_matches = list(combinations(all_bots, 2))

for round in range(2):
    shuffle(all_matches)
    print("-"*20)
    print("ROUND {}".format(round))
    for i in range(len(all_matches)):
        print("MATCH {} on {}".format(i + 1, len(all_matches)))
        white_bot, black_bot = all_matches[i][0], all_matches[i][1]
        print("*"*20)
        print("MATCH {} VS {}".format(white_bot.name, black_bot.name))
        res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = False)
        hist = updateTable(df, df_hist, white_bot, black_bot, res)
        df_hist = df_hist.append(hist, ignore_index = True)
        df.to_csv("GUI/modules/bots.csv")
        df_hist.to_csv("GUI/modules/matches_history.csv", index = False)

        white_bot, black_bot = all_matches[i][1], all_matches[i][0]
        print("*"*20)
        print("SWITCHING SIDES")
        res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = False)
        hist = updateTable(df, df_hist, white_bot, black_bot, res)
        df_hist = df_hist.append(hist, ignore_index = True)
        df.to_csv("GUI/modules/bots.csv")
        df_hist.to_csv("GUI/modules/matches_history.csv", index = False)

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