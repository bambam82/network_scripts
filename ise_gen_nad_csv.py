#!/usr/bin/env python3

# import re
import os
# import sys
import argparse
from mylib import libbart as lb


# Provide switches to control this script
parser = argparse.ArgumentParser(
    description='''This script is used to generate the NAD csv file.
    This file can than be imported in ISE.''',
    epilog='''Bash environment variables used:
    CISCOCOMMUNITY, ISERADIUSKEY''')
parser.add_argument(
    '-i', '--ip', required=True,
    help='''Input should be an IP address, a file containing IP addresses or
            an HPov csv export file.''')
parser.add_argument(
        '-sc', '--sitecode', required=True,
        help='''Provide the site code.''')
args = parser.parse_args()

iplist, iperror = lb.readipfile(args.ip)
iseradius = lb.envvariable("ISERADIUSKEY")
communitystring = lb.envvariable("CISCOCOMMUNITY")

workdir = os.path.expanduser('~') + '/working'
outputdir = "{}/{}_ISEconfig/".format(workdir, args.sitecode)
if not os.path.isdir(outputdir):
    os.mkdir(outputdir)
filename = '{}{}_NADs_import.csv'.format(outputdir, args.sitecode)
outputfile = open(filename, 'w')

outputfile.write('Name:String(32):Required,Description:String(256),IP Address:\
Subnets(a.b.c.d/m#....):Required,Model Name:String(32),Software \
Version:String(32),Network Device Groups:String(100)(Type#Root Name#Name|...)\
:Required,Authentication:Protocol:String(6),Authentication:Shared Secret:\
String(128),EnableKeyWrap:Boolean(true|false),EncryptionKey:String(ascii:16|\
hexa:32),AuthenticationKey:String(ascii:20|hexa:40),InputFormat:String(32),\
SNMP:Version:Enumeration(1|2c|3),SNMP:RO Community:String(32),SNMP:Username:\
String(32),SNMP:Security Level:Enumeration(Auth|No Auth|Priv),SNMP:\
Authentication Protocol:Enumeration(MD5|SHA),SNMP:Authentication Password:\
String(32),SNMP:Privacy Protocol:Enumeration(DES|AES128|AES192|AES256|3DES),\
SNMP:Privacy Password:String(32),SNMP:Polling Interval:Integer:600-86400 \
seconds,SNMP:Is Link Trap Query:Boolean(true|false),SNMP:Is MAC Trap Query:\
Boolean(true|false),SNMP:Originating Policy Services Node:String(32),SGA:\
Device Id:String(32),SGA:Device Password:String(256),SGA:Environment Data \
Download Interval:Integer:1-2147040000 seconds,SGA:Peer Authorization Policy \
Download Interval:Integer:1-2147040000 seconds,SGA:Reauthentication Interval:\
Integer:1-2147040000 seconds,SGA:SGACL List Download Interval:Integer:\
1-2147040000 seconds,SGA:Is Other SGA Devices Trusted:Boolean(true|false),\
SGA:Notify this device about SGA configuration changes:String(ENABLE_USING_\
CLI|ENABLE_USING_COA|DISABLE_ALL),SGA:Include this device when deploying \
Security Group Tag Mapping Updates:Boolean(true|false),Deployment:EXEC Mode \
Username:String(32),Deployment:EXEC Mode Password:String(32),Deployment:\
Enable Mode Password:String(32),SGA:PAC issue date:Date,SGA:PAC expiration \
date:Date,SGA:PAC issued by:String,TACACS:Shared Secret:String(128),TACACS:\
Connect Mode Options:String (OFF|ON_LEGACY|ON_DRAFT_COMPLIANT),Profile:\
String(128):Required,coaPort:Integer(128):Required\n')
# outputfile.write('!\n! Roaming switches should be removed.\n!\n')

for ip in iplist:
    try:
        sw = lb.Switch(ip)
        hostname = sw.gethostname()
    except ConnectionError as err:
        print('SNMP error:', ip, err)
        continue
    if hostname.startswith("SW"):
        hostname = '{}-{}'.format(args.sitecode, hostname)
    outputfile.write(
        '{},,{}/32,,,Device Type#All Device Types#Authenticator_switches\
|Location#All Locations#{},RADIUS,"{}",false,,,,2c,{},,,,\
,,,28800,true,true,,,,,,,,,ENABLE_USING_COA,,,,,,,,,,Cisco,1700\n'.format(
            hostname,
            ip,
            args.sitecode,
            iseradius,
            communitystring))

outputfile.close()
print('creation done. {} devices.\noutputfile: {}'.format(
    len(iplist), filename))
