"""
Partie graphique réalisée avec Pygame
"""

##Importations

import pygame as p
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


'''
GUI related definitions
'''

WIDTH_BOARD = 650
WIDTH_CARDS = 200
HEIGHT = WIDTH_BOARD
WIDTH = WIDTH_BOARD + WIDTH_CARDS 

DIMENSION = 5
SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 20

IMAGES_background = p.transform.scale(p.image.load("images/board_good_size_redone.png"), (WIDTH_BOARD, HEIGHT))

# IMAGES_w = p.transform.scale(p.image.load("GUI/images/wp.png"), (SQ_SIZE, SQ_SIZE))
# IMAGES_wK = p.transform.scale(p.image.load("GUI/images/wK.png"), (SQ_SIZE, SQ_SIZE))
# IMAGES_b = p.transform.scale(p.image.load("GUI/images/bp.png"), (SQ_SIZE, SQ_SIZE))

IMAGES_w = p.transform.scale(p.image.load("images/red_pawn_decoupe.png"), (49, 81))
IMAGES_wK = p.transform.scale(p.image.load("images/red_king_decoupe.png"), (43 + 10, 90 + 10))
IMAGES_b = p.transform.scale(p.image.load("images/blue_pawn_decoupe.png"), (50, 80))
IMAGES_bK = p.transform.scale(p.image.load("images/blue_king_decoupe.png"), (42 + 15, 90 + 10))
piece_imgs = {GAME.White: IMAGES_w, GAME.WhiteK: IMAGES_wK,
              GAME.Black: IMAGES_b, GAME.BlackK: IMAGES_bK}

# Functions to locate cards, set them in the board, get the selected cards
PAD = 4
CARD_WIDTH, CARD_HEIGHT = WIDTH_CARDS-2*PAD, 120-2*PAD
separation = (HEIGHT - 5*CARD_HEIGHT)//2
range_cards_low = {0: 0*CARD_HEIGHT, 1: 1*CARD_HEIGHT, 2:2*CARD_HEIGHT + separation,
                   3:3*CARD_HEIGHT + 2*separation, 4:4*CARD_HEIGHT + 2*separation}
range_cards_high = {0: 1*CARD_HEIGHT, 1: 2*CARD_HEIGHT, 2:3*CARD_HEIGHT + separation,
                   3:4*CARD_HEIGHT + 2*separation, 4:5*CARD_HEIGHT + 2*separation}

def find_card(loc):
  for k, v in range_cards_low.items():
    up = range_cards_high[k]
    if v < loc and loc < up:
      return k
  return None



cards_files = {"Rooster":"rooster.jpg",
"Crab":"crab.jpg",
"Boar":"boar.jpg",
"Dragon":"dragon.jpg",
"Monkey":"monkey.jpg",
"Elephant":"elephant.jpg",
"Rabbit":"rabbit.jpg",
"Mantis":"mantis.jpg",
"Horse":"horse.jpg",
"Eel":"eel.jpg",
"Tiger":"tiger.jpg",
"Goose":"goose.jpg",
"Cobra":"cobra.jpg",
"Frog":"frog.jpg",
"Crane":"crane.jpg",
"Ox":"ox.jpg"}

cards_images = {k: p.transform.scale(p.image.load("images/{}".format(v)), (CARD_WIDTH, CARD_HEIGHT)) for k, v in cards_files.items()}

def change_to_color(rects, color='red'):
  for r in rects: r.fill(p.Color(color))

def is_on_own_piece(board, r, c):
  return board.board[r][c]*board.turn > 0

def translate_card_on_board(board, card):
  if card == 2: return board.m_card
  if card in [0,1]: return board.b_cards[card]
  if card in [3,4]: return board.w_cards[card-3]
  raise Exception("Invalid card, translation could not be made")

def is_on_board(row, col):
  if row < 0 or row >= DIMENSION: return False
  if col < 0 or col >= DIMENSION: return False
  return True

def refresh_colors_board(board_cells, first_piece_selected):
  restart_board_colors(board_cells)
  if not first_piece_selected is None:
    row, col = first_piece_selected 
    board_cells[row][col].fill(p.Color('green'))
    
  
def highlight_moves(gs, board_cells, first_piece_selected, card_selected):
  card_board = translate_card_on_board(gs, card_selected)
  cards_player= gs.w_cards if gs.turn==GAME.White else gs.b_cards
  if not first_piece_selected is None and card_board in cards_player:
    refresh_colors_board(board_cells, first_piece_selected)
    x1, y1 = first_piece_selected
    moves_card = GAME.cards[gs.chosen_cards[card_board]]
    for move_card in moves_card:                              
      x2, y2 = x1 + move_card[0], y1 + move_card[1]
      if is_on_board(x2, y2) and not is_on_own_piece(gs, x2, y2):
        print(x2, ', ', y2)
        board_cells[x2][y2].fill(p.Color('blue'))
  

"""
Main pour joueur à la main contre un programme
"""





def main(**kwargs):
    nb_coups = kwargs['nb_coups']
    # Start pygame
    
    p.init()

    p.display.set_caption("Onitama")
    myfont = p.font.SysFont("monospace", 48)
    screen = p.display.set_mode((WIDTH, HEIGHT))  
    
    # Camera rectangles for sections of  the canvas
    board_camera = p.Rect(0,0,WIDTH_BOARD,HEIGHT)
    cards_camera = p.Rect(WIDTH_BOARD,0,WIDTH_CARDS,HEIGHT)
    
    # subsurfaces of canvas
    # Note that subx needs refreshing when px_camera changes.
    '''
    CARDS
    '''
    screen_cards = screen.subsurface(cards_camera)
    screen_cards_ind_frame, screen_cards_ind_inner = {}, {}
    delta_h = CARD_HEIGHT + 2*PAD
    separation = (HEIGHT - 5*CARD_HEIGHT - 10*PAD)//2
    height = 0
    '''
    Why arent rectangles padded correctly?
    '''
    for i in [0,1]:
      screen_cards_ind_frame[i] = screen_cards.subsurface(
        p.Rect(0, height, CARD_WIDTH+2*PAD, CARD_HEIGHT+2*PAD))
      
      screen_cards_ind_inner[i] = screen_cards_ind_frame[i].subsurface(
        p.Rect(PAD, PAD, CARD_WIDTH, CARD_HEIGHT))
      
      height += delta_h
  
    height += separation
    screen_cards_ind_frame[2] = screen_cards.subsurface(
        p.Rect(0, height, CARD_WIDTH+2*PAD, CARD_HEIGHT+2*PAD))
    
    screen_cards_ind_inner[2] = screen_cards_ind_frame[2].subsurface(
        p.Rect(PAD, PAD, CARD_WIDTH, CARD_HEIGHT))
    height += delta_h 
    height += separation
    
    for i in [3,4]:
      screen_cards_ind_frame[i] = screen_cards.subsurface(
        p.Rect(0, height, CARD_WIDTH+2*PAD, CARD_HEIGHT+2*PAD))
      
      screen_cards_ind_inner[i] = screen_cards_ind_frame[i].subsurface(
        p.Rect(PAD, PAD, CARD_WIDTH, CARD_HEIGHT))
      
      height += delta_h 
      
    '''
    BOARD
    '''
    screen_board = screen.subsurface(board_camera)
    
    screen_board.fill(p.Color("white"))
    screen_cards.fill(p.Color("red"))
    
    board_cells = {i: {} for i in range(DIMENSION)}
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
      for j in range(DIMENSION):      
        color = colors[(j+i)%2]
        board_cells[i][j] = screen_board.subsurface(p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        board_cells[i][j].fill(color)
    
        

    clock = p.time.Clock()
    
   
    
    # Start game
    gs = GAME.Board()
    T = transposition_table.T_Table()    
    first_piece_selected = None
    card_selected = None
    
    running = True    
    block_game = False
    try:        
        while running:
          if block_game:
            '''
            Game is over, waiting for user to close window
            '''
            
            
            # render text
            msg = "{} is the winner!".format('White' if gs.score()>0.5 else 'Black')
            label = myfont.render(msg, 1, (5, 34, 250))
            screen.blit(label, (30, HEIGHT//2))
            p.display.update()
            
            for e in p.event.get():
              if e.type == p.QUIT:                    
                  running = False
                  print("Exiting")
                  p.quit()
                  sys.exit()
          else:
            if gs.turn == White:
                for e in p.event.get():
                    if e.type == p.QUIT:                    
                        running = False
                        print("Exiting")
                        p.quit()
                        sys.exit()
                                      
                    elif e.type == p.MOUSEBUTTONDOWN:
                        location = p.mouse.get_pos() ##(x,y) location of mouse
                        print(location)
                        col = location[0]//SQ_SIZE
                        row = location[1]//SQ_SIZE
                        
                        if col >= DIMENSION:
                          '''
                          Clicked on a card
                          '''
                          # Select the card                          
                          card_selected = find_card(location[1])
                          print("Card selected: ", card_selected)
                          
                          # Check if it belongs to player
                          if (gs.turn==GAME.White and not card_selected in [3,4]) or (gs.turn==GAME.Black and not card_selected in [0,1]):
                            continue
                          
                          #Highlight the card
                          back = screen_cards_ind_frame[card_selected]
                          change_to_color(list(screen_cards_ind_frame.values()))
                          back.fill(p.Color('green'))
                          
                          # if first cell is selected, highlight the possible moves
                          print("Checking spots to highlight")
                          highlight_moves(gs, board_cells, first_piece_selected, card_selected)
                              
                          
                        else:
                          
                          '''
                          Clicked on the board
                          '''
                          print("Board: cell selected: ({},{})".format(row, col))
                          
                          if is_on_own_piece(gs, row, col):
                            # Only works for selecting first piece to move                            
                            if not first_piece_selected is None:
                              # If is same cell, reset
                              if first_piece_selected[0] == row and first_piece_selected[1] == col:
                                restart_board_colors(board_cells)
                                first_piece_selected=None
                                
                              # If piece is already selected, must start over
                              print("Must move to an empty space")                                                            
                            else:                              
                              restart_board_colors(board_cells)
                              board_cells[row][col].fill(p.Color('green'))
                              first_piece_selected = (row, col)
                              
                              # If card is selected, highlight
                              # if first cell is selected, highlight the possible moves
                              if not card_selected is None:
                                x1, y1 = first_piece_selected
                                moves_card = GAME.cards[gs.chosen_cards[translate_card_on_board(gs, card_selected)]]
                                for move_card in moves_card:                              
                                  x2, y2 = x1 + move_card[0], y1 + move_card[1]
                                  if is_on_board(x2, y2) and not is_on_own_piece(gs, x2, y2):
                                    board_cells[x2][y2].fill(p.Color('blue'))
                          else:
                            # Only works if first piece is selected,
                            # card is selected, and move is a valid move                            
                            
                            
                            if card_selected is None:
                              print("Must select card first")                              
                              continue
                            else:
                              # Check if move is valid                              
                              move = GAME.Move(gs.turn,
                                               first_piece_selected[0],
                                               first_piece_selected[1],
                                               row, col,
                                               translate_card_on_board(gs, card_selected))
                              if move.valid(gs):
                                # Everything is good, we can make the move
                                print('Performing move')
                                print(move)
                                print(gs)
                                gs.play(move)
                                if gs.terminal():
                                  print("END")
                                  block_game = True
                                  
                                restart_board_colors(board_cells)
                                first_piece_selected = None
                                change_to_color(list(screen_cards_ind_frame.values()))
                                card_selected = None
                              else:
                                print("Move is not valid")
                                                            
                                       
            else:
                # Bot plays
                gs.play (PLAYERS.SHUSS(T, gs, nb_coups))
                if gs.terminal():
                  print("END")
                  block_game=True
                
            
            drawGameState(screen_board, screen_cards, screen_cards_ind_inner, gs, board_cells)
            clock.tick(MAX_FPS)
            
            p.display.flip()
    except Exception as e:
        print(e)        
        running = False
        print("Exiting")
        p.quit()
        sys.exit()
        


def drawGameState(screen_board, screen_cards, screen_cards_ind_inner, gs, board_cells):
    # drawBoard(screen_board)
    # displayBoard(screen_board)
    drawPieces(screen_board, gs.board, board_cells)
    drawCards(screen_cards, screen_cards_ind_inner, gs)

def color_square(screen,c, r, color='green'):
  p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def displayBoard(screen):
    screen.blit(IMAGES_background, p.Rect(0, 0, WIDTH_BOARD, HEIGHT))


def restart_board_colors(board_cells, colors=[p.Color("white"), p.Color("gray")]):
  for i in range(DIMENSION):
      for j in range(DIMENSION):      
        color = colors[(j+i)%2]        
        board_cells[i][j].fill(color)

def drawPieces(screen, board, board_cells, colors=[p.Color("white"), p.Color("gray")]):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != GAME.Empty:
              img = piece_imgs[piece]
              board_cells[r][c].blit(img, p.Rect( 30,  10, SQ_SIZE, SQ_SIZE))
            else:
              blank = p.Surface((SQ_SIZE, SQ_SIZE))
              blank.fill(board_cells[r][c].get_at((1,1)))
              board_cells[r][c].blit(blank, p.Rect( 0,  0, SQ_SIZE, SQ_SIZE))
              

def drawCards(screen, screen_cards_ind_inner, board):
  names = board.chosen_cards
  height = 0
  delta_h = CARD_HEIGHT
  
  cont = 0
  separation = (HEIGHT - 5*CARD_HEIGHT - 5*PAD)//2
  for i in board.b_cards:
    parent = screen_cards_ind_inner[cont].get_parent()
    parent.blit(cards_images[names[i]], screen_cards_ind_inner[cont].get_bounding_rect())
    height += delta_h + PAD
    cont +=1

  height += separation
  
  # Middle card  
  # screen.blit(cards_images[names[board.m_card]], cards_rects[cont])
  parent = screen_cards_ind_inner[cont].get_parent()
  parent.blit(cards_images[names[board.m_card]], screen_cards_ind_inner[cont].get_bounding_rect())
  height += delta_h + PAD
  cont +=1
    
  height += separation
  
  for i in board.w_cards:
    # screen.blit(cards_images[names[i]], cards_rects[cont])
    parent = screen_cards_ind_inner[cont].get_parent()
    parent.blit(cards_images[names[i]], screen_cards_ind_inner[cont].get_bounding_rect())
    height += delta_h + PAD
    cont +=1
  


"""
Main pour faire jouer deux bots l'un contre l'autre en utilisant le GUI
"""

def main_bot_vs_bot(bot1, bot2, bot1_kwargs, bot2_kwargs):
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GAME.Board()
    # validMoves = gs.legalMoves()
    # moveMade = False
    running = True
    # sqSelected = ()
    # playerClicks = []
    game_finished = False

    
    while running:
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
        if gs.terminal() and not game_finished:
            print("END")
            print(gs.score())
            game_finished = True
        if game_finished == False:
            if gs.turn == White: ## Pour faire jouer RAVE en Blanc il suffit de changer == White par == Black
                """
                UCB joue blanc
                """
                bot1_kwargs['board'] = gs                
                move = bot1(**bot1_kwargs)
                gs.play(move)
                print("bot 1 played")
                print("Card: {}".format(gs.chosen_cards[move.card]))
                print(gs.board)
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
                print(gs.board)
        else:
            p.quit()
            sys.exit()
        # time.sleep(2)



if __name__ == "__main__":
    
  
    """
    GUI human vs bot
    """
    if True:
      main(nb_coups = 500)
  
  
    