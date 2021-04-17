#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 12:30:22 2019

@author: vagrant
"""

from sys import path 
path.append('Scripts_needed/script_data_process')
path.append('Scripts_needed/script_data_extraction')
path.append('Scripts_needed/script_function_clustering')
path.append('Scripts_needed/script_product_clustering')
path.append('Scripts_needed/')



######## IMPORTATION OF FUNDAMENTAL PRE-INSTALLED PACKAGES################################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from sklearn.cluster import SpectralClustering
import base64
import json
import numpy as np
#from app import app
import os
import datetime
import pickle as pk
import pandas as pd
import time


################### IMPORTATION OF SCRIPTS USED IN MAIN BODY ########################################################"##

from Deuxiememéthoderenommage import pick_representants_spectral
import script_function_clustering as sfc
import script_data_process as sdp
import script_data_extraction as sde
import script_product_clustering as spc





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    
#https://codepen.io/chriddyp/pen/bWLwgP


liste_dates_litterale = os.listdir('Datasets_csv')
liste_dates = []
for x in liste_dates_litterale:
    x = x.split('.')
    x = datetime.date(day = int(x[0]), month = int(x[1]),year = int(x[2]))
    liste_dates.append(x)
    
liste_dates.sort()        
possible_days = [y.strftime("%d-%B-%Y") for y in liste_dates]

print(possible_days)
print(liste_dates)





app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True

#CACHE_CONFIG = {
#    # try 'filesystem' if you don't want to setup redis
#    'CACHE_TYPE': 'redis',
#    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'localhost:6379')
#}
#
#cache = Cache()
#cache.init_app(app.server, config=CACHE_CONFIG)

image_filename = "Images/paths.png"
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
image_filename2 = "Images/CALogo.svg"
encoded_image2 = base64.b64encode(open(image_filename2, 'rb').read())
image_filename3 = "Images/happypersons.png"
encoded_image3 = base64.b64encode(open(image_filename3, 'rb').read())



app.layout = html.Div([
        html.H1('Clustering interactif des parcours webs', style = { 'textAlign' : 'center', 'margin' : '48px 0', 'fontFamily': 'fantasy'}),
        dcc.Tabs(id = "tabs", children = [
                
                dcc.Tab(label = 'Accueil', children = [
                html.Div(id = "seeable_when_none", children = [
                html.H2('''Choisissez vos paramètres de clustering : '''),
               
                html.Div([
                     html.Div([
                             html.Span('''Jour à analyser : '''),
                             dcc.Dropdown(
                                id='select_day',
                                options=[{'label': i, 'value' : i} for i in possible_days],
                                value= None,
                                placeholder="Select a day",
                                style = {'width' : '300px'  }
                                ),
                              html.Div([
                                    html.Div(id = 'add_day_form_00', children = [
                                        html.Img(src='/assets/goback.svg', id = "go_back_button", n_clicks = 0, style={'width':'auto', 'height' : '40px', 'margin-right': '10px', 'vertical-align' : 'bottom'}),            
#                                        src ="https://visualpharm.com/assets/956/Go%20Back-595b40b75ba036ed117d8029.svg"
                                        dcc.DatePickerSingle(
                                           id = "date_picker",
                                           min_date_allowed = datetime.datetime(2019,2,1),
                                           max_date_allowed=datetime.date.today()-datetime.timedelta(days=1),
                                           initial_visible_month = datetime.date.today()-datetime.timedelta(days=1),
                                           date = None,
                                           placeholder="Select a day",
                                           with_portal = True,
                                           display_format = 'D-MMM-Y'
                                                
                                        ),
                                        html.Button(id = 'extract_data', n_clicks=0, children="Lancer l'extraction", style = { 'display' : 'block', 'background-color' : '#F700CA', 'margin-top' : '5px', 'color' : 'white' })             
                                    ], style = {'display' : 'block'}),
                                    
                                    html.Div(id = 'add_day_form_01',children = [
                                        html.Button(id='add_day', n_clicks=0, children = 'Ajouter un jour absent de la liste', style = { 'display' : 'block', 'background-color' : '#25AEEE', 'margin-top' : '10px' })                                                                                                                                  
                                    ], style = {'display' : 'block'})                                                                                                  
                                
                                ]),
                            
                     ],style = {'width' : '100%'}),
                     html.Div([
                            html.Span('''Méthode de clustering : '''),
                            dcc.Dropdown(
                                    id='select_method',
                                    options=[{'label' : 'Par produit', 'value' : 'product'},
                                    {'label' : 'Par fonction', 'value' : 'function'}],
                                    value = None,
                                    placeholder = 'Select a method',
                                    style = {'width' : '300px' }
                                    )       
                    ], style = {'width' : '100%', 'margin-left' : '100px'}),
                     html.Button(id='submit-button', n_clicks=0, children='Submit', style = { 'display' : 'inline-block', 'background-image': 'url("https://omaharentalads.com/images/shutterstock-vector-1.png")','background-size': '118px 40px', 'background-position' : 'center','margin-left' : '150px', 'margin-top': '22px'})

                ], style={'display': 'flex', 'position' : 'absolute', 'left':'20%'}),
                    
                html.Div(id = "part_2", children=[
                        
#                        html.Span(id= 'validation_message', children='''Jour ajouté avec succès ! ''', style = {'display': 'none', 'font-weight' : 'bold' , 'color' : 'red', 'text-size' : '24px'}),
                        
            dcc.Loading(
                id="extraction_loading",
                children=[
                    html.Div(id = "validation_message", children = [
                            html.I( className='fas fa-check-square', style = {'height' : '34px' ,'color' : 'green', 'width' : 'auto', 'vertical-align' : 'bottom'}),
                            html.P(children='''Jour ajouté avec succès ! ''', style = {'font-weight' : 'bold' , 'color' : '#2BBE0D', 'font-size' : '24px'})                                                                                                                                                                                                   
                            
                            ], style = {'display' : 'none'}),

                    html.Div(id = 'error_message', children = [
                        html.Img(id="error_img", src="/assets/error.svg", style = {'height' : '34px' , 'width' : 'auto', 'vertical-align' : 'bottom'}),
                        html.P(children = '''Jour déjà extrait !''', style= {'font-weight' : 'bold', 'color' : '#F34425', 'font-size' : '24px'})
                        
                        
                        
                        ], style = {'display' : 'none'}),
                                                                                                                                
                    html.Div(id="loading-output", children=[])],
                                type='graph' 
                                
                                )],    

                  style={'position': 'absolute', 'width':'90%','margin-top':'130px','text-align':'center', 'margin-bottom': '40px'}),
              

                
                                          
                html.Div([
    
        html.Img(src = 'data:image/png;base64,{}'.format(encoded_image.decode()), alt = "paths_icon", width = "250", height = "250"),
        html.Img(src = 'data:image/png;base64,{}'.format(encoded_image2.decode()), alt = "cash_icon", width = "250", height = "250"),
        html.Img(src = 'data:image/png;base64,{}'.format(encoded_image3.decode()), alt = "happy_icon", width = "250", height = "250")
        ], style = {   'margin-top' : '300px', 'display': 'inline-block', 'position' : 'absolute' , 'left' : '25%','align-items' : 'center'})
                         
          ])
     ])
                
        ]),
    html.Div( id ='tabs_2_div' , children = [
    dcc.Tabs(id= "tabs2", style = {'margin-top' : '200px'}),
    html.Div(id='intermediate_results', style={'display': 'none'}),
    html.Div(id = 'signal_cache', children=json.dumps(False), style = {'display' : 'none'}),
    html.Div(id='last_day_picked' , style = {'display' : 'none'})
    ])
    ])



####################################   CALLBACKS FOR THE EXTRACTION PROCESS/ CALL TO AT-INTERNETAPI  ########################################


@app.callback(  [Output('add_day_form_00','style'),Output('add_day_form_01', 'style'), Output('select_day' , 'style'), Output('date_picker', 'date')],
              
              [ Input('add_day','n_clicks'), Input('go_back_button', 'n_clicks')]
              )


def date_picker_popup(n1,n2):

    if (n1-n2)==0:
        style_01 = {'display' : 'block' }
        style_00 = {'display' : 'none'}
        style_02 = style_01
        return style_00, style_01, style_02, None
    
    else: 
        style_00 = {'display' : 'block' }
        style_01 = {'display' : 'none'}
        style_02 = style_01
        return style_00, style_01, style_02, None


@app.callback( [Output('validation_message','style'), Output("loading-output", "style"), Output('signal_cache', 'children')],
              [Input('extract_data' ,'n_clicks'), Input('go_back_button', 'n_clicks')],
              [State('date_picker','date')]
        )


def extract_data(n_clicks, n2, day_selected):
    ctx = dash.callback_context
    if (day_selected == None and n_clicks == 0) or (ctx.triggered[0]['prop_id']=="go_back_button.n_clicks") :
        
        return {'display' : 'none'}, None, json.dumps(False)    
 
    elif day_selected is not None and n_clicks >0 : 
        
        date_test = datetime.datetime.strptime(day_selected, '%Y-%m-%d').strftime('%d-%B-%Y')
        print("la date test est : " + date_test)
        print("possible_days est : "  )
        print(possible_days)
        
        if date_test not in possible_days : 
            
            print(day_selected)
            date_debut = day_selected
            date_fin = (datetime.datetime.strptime(day_selected, '%Y-%m-%d')+datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            time.sleep(4)               ##line used to simulate a time-consuming event without actually doing any data extraction
#            filepath, folderpath = sde.extraction(date_debut, date_fin)
            
            
#            labels, links, values, global_matrix, liste_resfinal, List_actions = sdp.preprocess_dataset(filepath)     ### results : [List_actions, labels, links, values] ###
#            
#            pk.dump(labels, open(folderpath+'/Listedespages.pkl', 'wb'))
#            pk.dump(links, open(folderpath +'/Listofedges.pkl', 'wb'))
#            pk.dump(values, open(folderpath+'/Listofvalues.pkl', 'wb'))
#            pk.dump(global_matrix, open(folderpath+'/Global_matrix.pkl','wb'))
#            pk.dump(liste_resfinal, open(folderpath+'/Listeresfinal.pkl', 'wb'))
#            pk.dump(List_actions, open(folderpath+'/Listactions.pkl','wb'))
#            
#            possible_days.append(date_test)
#            possible_days.sort(key = lambda date: datetime.datetime.strptime(date, '%d-%B-%Y'))
#            liste_dates.append(datetime.datetime.strptime(date_test, '%d-%B-%Y'))
            # liste_dates.sort()
            return None, None, json.dumps(False)  
        else:
            return {'display' : 'none'}, None, json.dumps(True)
                    
    else: 
        
        return {'display' : 'none'}, None, json.dumps(True)

@app.callback(Output('error_message', 'style'),
               [Input('signal_cache','children')],
               [State('date_picker','date')])

def display_error(signal, date_selected):
    signal = json.loads(signal)
    print("Le boolean signal est : " + str(signal))
    if signal :
        return None
    else:
        return {'display' : 'none'}


@app.callback(Output('select_day', 'options'),
              [Input('go_back_button', 'n_clicks')])

def update_options(n):
    return [{'label': i, 'value' : i} for i in possible_days]


@app.callback(Output('tabs_2_div', 'style'),
              [Input('extract_data', 'n_clicks'), Input('submit-button' ,'n_clicks')])


def display_main_page(n1, n2):
    ctx = dash.callback_context
    print("FUUUUCK" + str(ctx.triggered[0]['prop_id']))
    if ctx.triggered[0]['prop_id']=="extract_data.n_clicks":
        return {'display' : 'none'}
    else :
        return None


####################################################################################################################################



#@cache.memoize()  


@app.callback([Output('tabs2', 'children'),Output('intermediate_results','children'), Output('last_day_picked','children')],
              [Input('submit-button', 'n_clicks')],
            [State('select_day', 'value'), State('select_method', 'value')])

def update_tabs(n_clicks, day_selected, method_selected):
    
    
    
    ########################### GLOBAL PART IN COMMON IN BOTH METHODS#####################################
    
    if day_selected != None :
            
        day_selected_litteral = liste_dates[possible_days.index(day_selected)].strftime("%d.%m.%Y")
        print("LE JOUR C'EST " + day_selected_litteral)
        path_list_pages = "D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Listedespages.pkl"
        path_links = "D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Listofedges.pkl"
        path_values ="D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Listofvalues.pkl"
        path_global_matrix = "D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Global_matrix.pkl"
        path_listeresfinal ="D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Listeresfinal.pkl"
        path_Listactions = "D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Datasets_csv/" + day_selected_litteral + "/Listactions.pkl" 
        
        #elements directly coming from the whole Sankey graph (before it is divided in separate subgraphs):
        global list_pages_tot
        global links
        global values
        
        list_pages_tot = pk.load(open(path_list_pages, 'rb'))
        links = pk.load(open(path_links, 'rb'))
        values = pk.load(open(path_values, 'rb'))
        sources = [list_pages_tot.index(x[0]) for x in links]
        targets = [list_pages_tot.index(x[1]) for x in links]
        global_matrix = pk.load(open(path_global_matrix, 'rb'))
        liste_resfinal = pk.load(open(path_listeresfinal, 'rb'))
        List_actions =     pk.load(open(path_Listactions, 'rb'))                                  
        
        ###################### FIRST CLUSTERING APPROACH ################################################"
        
        
        if (method_selected == 'product'):
            
            res1, res2  =     spc.product_clustering(list_pages_tot, values, sources, targets, global_matrix, day_selected_litteral)        
            return res1, res2, json.dumps(day_selected_litteral)
                
        
        #################################### SECOND CLUSTERING APPROACH ###########################################################
                
        elif method_selected == 'function' :
        
            return sfc.compute_sankey(liste_resfinal, 11, 4, 30, List_actions, day_selected_litteral), json.dumps(([[],[],[],[],[],[]])), json.dumps(day_selected_litteral)
        
        
        
        
        
        
    else :
        
        return None, json.dumps([[],[],[],[],[],[]]), json.dumps("")
                         


#intermediate_results = pk.load(open('STEP2_RESULTS', 'rb'))  
#sublists_pages = intermediate_results[0]
#list_of_links = intermediate_results[2]
#list_of_affinity_matrix = intermediate_results[1]
#value_share = intermediate_results[4]
#list_of_subgraph_indexes = intermediate_results[5]
#print(list_of_subgraph_indexes)

max_number_subgraphs = 100

for i in range(max_number_subgraphs):
    @app.callback(
        Output('Sankey' + str(i), 'figure'),
        [Input('cluster-slider-' + str(i), 'value'), Input('intermediate_results','children'), Input('last_day_picked', 'children')],
        )
    
    def update_figure(cluster_number, intermediate_results, last_day, i=i): 
        
        intermediate_results =json.loads(intermediate_results)
        sublists_pages = intermediate_results[0]
        list_of_links = intermediate_results[2]
        list_of_affinity_matrix = intermediate_results[1]
        value_share = intermediate_results[4]
        
        if (i not in intermediate_results[5]):
            return None
        #initialize a dataset --> not a global varibale because would cause issues if app opened
        # on several threads
        
        #print(sublists_pages)
        df = pd.DataFrame(sublists_pages[i])
        df.index = df.iloc[:,0]
        df.index.name = 'Page'
        df.drop(0, axis = 1, inplace = True)
    
        model = SpectralClustering(n_clusters = cluster_number, affinity = 'precomputed', n_init = 80, assign_labels = 'discretize')
        model.fit(list_of_affinity_matrix[i])       
        
        labels = model.labels_
        print("La longueur de la matrice affinité est : " + str(len(list_of_affinity_matrix[i])))
        print("La longueur du dataframe est : " + str(len(sublists_pages[i])))
        df['labels'] = labels
        
        data_nodes =  pick_representants_spectral(labels, list_of_affinity_matrix[i], df)
        data_src = []
        data_tar = []
        data_val = []
        new_links = []
        
        for x in list_of_links[i] :
            
            page_src = x[0]
            page_trg = x[1]
                
            src = df.loc[page_src]['labels']
            trg = df.loc[page_trg]['labels']
            val = values[list_of_links[i].index(x)]
            
            if src != trg : 
                
                if (src, trg) not in new_links :
                
                    new_links.append((src,trg))
                    data_src.append(src)
                    data_tar.append(trg)
                    data_val.append(val)
            
                else :
                
                    data_val[new_links.index((src, trg))] += val
        
        #clean the Sankey graph :
        
        rate = 0.13
                
        for src in data_src:
            for tar in data_tar :
                if (tar != src):
                    if (src, tar) in new_links and (tar, src) in new_links :
                        idx1 = new_links.index((src,tar))
                        idx2 = new_links.index((tar,src))
                        val1 = data_val[idx1]
                        val2 = data_val[idx2]
                        
                        if val1 >= val2:
                            
                            new_links.pop(idx2)
                            data_val.pop(idx2)
                            data_src.pop(idx2)
                            data_tar.pop(idx2)
            
                        else:
                            
                            new_links.pop(idx1)
                            data_val.pop(idx1)
                            data_src.pop(idx1)
                            data_tar.pop(idx1)
        
        
        res_in = [0 for i in range(0,cluster_number)]
        res_out = [0 for i in range(0,cluster_number)]
        
        for link in new_links :
            res_out[int(link[0])] += data_val[new_links.index(link)]
            res_in[int(link[1])] += data_val[new_links.index(link)]
            
        for link in new_links:
            src = link[0]
            tar = link[1]
            
            if  not (data_val[new_links.index(link)] > rate*res_in[src]
                and data_val[new_links.index(link)] > rate*res_in[tar]
                and data_val[new_links.index(link)] > rate*res_out[src]
                and data_val[new_links.index(link)] > rate*res_out[tar] ) :
                
                idx = new_links.index(link)
                data_val[idx]= 0
        
        
        
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
                width = 0.5
              ),
              label =  data_nodes
            ),
            link = dict(
              source =  data_src,
              target =  data_tar,
              value =  data_val,
              label =  ["" for x in values]
          ))                 
        
        layouts = dict(
            title = "Dynamique du traffic pertinent sur le site credit-agricole.fr le "+ json.loads(last_day) + " - subgraph numéro " + str(i) + '<br>' + 'Proportion du traffic total : ' + str(value_share[i]) + '%',
            font = dict(
              size = 10
            ),
            width = 1750,
            height = 800
        )   
        return {
                'data' : [data_trace],
                'layout' : layouts       
            }
    
                
if __name__ == '__main__':
    app.run_server(debug=True, port = 8080)
