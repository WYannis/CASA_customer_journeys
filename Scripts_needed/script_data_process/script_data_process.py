#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 13:33:08 2019

@author: vagrant
"""

import pandas as pd
from prefixspan import PrefixSpan
import datetime 
pd.set_option('display.max_columns', None)
import numpy as np

def generate_global_matrix(List_actions, list_pages):
    
    distance_matrix = [[0 for j in range(0,len(list_pages))] for i in range(len(list_pages))]
    
    for l in List_actions:
 
        for i in range(0,len(l)):
            if rename(l[i]) in list_pages :
                for j in range(i+1, len(l)):
                     if rename(l[j]) in list_pages:   
                            distance_matrix[list_pages.index(rename(l[i]))][list_pages.index(rename(l[j]))]+=1/((j-i)*1.0)
    
    distance_matrix = np.array(distance_matrix) + 1
    distance_matrix = 1/distance_matrix
    delta = 0.4
    distance_matrix = np.exp(- distance_matrix ** 2 / (2. * delta ** 2))
    
    return distance_matrix


def diversity_score(liste):
    transitory_liste = []
    for x in liste :
        if x not in transitory_liste :
            transitory_liste.append(x)
    return len(transitory_liste)
    
 

def compute_transitions_list(result_search):
    res=[]
    for count, pattern in result_search:
        for i in range(0, len(pattern)-1):
            x=pattern[i:i+2]
            if x not in res:
                res.append(x)
    return res


def rename(tag):
    tag_split = tag.split('::')
    return tag_split[len(tag_split)-1]


def preprocess_dataset(path_):
    
    #Extraction données------------------------------------------------------------------------------
    
    path = path_
    date_column = 'Date-heure UTC (événement)'
    action_column = 'Pages'
    identity_col = 'Visiteurs uniques ID'
    
    
    
    dataset = pd.read_csv(path, sep = ';', parse_dates = [date_column])
    
    dataset[date_column] = pd.to_datetime(dataset[date_column], errors='coerce')
    dataset = dataset.dropna(subset=[date_column])
    
    dataset = dataset[dataset[action_column] != '-']
    dataset.index = dataset[date_column]
    dataset.drop(columns= date_column, inplace = True)
    dataset.sort_index( ascending = True, inplace =True)
    
    #'particulier::compte::compte-conseil univers de besoin'
    valeurs_interdites = ['particulier::acces-CR::acces-CR-store locator trouver ma CR 50', 'particulier::particulier-accueil particuliers et BP']
    
    dataset_after = dataset[~dataset[action_column].isin(valeurs_interdites)]
    person_list = dataset_after[identity_col].unique()
            
    print("Le nombre de personnes répertoriées est : " + str(len(person_list)))
    
    #liste_pages_dataset = dataset[action_column].unique().tolist()
    #comparaisons du nombre de visiteurs avant/ après : 77406 - 24682 = 52724 personnes 
    #52724 personnes ne visitent que les pages de valeurs-interdites ....
    
    List_actions=[]
    
    #start = time.time()
    
    #parameter authorized_session_time defines the maximal inactivity time before we consider the client
    #opened two distincts sessions
    authorized_inactivity_time = datetime.timedelta(minutes = 30)
    
    for i in range(0, len(person_list)):
        
        personne = person_list[i]
        subdata = dataset_after[dataset_after[identity_col] == personne]
        start = 0
        
        for j in range(0, len(subdata.index)-1):
            
            duree = subdata.index[j+1]- subdata.index[j]
    
            if duree > authorized_inactivity_time: 
                
                actions = subdata[action_column].iloc[start:j+1].tolist()
                start = j+1 
                List_actions.append(actions)
                
        actions = subdata[action_column].iloc[start:len(subdata.index)].tolist()
        List_actions.append(actions)
    
    
    
    
    #Premier coup de PrefixSpan pour trouver les parcours pertinents---------------------------------------
    
    
    first_search = PrefixSpan(List_actions)
    first_search.min_len = 2
    first_search.max_len = 7
    results_search1 = first_search.frequent(15, filter = lambda patt, matches : diversity_score(patt) >= len(patt))
    
    results_search1.sort(key=lambda x:-x[0])
    
    #Deuxieme passage pour obtenir la liste des transitions de taille 2 et leurs effectifs---------------------
    
    
    second_search = PrefixSpan(List_actions)
    second_search.min_len = 2
    second_search.max_len = 2
    filter_list = compute_transitions_list(results_search1)
    results_search2 = second_search.frequent(5, filter = lambda patt, matches : patt in filter_list)
    
    results_search2.sort(key=lambda x:-x[0])
    
    #Tracé du Sankey -------------------------------------------------------------------------------------
    
    liste_resfinal = results_search2
    
    
    labels = []
    sources = []
    targets = []
    values= []
    links = []
    
    
    #A link only appears in the graph if it constitutes more than rate% of the incoming/outgoing traffic of the
    #two nodes involved in the link
    rate = 0.11    
    
    for match in liste_resfinal:
        
        if len(match[1]) == second_search.minlen :
            pattern = match[1]
        else:
            pattern = match[1][len(match[1])-2:len(match[1])]
        
        for label in pattern:
            renamed = rename(label)
            if renamed not in labels :
                labels.append(renamed)
            if match[1].index(label) < len(match[1])-1:
                targetted = rename(match[1][match[1].index(label)+1])
                res_exit = 0
                res_entry = 0
                res_incoming = 0
                res_ongoing = 0
                if labels.index(renamed) in targets :
                
                    for i in range(0, len(targets)) :
                        x = targets[i]
                        if x == labels.index(renamed):
                            res_exit+= values[i]
                            
                if labels.index(renamed) in sources:
                    
                    for i in range(0, len(sources)):
                        if sources[i] == labels.index(renamed):
                            res_incoming += values[i]
                            
                if  targetted in labels :
                    
                    if labels.index(targetted) in sources:
                    
                        for i in range(0, len(sources)) :
                            x = sources[i]
                            if x == labels.index(targetted):
                                res_entry+= values[i]
                                
                    if labels.index(targetted) in targets:
                        
                        for i in range(0, len(targets)) :
                            if targets[i] == labels.index(targetted):
                                res_ongoing+= values[i]
                            
                
                if (renamed, targetted) not in links :
                    
                    if match[0] > rate*res_exit and match[0] > rate*res_entry and match[0] > rate*res_ongoing and match[0] > rate*res_incoming:
                            
                            
                        if ((targetted, renamed) in links ) :
                            
                            if values[links.index((targetted, renamed))] <= match[0]:
                                
                                links.append((renamed, targetted))
                                sources.append(labels.index(renamed))
                                if targetted in labels :
                                    targets.append(labels.index(targetted))
                                else:
                                    labels.append(targetted)
                                    targets.append(labels.index(targetted))
                                sources.pop(links.index((targetted, renamed)))
                                targets.pop(links.index((targetted, renamed)))
                                values.pop(links.index((targetted, renamed))) 
                                links.pop(links.index((targetted, renamed)))
                                values.append(match[0])
                                
                                
                        else :
                            
                            links.append((renamed, targetted))
                            sources.append(labels.index(renamed))
                            if targetted in labels :
                                targets.append(labels.index(targetted))
                            else:
                                labels.append(targetted)
                                targets.append(labels.index(targetted))
                            values.append(match[0])
                            
                            
                else :
                    
                    values[links.index((renamed, targetted))] +=match[0]
    
    global_matrix = generate_global_matrix(List_actions, labels )
    
    return [labels, links, values, global_matrix, liste_resfinal, List_actions]


#pk.dump(labels, open('Listedespages.pkl', 'wb'))
#pk.dump(links, open('Listofedges.pkl', 'wb'))
#pk.dump(values, open('Listofvalues.pkl', 'wb'))

#pk.dump((subgraphs[23],list_subsources[23], list_subtargets[23], list_subvalues[23]), open('subgraphtotestonclustering.pkl','wb'))