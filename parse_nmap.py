#!/usr/bin/python

import sys
import xml.etree.ElementTree

for arg in sys.argv[1:]:
	print arg
	try:
		root = xml.etree.ElementTree.parse(arg).getroot()
		for element in root.findall('host'):
			status = element.find('status')
			if 'up' == status.get('state'):
				address = element.findall('address')
				ip = address[0].get('addr')
				ports = element.findall('ports')
				for port in ports:
					open_port = port.findall('port')
					for prt in open_port:
						service = prt.findall('service')
						state = prt.findall('state')
						for st in state:
							if 'open' == st.get('state'):
								for svc in service:
									print ip+"\t"+prt.get('protocol')+"\t"+prt.get('portid')+"\t"+svc.get('name')+"\t", svc.get("product"), svc.get("version")
	except xml.etree.ElementTree.ParseError as parseerror:
		print parseerror
		continue
