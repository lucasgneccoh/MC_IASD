import pandas as pd
import os
os.chdir("./data")

file = 'big'

with open('bots_{}.csv'.format(file)) as f:  
  l=f.readline()
  columns = l.strip().split(',')
  data = pd.DataFrame(columns = columns)
  while l:
    l=f.readline()
    values = l.strip().split(',')
    if len(values)>1:      
      dic = dict(zip(columns,values))   
      data=data.append(dic, ignore_index=True)

bots = list(data['bot'])
data.set_index('bot', inplace=True)
data['nb_wins'] = 0.0
def add_wins(row, bots):
  s = 0
  for b in bots: s += sum(map(float, row[b].split('/')))
  return s
data['nb_wins'] = data.apply(lambda r: add_wins(r, bots), axis=1)
data['winrate'] = data['nb_wins'] / data['nb_played'].apply(float)
data.loc[:,['nb_wins','winrate']].sort_values(by='winrate', ascending=False)

data['nb_wins'].sum()


def add_col(col):
  return sum(map(float,col.split("/")))
  
data_2 = data.copy(deep=True)
for c in data.columns:
  if c in bots:
    data_2[c] = data_2[c].apply(add_col)
    
    
data_oponents = data_2.copy(deep=True)
for c in bots:
  for b in bots:
    if c==b: 
      data_oponents.loc[c,b] = 0.0
      continue
    try:
      # print(c, data_2.loc[c,b], '-----', b, data_2.loc[c,b])
      total = data_2.loc[c,b] + data_2.loc[b,c]
      # print(total)
      data_oponents.loc[c,b] = data_2.loc[c,b]/total
    except Exception as e:
      print(c, b)
      print(e)
    
