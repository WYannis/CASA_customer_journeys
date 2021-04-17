#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 08:26:01 2019

@author: vagrant
"""

from Levenshtein import distance
import numpy as np

#Deuxieme méthode renommage : pour chaque cluster, on tente d'en extraire la page la plus représentative
# du groupe. Pour cela, calcul de la matrice de distance de Levenshtein des pages de chaque cluster.
#(1 matrice par cluster). La page dont sum(dist_aux_autres_pages) est minimale est choisie comme représentante.

def pick_representants(clusters, features):
    
    list_of_rep = []
    for i in range(0, len(clusters)):
        
        list_pages_cluster= features.iloc[clusters[i]].index
        distance_matrix = [[0 for i in range(0, len(list_pages_cluster))] for i in range(0, len(list_pages_cluster))] 
        
        for l in range(0, len(list_pages_cluster)):
            
            for j in range(l+1, len(list_pages_cluster)):
                
                distance_matrix[l][j] = distance(list_pages_cluster[l], list_pages_cluster[j])
                distance_matrix[j][l] = distance_matrix[l][j]
        
        res_sum = [sum(x) for x in distance_matrix]
        idx_rep = np.argmin(res_sum)
        rep = list_pages_cluster[idx_rep]
        
        list_of_rep.append(rep)
        
    return list_of_rep



def pick_representants_spectral(labels, affinity_matrix2, df):
    
    list_of_rep = []
    
    for i in range(0, max(labels)+1):
        
        list_pages_cluster= df.loc[df['labels'] == i].index
        
        sum_dist_min = sum(affinity_matrix2[df.index.tolist().index(list_pages_cluster[0])])
        indice = df.index.tolist().index(list_pages_cluster[0])
        
        for page in list_pages_cluster[1:] :
            
                indice_temp = df.index.tolist().index(page)
                
                if sum(affinity_matrix2[indice_temp]) > sum_dist_min:
                    
                    sum_dist_min = sum(affinity_matrix2[indice_temp])
                    indice = indice_temp
        
        list_of_rep.append(df.index.tolist()[indice])
        
    return list_of_rep