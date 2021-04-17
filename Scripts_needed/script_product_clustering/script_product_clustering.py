#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:33:08 2019

@author: vagrant
"""

import dash_core_components as dcc
import dash_html_components as html
from unionfind import unionfind
import json

def generate_sub_matrix(global_matrix, list_indices):
    
    affinity_matrix=[[0 for j in range(0,len(list_indices))] for i in range(len(list_indices))]
    
    for i in range(0,len(list_indices)):
        affinity_matrix[i] = [global_matrix[list_indices[i]][j] for j in list_indices]
        
    return affinity_matrix


def product_clustering(list_pages_tot, values, sources, targets, global_matrix, day_selected):    
    
    #compute each subgraphs -------------------------------------------------------------------
    
    
    total_flow = sum(values)        
    
    u = unionfind(len(list_pages_tot))
    for i in range(0, len(sources)) :
        u.unite(sources[i],targets[i])
    
    
    subgraphs = u.groups()
    number_of_subgraphs = len(subgraphs)
    print(number_of_subgraphs)
    
    global list_subsources
    list_subsources=[]
    list_subvalues=[]
    list_subtargets=[]
    
     
    for graph in subgraphs :
        
        sub_sources =[]
        sub_values = []
        sub_targets = []
        
        for j in range(0, len(sources)):
            
            source = sources[j]
            if source in graph:
                
                sub_sources.append(source)
                sub_targets.append(targets[j])
                sub_values.append(values[j])
    
        list_subsources.append(sub_sources)
        list_subvalues.append(sub_values)
        list_subtargets.append(sub_targets)
    
    
    
    #    data_traces = [0 for i in range(len(list_subsources))]
    value_share = [0 for i in range(len(list_subsources))]
    
    for i in range(0,len(list_subsources)): 
        if list_subsources[i] != [] :
            z = list_subvalues[i]
            
            value_share[i] = ((sum(z)*1.0)/total_flow) * 100
    
    #end of computation of the subgraphs : now working on the UI --------------------------------------- 
          
    list_of_affinity_matrix = [[] for i in range(len(list_subsources))]    
    sublists_pages = [[] for i in range(len(list_subsources))]   
    
    
    
    list_of_links = [[] for i in range(len(list_subsources))]    
                     
######      define the function which creates one tab for each subgraph    #############
            
    def multiple_tabs(number, list_subsources = list_subsources):
        res = []
        
        sublists_pages = [[] for i in range(len(list_subsources))] 
        list_of_affinity_matrix = [[] for i in range(len(list_subsources))] 
        for n in range(0,number):
            
            if value_share[n] >= 2:
            
                
                subgraph = (subgraphs[n],list_subsources[n], list_subtargets[n], list_subvalues[n])
                
                list_pages = [list_pages_tot[x] for x in subgraph[0]]
    
                sublists_pages[n] = list_pages

                src = [list_pages.index(list_pages_tot[x]) for x in subgraph[1]]
                tar = [list_pages.index(list_pages_tot[x]) for x in subgraph[2]]
                
                list_of_links[n]= [(list_pages[src[j]] , list_pages[tar[j]]) for j in range(len(src))]
                
                values = subgraph[3]
                
                list_of_affinity_matrix[n] = generate_sub_matrix(global_matrix, subgraph[0])
                
                data_trace = dict(
                    type='sankey',  
                    orientation = "h",
                    valueformat = ".0f",
                    valuesuffix = " logs",
                    node = dict(
                      pad = 15,
                      thickness = 12,
                      line = dict(
                        color = "black",
                        width = 0.5
                      ),
                      label =  list_pages
                    ),
                    link = dict(
                      source =  src,
                      target =  tar,
                      value =  values,
                      label =  ["" for x in values]
                  ))                 
                                  
                layout =  dict(
                    title = "Dynamique du traffic pertinent sur le site credit-agricole.fr le " + str(day_selected)+ " - subgraph numéro " + str(i) + '<br>' + 'Proportion du traffic total : ' + str(value_share[n]) + '%',
                    font = dict(
                      size = 10
                    ),
                    width = 1800,
                    height = 800
                )
                     
                res.append(dcc.Tab(label = 'Sous-graphe numéro '+ str(n), children = [
                                             
                         dcc.Graph(
                                id='Sankey'+str(n),
                                figure={
                                    'data': [
                                        data_trace
                                    ],
                                    'layout': layout
                                }
                            ),
                            html.Div([html.Span("Slide to change cluster number", style = {"text-align" : "center", 'padding' : 10}, className = 'row'),
                            dcc.Slider(
                                id='cluster-slider-' +str(n),
                                min=2,
                                max=len(list_pages),
                                value=len(list_pages),
                                marks={str(i) : str(i) for i in range(2, len(list_pages)+1, 2)},
                                step=None
                                
                            )
                            ], style = {"display": "block", "margin-left": "auto", "margin-right": "auto",
                                           "width": "70%", "padding": 20})                            
                        ])
                        )
            
        
        return (res, sublists_pages, list_of_affinity_matrix)    
          
    res, sublists_pages, list_of_affinity_matrix  = multiple_tabs(len(list_subsources))   
    
    list_of_subgraph_indexes=[]
    for i in range(0, len(value_share)):
        if value_share[i] > 2:
            list_of_subgraph_indexes.append(i)     
               
    INTERMEDIATE_RESULTS = [sublists_pages, list_of_affinity_matrix, list_of_links, list_subsources, value_share, list_of_subgraph_indexes]             

    return res, json.dumps(INTERMEDIATE_RESULTS)


