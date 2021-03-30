import numpy as np
import matplotlib.pyplot as plt
from random import shuffle

def p(D):
    return 1.0/(1.0 + 10.0**(-D/400))

def K(nb_played):
    if nb_played < 10:
        return 40
    elif 10 <= nb_played < 20:
        return 30
    else:
        return 20

def updateElo(W, bot1, bot2, df):
    """
    W = 1 si bot1 gagne, 0.5 si match nul, 0 si bot2 gagne
    """
    D = df["elo"][bot1.name] - df["elo"][bot2.name]
    df["elo"][bot1.name] = int(df["elo"][bot1.name] + K(df["nb_played"][bot1.name])*(W - p(D)))
    df["elo"][bot2.name] = int(df["elo"][bot2.name] + K(df["nb_played"][bot2.name])*(1.0 - W - p(-D)))
    
def updateTable(df, df_hist, white_bot, black_bot, res):
    try:
        hist = {"White":white_bot.name, "Black":black_bot.name,
        "Elo White Before":df["elo"][white_bot.name],
        "Elo Black Before":df["elo"][black_bot.name]}
    except KeyError as e:
        print("A bot was not found in the history table")
        raise e
        
            
        

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

    updateElo(W = res, bot1 = white_bot, bot2 = black_bot, df = df)

    df["nb_played"][black_bot.name] +=1
    df["nb_played"][white_bot.name] +=1
    hist["Elo White After"] = df["elo"][white_bot.name]
    hist["Elo Black After"] = df["elo"][black_bot.name]
    # df_hist = df_hist.append(hist, ignore_index = True)
    return hist


#######################################################

def fight(bot1, bot2):
    res = np.random.random()*force[bot1] - np.random.random()*force[bot2]
    # print(res)
    const = 1
    if res > const:
        return 1
    elif res < -1*const:
        return 0
    else:
        return 0.5

def updateHistory(bots):
    for bot in bots:
        history_elo[bot] += [elo[bot]]
    

if __name__ == "__main__":
    force = {"wood":5, "bronze":10, "silver":20, "gold":30, "platinium":40, "diamond":50, "master":60, "GM":80}
    elo = {"wood":1200, "bronze":1200, "silver":1200, "gold":1200, "platinium":1200, "diamond":1200, "master":1200, "GM":1200}
    history_elo = {"wood":[1200], "bronze":[1200], "silver":[1200], "gold":[1200], "platinium":[1200], "diamond":[1200], "master":[1200], "GM":[1200]}
    played = {"wood":0, "bronze":0, "silver":0, "gold":0, "platinium":0, "diamond":0, "master":0, "GM":0}
    bots = list(force.keys())
    total_plays = 1000
    for i in range(total_plays):
        shuffle(bots)
        for match in range(len(bots)//2):
            W = fight(bots[2*match], bots[2*match + 1])
            updateElo(W, bots[2*match], bots[2*match + 1])
        updateHistory(bots)
    bots = list(force.keys())
    for bot in bots:
        plt.plot(history_elo[bot], label = bot)
    plt.legend()
    plt.grid()
    plt.show()
