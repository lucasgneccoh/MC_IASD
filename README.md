# Onitama, the game
Final project - IASD - Monte Carlo Tree Search

We implement the game [Onitama](https://en.wikipedia.org/wiki/Onitama) in Python and test different MCTS algorithms to play the game. 

The script `onitama.py` contains the definition of the game with its rules and evolution. The class `Board` represents a game, and the class `Move` represents a move.

The script `play_functions.py` contains the different algorithms that play the game. The idea is that a player has to be general enough to play any other game. The standard arguments of a player are a transposition table (`\modules\transposition_table.py:T_Table`) that stores move statistics and other game constants passed from the game class, and a board representing the state of the game. Players must return a move given a transposition table, a board, and any other needed parameter.

# Use GUI to play the game
We made a simple implementation of the game using [Pygame](https://www.pygame.org/news).
If you want to play against one of the algorithms, launch the script `GUI_oni.py`. The parameters you can pass to this script are
Run `python GUI_oni.py --help` for all the details.
```
  --enemy    Select the enemy AI to play against from the options available (use --help to see them)
  --n        Budget for the AI
  --play_as  red or blue (red plays first)
```

# Compare the different algorithms
The script `modules\tournament.py` is designed to run a tournament between the bots. To run a tournament, you must create a JSON file containing the details for the tournament including its name, the bots included and their paramteres. See the [`bot_fights`](https://github.com/lucasgneccoh/Onitama/tree/main/bot_fights) folder for an [example](https://github.com/lucasgneccoh/Onitama/blob/main/bot_fights/tournament_example.json).
The results are saved in the `data` folder by default, but you can pass the desired path as argument.
Run `python tournament.py --help` for all the details.


# Create your own player
We tried to create general classes so that it is easy to implement your own AI. See the [`play_functions`](https://github.com/lucasgneccoh/Onitama/blob/main/modules/play_functions.py) script to see how we developped the players. The idea is to create a function that receives at least two inputs: a transposition table [T_Table](https://github.com/lucasgneccoh/Onitama/blob/main/modules/transposition_table.py) used to store move statictis and other variables from the game, and a [board](https://github.com/lucasgneccoh/Onitama/blob/main/modules/onitama.py) which contains all the game logic and state. You can also recieve other arguments if needed. This function must return a [Move](https://github.com/lucasgneccoh/Onitama/blob/main/modules/onitama.py) object representing the move to play next.
