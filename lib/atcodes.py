# Python Library Imports
import re

Commands = {
        'at'             : 'AT\r\n',
        'status'         : 'ATI\r\n',
        'extendedinfo'   : 'AT&V\r\n',
        'getimei'        : 'AT+CGSN\r\n',
        'setmode'        : 'AT+CMGF={0}\r\n',
        'checkmode'      : 'AT+CMGF?\r\n',
        'write'          : 'AT+CMGW="{0}"\r\n',
        'send'           : 'AT+CMSS={0}\r\n',
        'smsc'           : 'AT+CMSC={0}\r\n',
        'delete'         : 'AT+CMGD={0}\r\n',
        'signalstrength' : 'AT+CSQ\r\n',
        'networks'       : 'AT+COPS?\r\n',
        'csca'           : 'AT+CSCA="{0}"\r\n', # service center address
        'enterpin'       : 'AT+CPIN={0}\r\n',
        'changepin'      : 'AT+CPWD="SC","{0}","{1}"\r\n',
        'removepin'      : 'AT+CLCK="SC",0,"1234"\r\n',
        'cardlock'       : 'AT^CARDLOCK?\r\n',
        'ussd'           : 'AT+CUSD=1,"{0}",15\r\n',
        'list'           : 'AT+CMGL="{0}"\r\n',
        'charset'        : 'AT+CSCS="{0}"\r\n',
        'dial'           : 'ATD{0}\r\n',
        'cgdcont'        : 'AT+CGDCONT=1,"IP","{0}"\r\n',
        }

service_center_address = '+85290000000'
address_types = ['129','145']

ModeValues = {
        'pud' : '0',
        'sms' : '1',
        }

NetworkModes = {
        '0' : 'Automatic Network Selection',
        '1' : 'Manual Network Selection',
        '2' : 'Deregister From Network',
        '3' : 'Set <format only, no registration/deregistration',
        '4' : 'Manual Selection With Automatic Fall Back (Enters Automatic Mode If Manual Selection Fails)'
        }

NetworkFormats = {
        '0' : 'Long Alphanumeric String',
        '1' : 'Short Alphanumeric String',
        '2' : 'Numeric ID',
        }

NetworkStatuses = {
        '0' : 'Unknown',
        '1' : 'Available',
        '2' : 'Current',
        '3' : 'Forbidden',
        }

NetworkAccessTypes = {
        '0' : 'GSM',
        '1' : 'Compact GSM',
        '2' : 'UTRAN',
        '3' : 'GSM with EGPRS',
        '4' : 'UTRAN with HSDPA',
        '5' : 'UTRAN with HSUPA',
        '6' : 'UTRAN with HSDPA and HSUPA',
        }

MessageTypes = {
        'all'    : 'ALL',
        'unread' : 'REC UNREAD',
        'read'   : 'REC READ',
        'unsent' : 'STO UNSENT',
        }

ResponsesRegex = {
        'list'           : re.compile(r'\+CMGL\: (\d+)'),
        'write'          : re.compile(r'\+CMGW\: (\d+)'),
        'signalstrength' : re.compile(r'\+CSQ\: (\d+),(\d+)'),
        'networks'       : re.compile(r'\+COPS\: ([^,]*),([^,]*),([^,]*),(.*)'),
        'cardlock'       : re.compile(r'CARDLOCK\: (\d),(\d\d?),(\d+)\r'),
        'ussd'           : re.compile(r'\+CUSD\: (\d),\"(.*)\",(\d\d?)', re.DOTALL),
        'cms_error'      : re.compile(r'\+CMS ERROR\: (\d+)'),
        'cme_error'      : re.compile(r'\+CME ERROR\: (\d+)'),
        }
