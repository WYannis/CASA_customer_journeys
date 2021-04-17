#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 11:51:29 2019

@author: vagrant
"""

import pandas as pd
from prefixspan import PrefixSpan
import numpy as np
import dash_core_components as dcc
import kmedoids
from Levenshtein import distance
from sklearn.metrics import silhouette_score


def delete_first_tag(name):
    name_tab = name.split("::")
    name_tab= name_tab[len(name_tab)-1].split('-')
    name_res=10*name_tab[len(name_tab)-1]       #répéter la même chaine 10 fois permet d'augmenter les distances
    return name_res

def diversity_score(liste):
    transitory_liste = []
    for x in liste :
        if x not in transitory_liste :
            transitory_liste.append(x)
    return len(transitory_liste)

def create_str(liste):
    phrase = ""
    
    for x in liste:
        
        if liste.index(x) == 0:
            
            phrase = x + " " 
            
        elif liste.index(x) == len(liste)-1:
            
            phrase = phrase + x
            
        else : 
            phrase =  phrase + " " + x + " "
    return phrase   



def find_clusters_names(labels, features):
    
    groups = [[] for i in range(0, max(labels)+1)]
    for i in range(0, max(labels)+1):
        groups[i] =  features[features['labels'] == i].index
        groups[i] = groups[i].tolist()
    
    for group in groups:
        for i in range(0, len(group)):
            group[i] = group[i].split("::")
            group[i] = group[i] + group[i][len(group[i])-1].split(" ")
            
    res= []
    for group in groups :
        prefix = PrefixSpan(group)
        prefix.maxlen = 4
        prefix.minlen = 4
        res.append(prefix.topk(5, filter = lambda patt, matches : diversity_score(patt) >= len(patt)))
                
    return [create_str(res[i][0][1]) for i in range(0, len(res))]





def compute_sankey(results_search, n_max_clusters, n_min_clusters, n_repet_assess_cluster_number, List_actions, day_selected):
    liste_resfinal = results_search
    
    webpages = [x[1] for x in liste_resfinal]
    flattened_webpages = [item for sublist in webpages for item in sublist]
    flattened_webpages = list(set(flattened_webpages))
    
    
    features = pd.DataFrame(index = flattened_webpages)
    
    distance_matrix = [[0 for i in range(len(flattened_webpages))] for i in range(0, len(flattened_webpages))]
    
    for i in range(0, len(flattened_webpages)):
        for j in range(i+1, len(flattened_webpages)):
            
            x_page_name = delete_first_tag(flattened_webpages[i])
            y_page_name = delete_first_tag(flattened_webpages[j])
            distance_matrix[i][j] = ((distance(x_page_name,y_page_name)))
            distance_matrix[j][i] = distance_matrix[i][j]
                    
    distance_matrix = np.array(distance_matrix)
    n_max = n_max_clusters
    n_min = n_min_clusters
    range_n_clusters = [i for i in range(n_min,n_max)]
    silhouette_avg_scores = [0 for i in range(n_min, n_max)]
    
    for j in range(0,n_repet_assess_cluster_number):
        
        for n_clusters in range_n_clusters:
            
            medoids, clusterer= kmedoids.kMedoids(distance_matrix, n_clusters)
            
            cluster_labels = [0 for i in range(len(distance_matrix))]
            
            for label in clusterer :
                for point_idx in clusterer[label]:
                    cluster_labels[point_idx] = label
                    
            silhouette_avg = silhouette_score(distance_matrix, cluster_labels, metric="precomputed")
            print("For n_clusters =", n_clusters,
              "The average silhouette_score is :", silhouette_avg)
            silhouette_avg_scores[range_n_clusters.index(n_clusters)]+=silhouette_avg
    
    silhouette_avg_scores = (np.array(silhouette_avg_scores)/(n_repet_assess_cluster_number)).tolist()
    
    cluster_number = range_n_clusters[silhouette_avg_scores.index(max(silhouette_avg_scores))]
    medoids, clusters = kmedoids.kMedoids(distance_matrix, cluster_number)
    
    labels = [0 for i in range(len(distance_matrix))]
    
    for label in clusters :
        for point_idx in clusters[label]:
            labels[point_idx] = label
    features['labels'] = labels
    data_nodes = find_clusters_names(labels,features)
        
    label_to_process = 0
    
    for x in data_nodes :
        if "devis" in x :
            label_to_process = data_nodes.index(x)
        else :
            label_to_process =0
    
    ##Compute the clusterized Sankey diagramm -###########################################################
    
    
    #Initial computation with every nodes and every flux
    
    colors = []
    sources = []
    targets = []
    values= []
    links = []
    
    for sublist in List_actions:
        for i in range(0,len(sublist)-1):
            src_webpage = sublist[i]
            trg_webpage = sublist[i+1]
            if (src_webpage in flattened_webpages) and (trg_webpage in flattened_webpages):
                src_label = features.loc[src_webpage,'labels']
                trg_label= features.loc[trg_webpage, 'labels']
                
                
                if (src_label, trg_label) not in links:
                                          
                    links.append((src_label, trg_label))
                    values.append(1)
                    sources.append(src_label)
                    targets.append(trg_label)
                    
                else:
                    
                    values[links.index((src_label, trg_label))]+=1
    
    
    #clean up the Sankey a bit: remove bidirectional edges between immediately close nodes
     
    cleaned_values=[]
    cleaned_sources = []
    cleaned_targets = []
    sum_in_links = [0 for i in range(max(labels)+1)]
    sum_out_links = [0 for i in range(max(labels)+1)]
    
    for (src_label, trg_label) in links:
        if values[links.index((src_label, trg_label))] > 100:
            
                    
            if (trg_label, src_label) in links:
                
                if values[links.index((src_label, trg_label))] >= values[links.index((trg_label, src_label))]:
                    
                    
                    cleaned_values.append(values[links.index((src_label, trg_label))])
                    cleaned_sources.append(src_label)
                    cleaned_targets.append(trg_label)
                    sum_in_links[trg_label]+= values[links.index((src_label, trg_label))]
                    sum_out_links[src_label] += values[links.index((src_label, trg_label))]
                
            
            else:
                
                cleaned_values.append(values[links.index((src_label, trg_label))])
                cleaned_sources.append(src_label)
                cleaned_targets.append(trg_label)
                sum_in_links[trg_label]+= values[links.index((src_label, trg_label))]
                sum_out_links[src_label] += values[links.index((src_label, trg_label))]
    
    
    cleaned_val_V2 = []
    cleaned_src_V2 = []
    cleaned_trg_V2= []
    rate = 0.10
        
    for i in range(0,len(cleaned_values)):
        if (cleaned_values[i] > rate*sum_in_links[cleaned_targets[i]] and cleaned_values[i] > rate*sum_out_links[cleaned_sources[i]] and (cleaned_sources[i]!=label_to_process or cleaned_targets[i]==label_to_process)):
            cleaned_val_V2.append(cleaned_values[i])
            cleaned_src_V2.append(cleaned_sources[i])
            cleaned_trg_V2.append(cleaned_targets[i])
        
        
    
    
    #plot the final Sankey
                    
    for i in range (0, len(labels)):
        color_array = list(np.random.choice(range(256), size = 3))
        colors.append("rgba(" + str(color_array[0]) + ", " + str(color_array[1]) + ", " + str(color_array[2]) + ", 0.8 )")
                
    
    data_trace = dict(
        type='sankey',  
        orientation = "h",
        valueformat = ".0f",
        valuesuffix = " logs",
        textfont = dict(
                size = 12
        ),
        node = dict(
          pad = 22,
          thickness = 15,
          line = dict(
            color = "black",
            width = 0.5
          ),
          label =  data_nodes
        ),
        link = dict(
          source =  cleaned_src_V2,
          target =  cleaned_trg_V2,
          value =  cleaned_val_V2,
          label =  ["" for x in cleaned_val_V2]
      ))                 
    
    layouts = dict(
        title = "Dynamique du traffic pertinent sur le site credit-agricole.fr le "+ str(day_selected) +" - clustering fonctionnel",
        font = dict(
          size = 10
        ),
        width = 1750,
        height = 800
    )   
    
    res = dcc.Tab(id='Graph_function', children =[
            
            
            dcc.Graph(
                    id = 'Sankey_function',
                    figure = {
                            'data' : [data_trace],
                            'layout' : layouts
                            }                                                    
                    )                                                
            ])
    
    
    return res