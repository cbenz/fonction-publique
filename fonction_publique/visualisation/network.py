import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def plot_network(transition_w_outside = True):
    load_path = 'M:/CNRACL/output/'
    
    # List of grades that are in the AT corps
    list_neg_AT = ['0793', '0794', '0795', '0796']
    list_neg_AA = ['0791', '0792', '0014', '0162']
    list_neg_AS = ['0839', '0840','0841']
    
    # Read data
    df_AT = pd.read_table(os.path.join(load_path, "corpsAT_2011_2015.csv"),
                          delimiter=",")
    df_AA = pd.read_table(os.path.join(load_path, "corpsAT_2011_2015.csv"),
                          delimiter=",")
    df_ES = pd.read_table(os.path.join(load_path, "corpsAT_2011_2015.csv"),
                          delimiter=",")
    
    df = df_AT.append(df_AA).append(df_ES)
    df = df.sort(['ident'])
    df = df.drop_duplicates() # dup appear when merging df from different corps
    
    # Filter out observations with null c_neg
    df = df[df.c_neg.notnull()]
    df = df.set_index(['ident', 'annee'])
    
    # Create lags for code neg
    df = df.sort_index()
    df['lagged_neg'] = df.groupby(level=0)['c_neg'].shift(1); df
      
    # Rebalance panel in order to get transitions to outside
    df = df.reset_index()
    idents = df['ident'].unique()
    all_dates = df['annee'].unique()
    
    idents_full = np.array([[y]*len(all_dates) for y in idents]).flatten()
    dates_full = all_dates.tolist() * len(idents)
    
    balanced_panel = pd.DataFrame({'ident': idents_full, 'annee': dates_full})
    df = balanced_panel.merge(
            df, how='left', on=['ident', 'annee']).fillna('Out')
      
    # Create df of number of transitions for each couple (c_neg, lagged_neg)
    to_graph = df.groupby(
            ["lagged_neg", "c_neg"]).size().reset_index(name='size')
    to_graph = to_graph.sort('size', ascending = False)
    #to_graph = to_graph[15000 < to_graph['size']]
    
    # Create nodelist as list of unique code grades
    nodelist = set(
            to_graph['lagged_neg'].unique(
                    ).tolist() + to_graph['c_neg'].unique().tolist()
            )
    
    # Define the weights, which will be used as attributes of the edges
    weights = pd.to_numeric(to_graph['size'].reset_index()['size'].tolist())
    
    ###### plot without lagged_neg = c_neg
    mask = to_graph['lagged_neg'] == to_graph['c_neg']
    to_graph2 = to_graph[~mask] 
    to_graph2 = to_graph2[
            1000 < to_graph2['size']
            ]
    
    nodelist = set(
            to_graph2['lagged_neg'].unique(
                    ).tolist() + to_graph2['c_neg'].unique().tolist()
            )
    
    weights = pd.to_numeric(to_graph2['size'].reset_index()['size'].tolist())
    
    # Initialize a directed graph
    G3 = nx.DiGraph()
    
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
#    dict_nodes_types = {'AT': list_neg_AT,
#                        'AS': list_neg_AS,
#                        'AA': list_neg_AA,
#                        'autres': autres}
    node_colors = ['magenta', 'cyan', 'yellow', 'red']
    dict_type_color = dict(zip(node_types, node_colors))
    
    # Get size for transition to same node
    to_graph_no_transition = to_graph[to_graph['lagged_neg'] == to_graph['c_neg']]
    to_graph_no_transition = to_graph_no_transition.set_index('c_neg')
    to_graph_no_transition = to_graph_no_transition.loc[G3.nodes()] # reorder the size in nodes order (important)
    
    # Add edges with corresponding weights
    for i, (fr, to) in enumerate(zip(to_graph2['lagged_neg'], to_graph2['c_neg'])):
      G3.add_edge(fr, to, weight=weights[i])
    
    # Get sizes for transition to different node
    to_graph2 = to_graph2.set_index(['lagged_neg', 'c_neg'])
    x = pd.DataFrame(G3.edges())
    x.columns = ['lagged_neg', 'c_neg']
    x = x.set_index(['lagged_neg', 'c_neg'])
    to_graph2 = to_graph2.reindex(x.index)
    to_graph2 = to_graph2.reset_index()
    
    # Plot
    fig, ax = plt.subplots(1, figsize=(7,7))
    
    nx.draw_circular(G3,
                with_labels=True,
                arrows = True,
                node_color = color_map,
                node_size = to_graph_no_transition['size']/100,
                linewidths=0.5,
                label = node_types,
                width = to_graph2['size']/6000
                )
    ax = plt.gca()
    ax.collections[0].set_edgecolor("black")
    #ax.legend(scatterpoints=1)
    
    markers = [plt.Line2D(
                        [0,0],[0,0],color=color, marker='o', linestyle=''
                        ) for color in dict_type_color.values()]
    plt.legend(markers, dict_type_color.keys(), numpoints=1, loc = 3)
    return 



