import pandas as pd
import play_functions as PLAYERS
import onitama as GAME
from itertools import combinations, cycle, count
import transposition_table as T
import time
import elo
from random import shuffle
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import json
pd.options.mode.chained_assignment = None  # default='warn'

# %% Set transposition table info here
White = GAME.White
Black = GAME.Black
T.T_Table.MaxLegalMoves = GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 5

T.T_Table.MaxTotalLegalMoves = 2 * GAME.Dx * GAME.Dy * GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 2 * 2

T.T_Table.White = GAME.White
T.T_Table.Black = GAME.Black


bot_dict = PLAYERS.bots

# %% Classes and functions

def parseInputs():
  parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
  parser.add_argument("--out_path", help="Path to dump the output files with the results", default='../data')
  parser.add_argument("--verbose", help="Controls console output. true or false", default='false')
  parser.add_argument("--save_at_each", help="Choose to save the results after every match. If false, saves only at the end of the tournament", default='true')
  parser.add_argument("--rounds", help="Number of rounds each pair of bots will play (two games per round, home and away)", default=2)
  bot_options = ', '.join(bot_dict.keys())
  parser.add_argument("--bots", help=f"JSON file containing the tournaments and the bots involved. The options for the bots are {bot_options}. See \bot_fights\tournament_example.json for an example.", default="../bot_fights/tournament_example.json")
  args = parser.parse_args()
  return args


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
    loading = cycle(["-","/","|","\\"])
    num_moves = count(0,1)
    while (True):
        if verbose:
            c = next(loading)
            cont = next(num_moves)
            sys.stdout.write('\rRunning {}, Total moves: {:05d}'.format(c, cont))
            sys.stdout.flush()
        if board.terminal():
            return board.score()
        if board.turn == White:
            board.play(white_bot.play(board))
        else:
            board.play (black_bot.play(board))
        

def res_status(res, white_bot, black_bot):
  if res == 1: return white_bot.name
  if res == 0: return black_bot.name
  return "error"


def bot_from_json_dict(info, bot_dict):
  name = '_'.join(list(map(str, info.values())))
  bot = info['bot']
  del info['bot']
  return Bot(name, bot_dict[bot], **info)
  

# Fichier bots.csv avec les elos et les wins
def bots_df(BASE_PATH, all_bots):
  path_b = os.path.join(BASE_PATH,"bots.csv")
  if not os.path.exists(path_b):
    with open(path_b,'w+') as f:
      f.close()
    df = pd.DataFrame(columns = ["bot", "elo", "nb_played"] + [bot.name for bot in all_bots])
    for i, bot in enumerate(all_bots):
        df.loc[i] = [bot.name, 1200, 0] + ["0/0"]*len(all_bots)
    df.set_index("bot", inplace=True)
    if not os.path.exists(path_b):
      with open(path_b,'w+') as f:
        f.close()
    df.to_csv(path_b)
  else:
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
        df.to_csv(path_b)
  return df

# Fichier matches_history.csv avec l'historique des parties
def history_df(BASE_PATH):  
  path_h = os.path.join(BASE_PATH,"matches_history.csv")
  if not os.path.exists(path_h):
    with open(path_h, 'w+') as f:
      f.close()
    df_hist = pd.DataFrame(columns = ["datetime", "White", "Black", "Winner", "Elo White Before", "Elo Black Before", "Elo White After","Elo Black After"])
    df_hist.to_csv(path_h)
  else:
    try:
        df_hist = pd.read_csv(path_h)    
    except:
        df_hist = pd.DataFrame(columns = ["datetime", "White", "Black", "Winner", "Elo White Before", "Elo Black Before", "Elo White After","Elo Black After"])
        df_hist.to_csv(path_h)
  return df_hist




# %% Parse arguments
args = parseInputs()

BASE_PATH = args.out_path
VERBOSE = True if args.verbose=='true' else False
SAVE_EACH = True if args.save_at_each=='true'else False
ROUNDS = int(args.rounds)
PRINT_LENGTH = 40
FILL_CHAR = '-'
TOURNAMENT_PATH = args.bots


# %% Read json file with the tournaments to run
with open(TOURNAMENT_PATH) as f:
  content = json.load(f)
tournaments = content['tournaments']

# %% main

path_b = os.path.join(BASE_PATH,"bots.csv")
path_h = os.path.join(BASE_PATH,"matches_history.csv")

for tourn in tournaments:
  format_key = "{{:{}^{}}}".format(FILL_CHAR, PRINT_LENGTH)
  format_key_star = "{{:{}^{}}}".format("*", PRINT_LENGTH)
  
  
  print("*"*PRINT_LENGTH)
  print(format_key_star.format(" TOURNAMENT {} ".format(tourn)))
  print("*"*PRINT_LENGTH)
  print()
  all_bots = [bot_from_json_dict(t, bot_dict) for t in tournaments[tourn]]
  all_matches = list(combinations(all_bots, 2))
  
  df = bots_df(BASE_PATH, all_bots)
  df_hist = history_df(BASE_PATH)
  
  simple_table = pd.DataFrame(columns = ['white_bot','black_bot', 'score','time'])
  
  dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
  
  counter = 0
  for r in range(ROUNDS):
      shuffle(all_matches)
      if VERBOSE:
        print("*"*PRINT_LENGTH)
        print(format_key_star.format(" ROUND {} ".format(r+1)))
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
            print(e)
            res = None
          
          simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
          counter += 1
          if VERBOSE: 
            print("\nWinner: {}".format(res_status(res,white_bot,black_bot)))
          
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
            print(e)
            res = None
          
          
          simple_table.loc[counter] = [white_bot.name, black_bot.name, res, time.process_time()-start]
          counter += 1
          if VERBOSE: 
            print("\nWinner: {}".format(res_status(res,white_bot,black_bot)))
        
          hist = elo.updateTable(df, df_hist, white_bot, black_bot, res, dt_string)
          df_hist = df_hist.append(hist, ignore_index = True)
          
          if SAVE_EACH:
            df.to_csv(path_b)
            df_hist.to_csv(path_h, index = False)
          
  
  df.to_csv(path_b)
  df_hist.to_csv(path_h, index = False)
  path = os.path.join(BASE_PATH,"simple_table_{}.csv".format(dt_string))
  if not os.path.exists(path):
    with open(path,'w') as f:
      f.close()
  simple_table.to_csv(path, index = False)
  
  print(f"Tournament {tourn} is over. Results are available in {BASE_PATH}")

