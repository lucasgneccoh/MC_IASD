# MC_IASD
Final project - IASD - Monte Carlo

We implement the game [Onitama](https://en.wikipedia.org/wiki/Onitama) and test different algorithms to play the game. 

The script `onitama.py` contains the definition of the game with its rules and evolution. The class `Board` represents a game, and the class `Move` represents a move.

The script `play_functions.py` contains the different algorithms that play the game. The idea is that a player has to be general enough to play any other game. The standard arguments of a player are a transposition table (`\modules\transposition_table.py:T_Table`) that stores move statistics and other game constants passed from the game class, and a board representing the state of the game. It must return a move.

# Use GUI to play the game
If you want to play against one of the algorithms, launch the script `GUI_oni.py`. The parameters you can pass to this script are
 --enemy    Select the enemy AI to play against from the options available (--help see them)
 --n        Budget for the AI
 --play_as  red or blue (red plays first)
 
# Compare the different algorithms
The script `modules\tournament.py` is designed to run a tournament between the bots. The results are saved in the `data` folder.

