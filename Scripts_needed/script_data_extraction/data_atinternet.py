# -*- coding: utf-8 -*-

"""
Script d'exportation de données AT-Internet pour les sites de PACIFICA
Note: usage de l'API Data Query.
"""


import requests
import yaml
from chrono import Chrono
import test_cookie as cookie

class DataATInternet():

	base_url = "https://exportsproxy.atinternet-solutions.com/Dataquery/ImmediateDataqueryDocument.aspx"
	
	# Tous les champs communs disponibles
	fields_all = ['d_app_version', 'd_browser', 'd_browser_acrobat_reader', 'd_browser_cat', 'd_browser_cookie', 'd_browser_flash',
		'd_browser_java', 'd_browser_javascript', 'd_browser_quicktime', 'd_browser_real_player', 'd_browser_silverlight',
		'd_browser_window_width', 'd_browser_wmp', 'd_click', 'd_click_chap1', 'd_click_chap2', 'd_click_chap3',
		'd_click_l2', 'd_click_type', 'd_conn_speed', 'd_date_hour_event', 'd_date_hour_visit', 'd_device',
		'd_device_height', 'd_device_type', 'd_device_width', 'd_di', 'd_entry_aisle1', 'd_entry_aisle2',
		'd_entry_aisle3', 'd_entry_aisle4', 'd_entry_aisle5', 'd_entry_aisle6', 'd_entry_page', 'd_entry_page_chap1',
		'd_entry_page_chap2', 'd_entry_page_chap3', 'd_exit_page', 'd_exit_page_chap1', 'd_exit_page_chap2',
		'd_exit_page_chap3', 'd_geo_browser_lng', 'd_geo_city', 'd_geo_continent', 'd_geo_country', 'd_geo_organisation',
		'd_geo_os_lng', 'd_geo_region', 'd_goal_type', 'd_hour_server', 'd_hour_visitor', 'd_ise_click_position',
		'd_ise_kw', 'd_ise_page', 'd_ise_search', 'd_isp', 'd_l2', 'd_l2_entry', 'd_l2_exit', 'd_manufacturer',
		'd_monitored_ip', 'd_os', 'd_os_colours', 'd_os_resolution', 'd_page', 'd_page_chap1', 'd_page_chap2',
		'd_page_chap3', 'd_page_position', 'd_page_views_per_visit', 'd_site', 'd_source', 'd_source_global',
		'd_source_type', 'd_space_l2', 'd_time_date', 'd_time_spent_per_visit', 'd_uv_id', 'd_visit_id', 'd_visitor_cat',
		'd_visitor_id', 'd_visitor_num_id', 'd_visitor_text_id', 'm_bounce_rate', 'm_bounces', 'm_bq', 'm_clicks',
		'm_conversions1_loads', 'm_conversions1_rate', 'm_conversions1_visits', 'm_conversions2_loads',
		'm_conversions2_visits', 'm_days', 'm_entering_visits', 'm_entry_rate', 'm_ise_clicks', 'm_ise_exit_rate',
		'm_ise_exit_visits', 'm_ise_page_views', 'm_page_loads', 'm_page_loads_per_visits', 'm_page_views',
		'm_page_views_per_entering_visits', 'm_page_views_per_visits', 'm_sales', 'm_time_spent',
		'm_time_spent_per_pages', 'm_time_spent_per_pages_loads', 'm_time_spent_per_pages_visits',
		'm_time_spent_per_visits', 'm_v_revised_sales', 'm_v_sales', 'm_v_sales_per_conversions1', 'm_visitors',
		'm_visits', 'm_visits_all', 'm_visits_nopages'
	]
	
	# Clefs de base
	# Chaque export contiendra ces clefs (donc dupliquées partout), pour les raisons suivantes:
	# - pouvoir réconcilier de manière robuste les extraits pour les différentes partitions de colonnes
	# - pouvoir être sûr d'avoir une granularité fine (1 ligne = 1 individu)
	# TODO: pas sûr pour m_visits!
	fields_base = ['d_click', 'd_date_hour_event', 'd_date_hour_visit', 'd_hour_server',
		'd_hour_visitor', 'd_page', 'd_page_position', 'd_time_date',
		'd_visit_id', 'd_visitor_id', 'd_visitor_text_id',
		'm_visits'
	]
	
	# Pour rappel, champs utilisés pour "download-part1.sh"
	fields_p1 = [
		'd_time_date', 'd_date_hour_visit', 'd_date_hour_event',
		'd_page', 'd_page_chap1', 'd_page_chap2', 'd_page_chap3', 'd_ise_page', 'd_page_position',
		'd_geo_browser_lng', 'd_geo_city', 'd_geo_region',
		'd_app_version', 'd_l2', 'd_device', 'd_browser_javascript', 'd_manufacturer', 'd_os',
		'd_geo_os_lng', 'd_geo_country', 'd_monitored_ip', 'd_visit_id', 'd_visitor_text_id', 'd_visitor_num_id', 'd_uv_id',
		'd_visitor_id', 'd_visitor_cat', 'd_source', 'd_source_global',
		'm_conversions1_rate'
	]
		
	def __init__(self):
	
		# Read config
		with open("D:/Users/wyannis/Documents/Scolarite/Stage 2A/Rapport de stage/App_Demo/Scripts_needed/script_data_extraction/config.yml", 'r') as ymlfile:
			self.cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


	# Teste si les champs demandé sont OK pour AT Internet
	# Sinon, on prend le risque d'avoir un 'bad request'
	@staticmethod
	def verif(fields):
		sz = len(fields)
		if sz > 30:
			return 'Too much fields!'
			
		b = 'm' in [s[0] for s in fields]
		if not b:
			return 'We need at least one metric!'
		return 'OK!'

	# Format a json
	@staticmethod
	def fj(j):
		return str(j).replace("'","\"").replace(' ', '')
		
	# Renvoie une liste de listes, correspondant aux champs à utiliser pour chaque requête
	# - Vérifie que les champs seront acceptés par AT Internet
	# - Dans chaque partie, il y a les clefs de base
	def parts(self):
		limit_max = 30 # Nombre de champs autorisés par requête
		fmisc = list(set(self.fields_all)-set(self.fields_base))
		lmisc = limit_max-len(self.fields_base) # Nombre de champs supplémentaires
		fa = fmisc
		while len(fa)>0:
			fc = fa[:lmisc]
			fa = fa[lmisc:]
			fc += self.fields_base
			fc = sorted(list(set(fc)))
			print(self.verif(fc))
			yield fc
			
	# Download un fichier AT Internet
	# site_id: ID numérique du site dont il faut extraire les données
	# fields: champs à extraire
	# date_beg, date_end: date de début et de fin, au format YYYY-MM-DD
	# filename: fichier de sortie
	def download(self, site_id, fields, date_beg, date_end, filename, show_chrono=True):

		url=(
			self.base_url + "?"
			+ "UrlTemplate="
			+ "%26columns={" + ','.join(fields) +"}"
			+ "%26sort={-" + fields[0] + "}"
			#+ "%26segment=100068961" # Ce champ apparaissait pour les requêtes CA.fr
			+ "%26space={s:"+ str(site_id) + "}"
			#+ "%26period={R:{D:'-1'}}" # La veille
			+ "%26period={D:{start:'" + date_beg + "',end:'" + date_end + "'}}"
			+ "%26max-results=%23maxresult%23"
			+ "%26page-num=%23pagenum%23"
			+ "%26sep=dot"
			+ "&UserId={}".format(self.cfg['user_id'])
			+ "&UserLanguageId=1"
			+ "&Filename=mycsv"
			+ "&Space={\"sites\":[\"" + str(site_id) + "\"],\"group\":\"\"}"
		)
	 
		headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
			"Connection": "keep-alive",
			"Cookie": (
				"atuserid={}; ".format(self.fj(self.cfg['cookie']['atuserid']))
				+ "AnalyticsSuiteVersion=2; "
				+ "atidvisitor={}; ".format(self.fj(self.cfg['cookie']['atidvisitor']))
				+ "ATToken=Token=" + cookie.FIND_COOKIE() + ";"),
			"Host": "exportsproxy.atinternet-solutions.com",
			"Referer": "https://apps.atinternet-solutions.com/DataQuery/Designer/",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36" # Yes! on imite vraiment tout!
		}

		#print (cookie.FIND_COOKIE())
		#print (headers)

		if show_chrono:
			chn = Chrono().start()
		r=requests.get(url, headers=headers)
		if show_chrono:
			chn.stop() # Temps : 36s à 1min12

		with open(filename, 'wt') as fout:
			fout.write(r.text)
