# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 14:53:59 2021

@author: lucas
"""


import sys
from modules import onitama as GAME
from modules import play_functions as PLAYERS
from modules import transposition_table
import time
# import copy

##Constantes
'''
Game and player constants. They communicate some things through the transposition table
'''

White = GAME.White
Black = GAME.Black
transposition_table.T_Table.MaxLegalMoves = GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 5

transposition_table.T_Table.MaxTotalLegalMoves = 2 * GAME.Dx * GAME.Dy * GAME.ONITAMA_CARDS_IN_GAME * GAME.ONITAMA_MAX_MOVES_CARD * 2 * 2

def main_bot_vs_bot_console(bot1 = PLAYERS.UCB, bot2 = PLAYERS.flat, bot1_kwargs ={}, bot2_kwargs ={}, time_sleep = 1):
    
    gs = GAME.Board()
    running = True
    while running:        
        if gs.terminal():
            print("END")
            print(gs.score())
            print("Winner is {}".format("White" if gs.score()>0.5 else "Black"))
            break
        else:
            if gs.turn == White: ## Pour faire jouer RAVE en Blanc il suffit de changer == White par == Black
                """
                UCB joue blanc
                """
                bot1_kwargs['board'] = gs                
                move = bot1(**bot1_kwargs)
                gs.play(move)
                print("bot 1 played")
                print("Card: {}".format(gs.chosen_cards[move.card]))
                print(move)
                print(gs)
            elif gs.turn == Black:
                """
                Flat joue noir
                """
                # gs.play_random ()
                bot2_kwargs['board'] = gs
                move = bot2(**bot2_kwargs)
                gs.play(move)                
                print("bot 2 played")
                print("Card: {}".format(gs.chosen_cards[move.card]))
                print(move)
                print(gs)
        
        


def print_cards(gs):
    print("White cards")
    for i in gs.w_cards:
        c_name = gs.chosen_cards[i]
        c = GAME.cards[c_name]
        print("{}: {} -> {}".format(i, c_name, c))
    print("Middle card")    
    c_name = gs.chosen_cards[gs.m_card]
    c = GAME.cards[c_name]
    print("{}: {} -> {}".format(gs.m_card, c_name, c))
    print("Black cards")
    for i in gs.b_cards:
        c_name = gs.chosen_cards[i]
        c = GAME.cards[c_name]
        print("{}: {} -> {}".format(i, c_name, c))
    print("Board")
    print(gs)
    
"""
Main pour joueur à la main contre un programme en utilisant la console
"""
def main_console(player = PLAYERS.UCB, nb_steps = 100, **kwargs):
    gs = GAME.Board()
    while not gs.terminal():
        if gs.turn == White:
            # Show cards
            print_cards(gs)
            sel_c= input("Select a card: ")
            
            if sel_c == 'q' or not int(sel_c) in gs.w_cards:
                break
                    
            sel_p= input("Enter piece to move (x,y): ")
            coords = list(map(int, sel_p.strip().split(',')))
                            
            sel_m = input("Select move from card (using index): ")
            c_name = gs.chosen_cards[int(sel_c)]
            c = GAME.cards[c_name]
            m = c[int(sel_m)]
            new_coords = [coords[0] + m[0], coords[1] + m[1]]
            move = GAME.Move(White, coords[0], coords[1], new_coords[0], new_coords[1], int(sel_c))
            gs.play(move)
            
        else:
            move = player(gs, nb_coups, kwargs)
            print("Bot plays: ", move)
            gs.play(move)
            
    return gs.score()
    
         


if __name__ == "__main__":
    
  
    """
    Console bot vs bot
    """
    if True:
      nb_coups = 10
      
      # if player function requires a transposition table, it must be passed to the main function as a kwarg Table = t_table
      # main_console()

      T1 = transposition_table.T_Table()
      T2 = transposition_table.T_Table()
      # bot1 = PLAYERS.BestMoveGRAVE
      # bot1_kwargs = {'Table': T1,'n': nb_coups}
      
      # White player
      bot1 = PLAYERS.SequentialHalving
      bot1_kwargs = {'Table': T1, 'n': nb_coups}
      
      # Black player
      bot2 = PLAYERS.SHUSS
      bot2_kwargs = {'Table': T2, 'n': nb_coups}
      
      main_bot_vs_bot_console(bot1, bot2, bot1_kwargs, bot2_kwargs)
    