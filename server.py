#!/usr/bin/env python
# Jan-Piet Mens, November 2015
# backend for PowerDNS remote

import sys
import dns.name
from bottle import get, run, request
import airports

HTTP_PORT = 9053
HTTP_LISTEN = '0.0.0.0'

ZONE = 'airports.aa'
db = {}

SOA = { "qname"     : ZONE,
        "qtype"     : "SOA",
        "content"   : "remote.local. jpm.remote. 1 1800 900 604800 60",
        "ttl"       : 60 }
NS  = { "qname"     : ZONE,
        "qtype"     : "NS",
        "content"   : "remote.local.",
        "ttl"       : 60 }

@get("/list/:qname")
def axfr(qname):
    responses = [ SOA, NS ]

    for key in db: # [ 'IBZ', 'FRA', 'LAX' ]:
        data = db[key]
        qname = key.lower() + "." + ZONE    # no trailing period for powerdns
        if 'name' in data and data['name'] is not None:
            responses.append({
                "qname"     : qname,
                "qtype"     : "TXT",
                "content"   : data['name'],
                "ttl"       : 60,
            })
        if 'loc' in data and data['loc'] is not None:
            responses.append({
                "qname"     : qname,
                "qtype"     : "LOC",
                "content"   : data['loc'],
                "ttl"       : 60,
            })

    return dict(result=responses)

@get("/lookup/:qname/:qtype")
def lookup(qname, qtype):

    print "z=",qname," qtype=",qtype

    if qname.endswith(ZONE) == False:
        return dict(result=False, log="I don't have " + qname)

    z = dns.name.from_text(ZONE)
    n = dns.name.from_text(qname)
    owner = n - z
    ownerstring = owner.to_text()

    responses = []

    if ownerstring == '@' and (qtype == 'SOA' or qtype == 'ANY'):
        responses.append(SOA)

    if ownerstring == '@' and (qtype == 'NS' or qtype == 'ANY'):
        responses.append(NS)

    if ownerstring == '@' and (qtype == 'A' or qtype == 'ANY'):
        responses.append({
            "qname"     : qname,
            "qtype"     : "A",
            "content"   : "192.168.1.114",
            "ttl"       : 60,
        })

    print "OWNER=", ownerstring
    if ownerstring != '@' and qtype == 'ANY':
        if ownerstring.upper() in db:
            data = db[ownerstring.upper()]
            if 'name' in data:
                responses.append({
                    "qname"     : qname,
                    "qtype"     : "TXT",
                    "content"   : data['name'],
                    "ttl"       : 60,
                    "auth"      : 1,
                })
            if 'loc' in data:
                responses.append({
                    "qname"     : qname,
                    "qtype"     : "LOC",
                    "content"   : data['loc'],
                    "ttl"       : 60,
                    "auth"      : 1,
                })


    return dict(result=responses)

# pdnssec show-zone xx
@get("/getDomainInfo/:qname")
def getdomaininfo(qname):
    return dict(result={
        'id'        : 1,
        'zone'      : qname,
        'kind'      : "NATIVE",
        'serial'    : 11,
        })

db = airports.load()
run(host=HTTP_LISTEN, port=HTTP_PORT, debug=True)
