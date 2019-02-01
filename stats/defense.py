import pandas as pd
import matplotlib.pyplot as plt
from frames import games, info, events


plays = games.query("type == 'play' & event != 'NP'")
plays.columns = ['type', 'inning', 'team', 'player', 'count', 'pitches', 'event', 
        'game_id', 'year']

# shift rows
pa = plays.loc[plays['player'].shift() != plays['player'], ['year', 'game_id', 
    'inning','team', 'player']]
pa = pa.groupby(['year','game_id', 'team']).size().reset_index(name='PA')

events = events.set_index(['year', 'game_id', 'team', 'event_type'])
events = events.unstack().fillna(0).reset_index()
events.columns = events.columns.droplevel()
events.columns = ['year', 'game_id', 'team', 'BB', 'E', 'H', 'HBP', 'HR', 'ROE', 'SO']
events = events.rename_axis(None, axis='columns')

print("events\n", events.head())
print("pa\n", pa.head())
events_plus_pa = pd.merge(events, pa, how='outer', left_on=['year', 'game_id', 'team'],
        right_on=['year', 'game_id', 'team'])
print("events_plus\n", events_plus_pa.head())
print("info\n", info.head())
# Merge plate appearances
defense = pd.merge(events_plus_pa, info)
#defense = pd.merge(events_plus_pa, info, how='outer', left_on=['year', 'game_id'],
#        right_on=['year', 'game_id'])

print("\ndefense\n", defense.head())
# add col and calculate the DER
defense.loc[:, 'DER'] = 1 - ((defense['H'] + defense['ROE'])/(defense['PA'] - defense['BB'] 
    - defense['SO'] - defense['HBP'] - defense['HR']))
# Convert to numeric
defense.loc[:, 'year'] = pd.to_numeric(defense['year'])
# filter those after 1978
der = defense.loc[defense['year'] >= 1978, ['year', 'defense', 'DER']]
print("der before pivot\n", der.head())
# Reshape with Pivot
der = der.pivot(index='year', columns='defense', values='DER')

print("der after pivot\n", der.head())
der.plot(x_compat=True, xticks=range(1978, 2018, 4), rot=45)
plt.show()


