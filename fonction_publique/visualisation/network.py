import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pydot
from networkx.drawing.nx_pydot import write_dot

#def plot_network(transition_w_outside = True, threshold = None):
"plot a network of the careers transitions"
"transition_w_outisde=False leads to not representing transitions from/to missing grades"
"threshold takes an integer as argument. Only trajectories taken by a number superior or equal"
"to the threshold are represented"
load_path = 'M:/CNRACL/output/archives'
save_path = 'C:/Users/l.degalle/CNRACL/fonction-publique/fonction_publique/ecrits/note_1_Lisa/Tables'

# List of grades that are in the AT corps
list_neg_AT = ['0793', '0794', '0795', '0796']
list_neg_AA = ['0791', '0792', '0014', '0162']
list_neg_AS = ['0839', '0840','0841']

# Read data
df_AT = pd.read_table(os.path.join(load_path, "corpsAT_2011.csv"),
                      delimiter=",")
df_AA = pd.read_table(os.path.join(load_path, "corpsAA_2011.csv"),
                      delimiter=",")
df_AS = pd.read_table(os.path.join(load_path, "corpsAS_2011.csv"),
                      delimiter=",")

df = df_AT.append(df_AA).append(df_AS)
df = df.sort(['ident'])
df = df.drop('Unnamed: 0', 1)
df = df.drop_duplicates() # dup appear when merging df from different corps                
                       
print(df.c_neg.value_counts())

# Filter out observations with null c_neg
df = df.loc[~df['c_neg'].isnull()]
print len(df)
df = df.loc[df['etat4'] == 1] # prends uniquement les obs en activité
print len(df)
           
ids_full =  pd.DataFrame(df.groupby(['ident'])['annee'].count() == 5).reset_index()
ids_full = ids_full.loc[ids_full['annee'] == True]

df = df.loc[df['ident'].isin(ids_full['ident'])]
df = df.set_index(['ident', 'annee'])

# Create lags for code neg
df = df.sort_index()
df['lagged_neg'] = df.groupby(level=0)['c_neg'].shift(1); df

#transition_w_outside = True
#if transition_w_outside == True:
#    # Rebalance panel in order to get transitions to outside
#    df = df.reset_index()
#    idents = df['ident'].unique()
#    all_dates = df['annee'].unique()
#    
#    idents_full = np.array([[y]*len(all_dates) for y in idents]).flatten()
#    dates_full = all_dates.tolist() * len(idents)
#    
#    balanced_panel = pd.DataFrame(
#                                {'ident': idents_full, 'annee': dates_full}
#                                )
#    df = balanced_panel.merge(
#            df, how='left', on=['ident', 'annee']).fillna("manquant")
#    # le code neg lagged vaut NA si l'année est 2011 et qu'on a les données pour cette personne
#    df['lagged_neg'] = np.where((df['sexe'] != False) & (df['annee'] == 2011), 'NA', df['lagged_neg'])
#
#    already_entered = True
#    if already_entered == True:
#        df = 
#else:
#    df = df  
## Create df of number of transitions for each couple (c_neg, lagged_neg)
to_graph = df.groupby(
        ["lagged_neg", "c_neg"]).size().reset_index(name='size')
to_graph = to_graph.sort('size', ascending = False)
to_graph = to_graph[15000 < to_graph['size']]

df_number_of_trans_fr_lag = pd.DataFrame(to_graph.groupby('lagged_neg')['size'].sum()).reset_index()

to_graph = to_graph.merge(df_number_of_trans_fr_lag, on = ['lagged_neg'], how = 'left')
to_graph['share_of_transit'] = to_graph['size_x'] / to_graph['size_y']


# Create nodelist as list of unique code grades
nodelist = set(to_graph['c_neg'].unique().tolist())

# Define the weights, which will be used as attributes of the edges
#weights = pd.to_numeric(to_graph['size'].reset_index()['size'].tolist())

###### plot without lagged_neg = c_neg
#mask = to_graph['lagged_neg'] == to_graph['c_neg']
#to_graph2 = to_graph[~mask] 
#to_graph2 = to_graph2[
#        10000 < to_graph2['size']
#        ]

#weights = pd.to_numeric(to_graph2['size'].reset_index()['size'].tolist())

# Initialize a directed graph
G3 = nx.MultiDiGraph()

# Add nodes to the directed graph
G3.add_nodes_from(nodelist)

# Add color attributes to differentiate nodes/grades that are in the AT corps
# and not in the AT corps
color_map = []
for node in G3:
    if node in list_neg_AT:
        color_map.append('magenta')
    elif node in list_neg_AS:
        color_map.append('cyan')
    elif node in list_neg_AA:
        color_map.append('yellow')
    else:
        color_map.append('red')

node_types = ['AT', 'AS', 'AA', 'autres']

autres = set(to_graph.c_neg.unique().tolist(
        )) - set(list_neg_AT) - set(list_neg_AA) - set(list_neg_AS)
dict_nodes_types = {'AT': list_neg_AT,
                    'AS': list_neg_AS,
                    'AA': list_neg_AA,
                    'autres': autres}
node_colors = ['magenta', 'cyan', 'yellow', 'red']
dict_type_color = dict(zip(node_types, node_colors))

## Get size for transition to same node
#to_graph_no_transition = to_graph[to_graph['lagged_neg'] == to_graph['c_neg']]
#to_graph_no_transition = to_graph_no_transition.set_index('c_neg')
#to_graph_no_transition = to_graph_no_transition.loc[G3.nodes()] # reorder the size in nodes order (important)

# Add edges with corresponding weights

for i, (fr, to) in enumerate(zip(to_graph['lagged_neg'], to_graph['c_neg'])):
  G3.add_edge(fr, to, weight = to_graph['share_of_transit'][i])
#  for i, (fr, to) in enumerate(zip(to_graph2['lagged_neg'], to_graph2['c_neg'])):
#  G3.add_edge(fr, to, weight=weights[i])

# Get sizes for transition to different node
to_graph = to_graph.set_index(['lagged_neg', 'c_neg'])
x = pd.DataFrame(G3.edges())
x.columns = ['lagged_neg', 'c_neg']
x = x.set_index(['lagged_neg', 'c_neg'])
to_graph = to_graph.reindex(x.index)
to_graph = to_graph.reset_index()

write_dot(G3,'graph.dot')
graph = pydot.graph_from_dot_file('graph.dot')

G = nx.nx_agraph.to_agraph(G) 

graph = pydot.Dot(graph_type='graph')
for i in range(3):
    # we can get right into action by "drawing" edges between the nodes in our graph
    # we do not need to CREATE nodes, but if you want to give them some custom style
    # then I would recomend you to do so... let's cover that later
    # the pydot.Edge() constructor receives two parameters, a source node and a destination
    # node, they are just strings like you can see
    edge = pydot.Edge("king", "lord%d" % i)
    # and we obviosuly need to add the edge to our graph
    graph.add_edge(edge)

vassal_num = 0
for i in range(3):
    # we create new edges, now between our previous lords and the new vassals
    # let us create two vassals for each lord
    for j in range(2):
        edge = pydot.Edge("lord%d" % i, "vassal%d" % vassal_num)
        graph.add_edge(edge)
        vassal_num += 1

# ok, we are set, let's save our graph into a file
graph.write_png('example1_graph.png')


# Plot
fig, ax = plt.subplots(1, figsize=(7,7))

pos = nx.spring_layout(G3,scale=0.5)

nx.draw(G3, pos,
            with_labels=True,
            arrows = True,
            node_color = color_map,
            node_size = 0.5,
            linewidths=0.5,
            label = node_types,
            width = to_graph['share_of_transit']
            )
#pos = nx.fruchterman_reingold_layout(G3)
#    nx.spring_layout(G3,
#            with_labels=True,
#            arrows = True,
#            node_color = color_map,
#            node_size = to_graph_no_transition['size']/100,
#            linewidths=0.5,
#            label = node_types,
#            width = to_graph2['size']/9000
#            )
ax = plt.gca()
ax.collections[0].set_edgecolor("black")
#ax.legend(scatterpoints=1)

markers = [plt.Line2D(
                    [0,0],[0,0],color=color, marker='o', linestyle=''
                    ) for color in dict_type_color.values()]
plt.legend(markers, dict_type_color.keys(), numpoints=1, loc = 3)
#    return to_graph2.sort('size', ascending=False)


