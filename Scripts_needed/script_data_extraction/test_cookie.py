#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 12:18:49 2019

@author: vagrant
"""


from requests import Session
import yaml

##################      AIM OF THIS SCRIPT: EXTRACT THE ATTOKEN OF AT-INTERNET APP      ####################


def fj(j):
		return str(j).replace("'","\"").replace(' ', '')
    
with open("D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Scripts_needed/script_data_extraction/config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

def FIND_COOKIE():
    ################################    LOGIN INFORMATIONS     #########################################""
    
    values = {'login' : 'arnaud.quirin@credit-agricole-sa.fr',
              'password' : '314Bm=93'
              }
    
    #######################     MAKE THE REQUEST WITH THE CORRECT HEADER (obtained from inspecting the site) ######################
    
    
    with Session() as s :
        login_url = "https://auth.atinternet-solutions.com/api/config/v1/public/authentication/connect"
        site = s.get(login_url)    
        headers = {
    			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    			"Accept-Encoding": "gzip, deflate, br",
    			"Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    			"Connection": "keep-alive",
    			"Cookie": (
    				"atuserid={}; ".format(fj(cfg['cookie']['atuserid']))
    				+ "AnalyticsSuiteVersion=2; "
    				+ "atidvisitor={}; ".format(fj(cfg['cookie']['atidvisitor']))),
    #			"Host": login_url,
    			"Referer": "https://apps.atinternet-solutions.com/login/",
    			"Upgrade-Insecure-Requests": "1",
    			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36" # Yes! on imite vraiment tout!
    		}
        result = s.post(login_url, data = values, headers = headers)
        ATToken = s.cookies.get_dict()['ATToken'].split('=')[1]
        
    return ATToken

    

