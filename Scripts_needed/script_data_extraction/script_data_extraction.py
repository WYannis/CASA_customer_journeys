#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 12:56:09 2019

@author: vagrant
"""
import pathlib
import data_atinternet
import chrono

#######/!\ FORMAT DE LA DATE : 'YYYY-MM-DD' /!\ #######

def extraction(date_debut, date_fin, liste_param = ['d_date_hour_utc_event', 'd_source', 'd_page', 'd_uv_id', 'd_geo_city', 'm_visits']):
    DI = data_atinternet.DataATInternet()
    date_beg = date_debut
    date_end = date_fin
    site_id = DI.cfg['sites']['npc_prod']['site_id']
    fields = liste_param
    str_date = date_debut.split('-')
    str_date = str_date[2]+'.'+ str_date[1] +'.'+ str_date[0]
    pathlib.Path('D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/' + str_date).mkdir(parents=True, exist_ok=True) 
    filename = 'D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/' + str_date + '/AT-Internet {} NPC Prod.csv'.format(
        date_beg)
    folder_name = 'D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/' + str_date
    DI.download(site_id, fields, date_beg, date_end, filename)
    return filename, folder_name


