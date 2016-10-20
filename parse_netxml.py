#!/usr/bin/python

import re
import sys
import pprint
import sqlite3
import argparse
import xml.etree.ElementTree

def main(args):
	conn = sqlite3.connect('networks.db')

	c = conn.cursor()
	c.execute('''
	CREATE TABLE IF NOT EXISTS networks (
		bssid TEXT PRIMARY KEY, 
		essid TEXT, 
		cloaked TEXT, 
		encryption TEXT, 
		channel TEXT
	)
	''')

	c.execute('''
	CREATE TABLE IF NOT EXISTS clients (
		bssid TEXT, 
		mac TEXT UNIQUE
	)
	''')
	c.close()
	conn.commit()
	
	if None is not args.files:
		for arg in args.files:
			try:
				print arg
				parse(arg,conn)
			except xml.etree.ElementTree.ParseError as parse_error:
				print parse_error
				with open(arg,'r') as in_file:
					with open("cleaned_"+arg, 'w') as out_file:
						for line in in_file:
							line = re.sub('&#x   0;', '', line)
							out_file.write(line)
				parse("cleaned_"+arg,conn)
	
	if args.all:
		all_networks(conn)
      	if args.wpa2:
		wpa2_networks(conn)
	if args.wpa:
        	wpa_networks(conn)
	if args.opn:
        	open_networks(conn)
	if args.psk:
		psk_networks(conn)
	if args.mgt:
        	mgt_networks(conn)
        
	conn.close()

def parse(arg,conn):
	verbose = "false"
	root = xml.etree.ElementTree.parse(arg).getroot()
	for element in root.findall('wireless-network'):
		bssid = ""
		essid = ""
		cloaked = ""
		channel = ""
		network_type = element.get('type')
		if "probe" != network_type:
			ssid_tag = element.find('SSID')
			if None is not ssid_tag:
				essid_tag = ssid_tag.find('essid')
				essid = essid_tag.text
				cloaked = essid_tag.get("cloaked")
				if None is essid:
					essid = "<Hidden>"
				essid = re.sub('^Hidden', '<Hidden>', essid)
				encryption = ssid_tag.findall('encryption')
				ciphers = ""
				for algorithm in encryption:
					ciphers = ciphers + " " + algorithm.text
		if "probe" != network_type or "true" == verbose:
			bssid = element.find('BSSID').text
			bssid = re.sub(':', '-', bssid)	
	
			channel = element.find("channel").text
			if None is channel:
				channel = "0"
			
			print bssid
			c = conn.cursor()
			c.execute('''
				INSERT OR IGNORE INTO networks 
				VALUES (?,?,?,?,?);
				''', (bssid, essid, cloaked, ciphers, channel)
			)
			if None is not essid and "<Hidden>" == essid:
				c.execute('''
					UPDATE networks 
					SET essid=(?) 
					WHERE bssid LIKE (?) 
					AND essid LIKE '<Hidden>';
					''', (essid, bssid)
				)
			conn.commit()
			c.close()	
	
			network_clients = element.findall('wireless-client')	
			for client in network_clients:
				c = conn.cursor()
				connection = client.get("type")
				mac = client.find("client-mac").text
				print "\t"+mac
				client_ssid = client.find('SSID')
				if None is not client_ssid:
					client_essid = client_ssid.find('ssid')
					if None is not client_essid:
						print "\t\t"+client_essid.text
						c.execute('''
							UPDATE networks 
							SET essid=(?) 
							WHERE bssid LIKE (?) 
							AND essid LIKE '<Hidden>';
							''', (client_essid.text, bssid)
						)
				c.execute('''
					INSERT OR IGNORE INTO clients 
					VALUES (?,?);
					''', (bssid, mac)
				)
				c.close()			
	conn.commit()

def all_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_all.csv", c.fetchall(), args)
	c.close()

def wpa2_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		WHERE encryption LIKE '%WPA+AES-CCM%' 
		AND channel NOT LIKE '0' 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_wpa2.csv", c.fetchall(), args)
	c.close()

def wpa_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		WHERE encryption LIKE '%WPA+TKIP%' 
		AND channel NOT LIKE '0' 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_wpa.csv", c.fetchall(), args)
	c.close()

def open_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		WHERE encryption LIKE '%None%' 
		OR encryption IS NULL 
		AND channel NOT LIKE '0' 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_open.csv", c.fetchall(), args)
	c.close()

def psk_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		WHERE encryption LIKE '%WPA+PSK%' 
		AND channel NOT LIKE '0' 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_psk.csv", c.fetchall(), args)
	c.close()

def mgt_networks(conn):
	c = conn.cursor()
	c.execute('''
		SELECT * FROM networks 
		WHERE encryption LIKE '%WPA+MGT%' 
		AND channel NOT LIKE '0' 
		ORDER BY bssid 
		COLLATE NOCASE ASC
	''')
	print_results("networks_mgt.csv", c.fetchall(), args)
	c.close()

def print_results(file_name, results, args):
	print file_name
	with open(file_name, 'w') as out:
                out.write("bssid,essid,cloaked,ciphers,channel\n")
                for result in results:
                        print("{: >20} {: >30} {: >10} {: >30} {: >10}".format(*result))
                        if args.csv:
				out.write(result[0]+","+result[1]+","+result[2]+","+result[3]+","+result[4]+"\n")

if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--files", nargs='*', help='Files to parse')
	parser.add_argument("--all", action='store_true', help='Display all networks')
	parser.add_argument("--wpa2", action='store_true', help='Display only WPA2 Networks')
	parser.add_argument("--wpa", action='store_true', help='Display only WPA Networks')
	parser.add_argument("--wep", action='store_true', help='Display only WEP Networks')
	parser.add_argument("--opn", action='store_true', help='Display only OPEN Networks')
	parser.add_argument("--psk", action='store_true', help='Display only networks using Pre-Shared Keys')
	parser.add_argument("--mgt", action='store_true', help='Display only networks using individual user authentication (MGT/Enterprise)')
	parser.add_argument("--csv", action='store_true', help='Record output in CSV File')
	parser.add_argument("--clients", action='store_true', help='Record clients connected to each network')
	parser.add_argument("--output-name", action='store_true', help='Alternative name for output files')
	args=parser.parse_args()
	main(args)
