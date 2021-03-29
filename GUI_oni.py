"""
Partie graphique réalisée avec Pygame
"""

##Importations

import pygame as p
from modules import onitama as BtEngine
import time
# import copy

##Constantes

WIDTH = HEIGHT = 500
DIMENSION = 5
SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15

IMAGES_background = p.transform.scale(p.image.load("images/board_good_size_redone.png"), (WIDTH, HEIGHT))

# IMAGES_w = p.transform.scale(p.image.load("GUI/images/wp.png"), (SQ_SIZE, SQ_SIZE))
# IMAGES_wK = p.transform.scale(p.image.load("GUI/images/wK.png"), (SQ_SIZE, SQ_SIZE))
# IMAGES_b = p.transform.scale(p.image.load("GUI/images/bp.png"), (SQ_SIZE, SQ_SIZE))

IMAGES_w = p.transform.scale(p.image.load("images/red_pawn_decoupe.png"), (49, 81))
IMAGES_wK = p.transform.scale(p.image.load("images/red_king_decoupe.png"), (43 + 10, 90 + 10))
IMAGES_b = p.transform.scale(p.image.load("images/blue_pawn_decoupe.png"), (50, 80))
IMAGES_bK = p.transform.scale(p.image.load("images/blue_king_decoupe.png"), (42 + 15, 90 + 10))



White = 1
Black = -1

"""
Main pour joueur à la main contre un programme
"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = BtEngine.Board()
    validMoves = gs.legalMoves()
    moveMade = False
    # loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    
    while running:
        # print("pass")
        if gs.turn == White:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.close()
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos() ##(x,y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): ##Reset Clicks
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks += [sqSelected]
                    if len(playerClicks) == 2:
                        move = BtEngine.Move(gs.turn,playerClicks[0][0], playerClicks[0][1],
                        playerClicks[1][0], playerClicks[1][1])
                        # print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.play(validMoves[i])
                                moveMade = True
                            
                                ##Reset Clicks
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

                # elif e.type == p.KEYDOWN:
                #     if e.key == p.K_z: ##undo when 'z' is pressed
                #         gs.undoMove()
                #         moveMade = True
            if moveMade:
                validMoves = gs.legalMoves()
                moveMade = False
        else:
            gs.play (BtEngine.UCB(gs, nb_coups))
            validMoves = gs.legalMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs):
    # drawBoard(screen)
    displayBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def displayBoard(screen):
    screen.blit(IMAGES_background, [0,0])

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece == 1: ##white
                screen.blit(IMAGES_w, p.Rect(c*SQ_SIZE + 30, r*SQ_SIZE + 10, SQ_SIZE, SQ_SIZE))
            elif piece == 9:
                screen.blit(IMAGES_wK, p.Rect(c*SQ_SIZE + 30, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            elif piece == -1: ##black
                screen.blit(IMAGES_b, p.Rect(c*SQ_SIZE + 30, r*SQ_SIZE + 10, SQ_SIZE, SQ_SIZE))
            elif piece == -9: ##black
                screen.blit(IMAGES_bK, p.Rect(c*SQ_SIZE + 30, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Main pour faire jouer deux bots l'un contre l'autre
"""

def main_bot_vs_bot():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = BtEngine.Board()
    validMoves = gs.legalMoves()
    moveMade = False
    running = True
    sqSelected = ()
    playerClicks = []
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
                gs.play(BtEngine.flat(gs, nb_coups))
                validMoves = gs.legalMoves()
                moveMade = False
                print("flat played")
                print(gs.board)
            elif gs.turn == Black:
                """
                RAVE joue noir
                """
                # gs.play_random ()
                gs.play(BtEngine.UCB(gs, nb_coups))
                validMoves = gs.legalMoves()
                moveMade = False
                print("UCB played")
                print(gs.board)
        # time.sleep(2)
        
def main_console(player = BtEngine.UCB, nb_steps = 100):
    gs = BtEngine.Board()
    while not gs.terminal():
        if gs.turn == White:
            # Show cards
            print("Your cards")
            for i in gs.w_cards:
                c_name = gs.chosen_cards[i]
                c = BtEngine.cards[c_name]
                print("{}: {} -> {}".format(i, c_name, c))
            print("Middle card")    
            c_name = gs.chosen_cards[gs.m_card]
            c = BtEngine.cards[c_name]
            print("{}: {} -> {}".format(gs.m_card, c_name, c))
            print("Opponent cards")
            for i in gs.b_cards:
                c_name = gs.chosen_cards[i]
                c = BtEngine.cards[c_name]
                print("{}: {} -> {}".format(i, c_name, c))
            print("Board")
            print(gs.board)
            
            
            sel_c= input("Select a card: ")
            
            if sel_c == 'q' or not int(sel_c) in gs.w_cards:
                break
                    
            sel_p= input("Enter piece to move (x,y): ")
            coords = list(map(int, sel_p.strip().split(',')))
                            
            sel_m = input("Select move from card (using index): ")
            c_name = gs.chosen_cards[int(sel_c)]
            c = BtEngine.cards[c_name]
            m = c[int(sel_m)]
            new_coords = [coords[0] + m[0], coords[1] + m[1]]
            move = BtEngine.Move(White, coords[0], coords[1], new_coords[0], new_coords[1], int(sel_c))
            gs.play(move)
            
        else:
            move = BtEngine.UCB(gs, nb_coups)
            print("Bot plays: ", move)
            gs.play(move)
            
    return gs.score()
    
         


if __name__ == "__main__":
    nb_coups = 100
    # main_bot_vs_bot()
    main_console()
    