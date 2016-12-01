import requests
import re
import json

jfp_token = ""

class citi:
	def set_headers(self,response_cookies):
			#print "getting cookie!!!***!!!***!"
			self.authorisation_token = "JSESSIONID=%s" % (response_cookies['JSESSIONID'])
			self.authenticated_headers = {
				'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10",
				'Cookie':  self.authorisation_token,
			}
			#print "I'm here!"
			#print self.authorisation_token

	def set_referer_headers(self,response_headers,location,token,sessioncheck):
			#print "getting cookie!!!***!!!***!"
			jsessionid = response_headers['JSESSIONID']
			self.authorisation_token = jsessionid
			self.authenticated_headers_2 = {
						'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10",
						'Cookie':  "JSESSIONID=%s; token=%s; sessionCheck=%s; AdTrack=pageHistory|Signon.713.200; s_pers_c5=anon; s_pers_c6=1; s_sq=[[B]]; CITI_SITE=GBRDC; __citiOvrl-UK-Outage=1; style=null; s_cc=true; s_gpv_pageName=GB|Account Daskboard|My Citi Home; s_invisit=true; s_nr=1480599455253-New; s_vnum=1483228800255&vn=1" % (self.authorisation_token,token,sessioncheck),
						'Referer': location,
						'Content-Type': 'application/json',

				}
			#print self.authenticated_headers_2

	def login(self,username,password):

			global jfp_token

			response = requests.get('https://online.citi.eu/GBIPB/JSO/signon/DisplayUsernameSignon.do')
			self.set_headers(response.cookies)
			#print "now getting token"

			match = re.search("JFP_TOKEN=\w{8}",response.text)
			jfp_token = match.group(0)
			#print jfp_token

			match = re.search("name=\"SYNC_TOKEN\" value=(.*)",response.text)
			sync_token = match.group(1).split("\"")[1]
			#print sync_token

			
			response = requests.get('https://online.citi.eu/wdp-service/latest/dyn_wdp.js',headers=self.authenticated_headers)
			token = response.cookies['token']
			#print "*** the token is: %s ***" % token

			print "im now here logging on"

			login_data = {
				'SYNC_TOKEN': sync_token,
				'JFP_TOKEN': jfp_token.split('=')[1],
				'username': username,
				'password': password,
			}
			sessioncheck2 = 1
			response = requests.post('https://online.citi.eu/GBIPB/JSO/signon/ProcessUsernameSignon.do?' + jfp_token,login_data,headers=self.authenticated_headers,allow_redirects=False)
			location = response.headers['Location']
			self.set_referer_headers(response.cookies,"https://online.citi.eu/GBIPB/JSO/signon/DisplayUsernameSignon.do",token,sessioncheck2)
			#print location

			#print "NOW GETTING A NEW SESSION KEY!!!"
	
			response = requests.get(location,headers=self.authenticated_headers_2)
			#self.set_headers(response.cookies)

			match = re.search("\"sessionCheck\"\, \'\w{16}\'",response.text)
			sessioncheck = match.group(0).split(",")[1]
			sessioncheck2 = sessioncheck.split('\'')[1]
			#print "sesion_check is!!!!: %s" % sessioncheck2

			
			#print response.cookies
			#print response.status_code
			self.set_referer_headers(response.cookies,location,token,sessioncheck2)
			print "done"

	def getname(self):

			global jfp_token

			response = requests.post("https://online.citi.eu/GBIPB/REST/welcome/welcomeMsgContent?" + jfp_token,headers=self.authenticated_headers_2,allow_redirects=False)
			return json.loads(response.text)


	def getstatus(self):
			global jfp_token

			response = requests.post('https://online.citi.eu/GBIPB/COA/ain/accdetact/flow.action?' + jfp_token, headers=self.authenticated_headers_2,allow_redirects=False)

			response = requests.post("https://online.citi.eu/GBIPB/REST/coa/ain/accsumlit/getAccounts?" + jfp_token,headers=self.authenticated_headers_2,allow_redirects=False)
			x =  json.loads(response.text)
			curr = len(x["accountDetailList"]) - 1
			while curr >= 0:
				account_name = x["accountDetailList"][curr]["accountName"]
				account_balance = x["accountDetailList"][curr]["elementEntryMap"]["right"][0]["value"]
				print "%s : %s" % (account_name,account_balance)
				curr = curr - 1

