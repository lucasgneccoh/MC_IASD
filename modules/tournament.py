import pandas as pd
import play_functions as PLAYERS
import onitama as GAME
from itertools import combinations
import transposition_table as T
import time
import elo
from random import shuffle
import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime



def parseInputs():
  parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("--out_path", help="Path to dump the output files with the results", default='../data')
  parser.add_argument("--verbose", help="Controls console output. true or false", default='false')
  parser.add_argument("--rounds", help="Number of rounds each pair of bots will play (two games per round, home and away)", default=2)
  args = parser.parse_args()
  return args




pd.options.mode.chained_assignment = None  # default='warn'


# Set transposition table info here
White = GAME.White
Black = GAME.Black
T.T_Table.MaxLegalMoves = GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 5

T.T_Table.MaxTotalLegalMoves = 2 * GAME.Dx * GAME.Dy * GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 2 * 2

T.T_Table.White = GAME.White
T.T_Table.Black = GAME.Black


class Bot:

    def __init__(self, name, play_func, **kwargs):
        self.name = name
        self.play_func = play_func        
        self.params = kwargs
        

    def play(self, board):
        Table = T.T_Table()
        return self.play_func(board=board, Table=Table, **self.params)

def bot1_vs_bot2(white_bot, black_bot, verbose = False):
    board= GAME.Board()
    while (True):
        if board.terminal():
            return board.score()
        if board.turn == White:
            board.play(white_bot.play(board))
        else:
            board.play (black_bot.play(board))
        if verbose: 
            # print(board.board)
            pass

def res_status(res, white_bot, black_bot):
  if res == 1: return white_bot.name
  if res == 0: return black_bot.name
  return "error"

n_tot = 1000

# shu1000_c4 = Bot("SHUSS_1000_C4", PLAYERS.SHUSS, n=n_tot, c = 4)
shu1000_c16 = Bot("SHUSS_1000_C16", PLAYERS.SHUSS, n=n_tot, c = 16)
shu1000_c64 = Bot("SHUSS_1000_C64", PLAYERS.SHUSS, n=n_tot, c = 64)
shu1000_c128 = Bot("SHUSS_1000_C128", PLAYERS.SHUSS, n=n_tot, c = 128)
shu1000_c256 = Bot("SHUSS_1000_C256", PLAYERS.SHUSS, n=n_tot, c = 256)

uct1000 = Bot("UCT_1000", PLAYERS.BestMoveUCT, n=n_tot)
sh1000 = Bot("SH_1000", PLAYERS.SequentialHalving, n=n_tot)
gr1000 = Bot("GRAVE_1000", PLAYERS.BestMoveGRAVE, n=n_tot)
r1000 = Bot("RAVE_1000", PLAYERS.BestMoveRAVE, n=n_tot)
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


all_bots = [shu1000_c16, shu1000_c64, shu1000_c128, shu1000_c256, uct1000, sh1000, gr1000, r1000, ucb1000, flat1000]
# all_bots = [uct1000,  gr1000, r1000, ucb1000, flat1000]

# all_bots = [r500, ucb500, flat500]
# all_bots = [r50, ucb50, flat50]


## For testing
# ucbTest= Bot("UCB_test", PLAYERS.UCB, n=100)
# flatTest = Bot("FLAT_test", PLAYERS.flat, n=100)
# all_bots = [ucbTest, flatTest]


args = parseInputs()

BASE_PATH = args.out_path
VERBOSE = True if args.verbose=='true' else False
ROUNDS = int(args.rounds)
PRINT_LENGTH = 40
FILL_CHAR = '-'



"""
Fichier bots.csv avec les elos et les wins
"""

path_b = os.path.join(BASE_PATH,"bots.csv")
try:
    df = pd.read_csv(path_b, index_col="bot")
    for b in all_bots:
        if not b in df.columns:
            raise Exception('New bot. Reseting table')
except:
    df = pd.DataFrame(columns = ["bot", "elo", "nb_played"] + [bot.name for bot in all_bots])
    for i, bot in enumerate(all_bots):
        df.loc[i] = [bot.name, 1200, 0] + ["0/0"]*len(all_bots)
    df.set_index("bot", inplace=True)
    if not os.path.exists(path_b):
      with open(path_b,'w+') as f:
        f.close()
    df.to_csv(path_b)
    

"""
Fichier matches_history.csv avec l'historique des parties
"""
path_h = os.path.join(BASE_PATH,"matches_history.csv")
try:
    df_hist = pd.read_csv(path_h)    
except:
    df_hist = pd.DataFrame(columns = ["datetime", "White", "Black", "Winner", "Elo White Before", "Elo Black Before", "Elo White After","Elo Black After"])
    if not os.path.exists(path_h):
      with open(path_h, 'w+') as f:
        f.close()
    df_hist.to_csv(path_h)



"""
main
"""

all_matches = list(combinations(all_bots, 2))

simple_table = pd.DataFrame(columns = ['white_bot','black_bot', 'score','time'])

dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
format_key = "{{:{}^{}}}".format(FILL_CHAR, PRINT_LENGTH)
format_key_star = "{{:{}^{}}}".format("*", PRINT_LENGTH)
counter = 0
for r in range(ROUNDS):
    shuffle(all_matches)
    if VERBOSE:
      print("*"*PRINT_LENGTH)
      print(format_key_star.format(" ROUND {} ".format(r)))
      print("*"*PRINT_LENGTH)
    for i in range(len(all_matches)):
        white_bot, black_bot = all_matches[i][0], all_matches[i][1]
        if VERBOSE:          
          print(format_key.format("  MATCH {} on {}  ".format(i + 1, len(all_matches))))  
          print("-"*PRINT_LENGTH)
          print(format_key.format("  MATCH {} VS {}  ".format(white_bot.name, black_bot.name)))
          
        start = time.process_time()
        try:
          res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = VERBOSE)
        except Exception as e:
          res = None
        
        simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
        counter += 1
        if VERBOSE: 
          print("Winner: {}".format(res_status(res,white_bot,black_bot)))
        
        hist = elo.updateTable(df, df_hist, white_bot, black_bot, res, dt_string)
        df_hist = df_hist.append(hist, ignore_index = True)
        white_bot, black_bot = all_matches[i][1], all_matches[i][0]
        print()
        if VERBOSE: 
          print(format_key.format("  SWITCHING SIDES  "))
        start = time.process_time()
        try:
          res = bot1_vs_bot2(white_bot = white_bot, black_bot = black_bot, verbose = VERBOSE)
        except Exception as e:
          res = None
        
        
        simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
        counter += 1
        if VERBOSE: 
          print("Winner: {}".format(res_status(res,white_bot,black_bot)))
      
        hist = elo.updateTable(df, df_hist, white_bot, black_bot, res, dt_string)
        df_hist = df_hist.append(hist, ignore_index = True)
        

df.to_csv(path_b)
df_hist.to_csv(path_h, index = False)
path = os.path.join(BASE_PATH,"simple_table_{}.csv".format(dt_string))
if not os.path.exists(path):
  with open(path,'w') as f:
    f.close()
simple_table.to_csv(path, index = False)

print(f"Tournament is over. Results are available in {BASE_PATH}")

