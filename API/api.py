#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Brian Whitman on 2010-06-16.
Copyright (c) 2010 The Echo Nest Corporation. All rights reserved.
"""
from __future__ import with_statement

import os
import sys
import logging

abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import web
import fp
import re

try:
    import json
except ImportError:
    import simplejson as json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.addHandler(logging.FileHandler('log/api.log'))

# Very simple web facing API for FP dist

urls = (
    '/query', 'query',
    '/query?(.*)', 'query',
    '/ingest', 'ingest',
    '/delete', 'delete',
    '/delete?(.*)', 'delete',
)


class ingest:
    def POST(self):
        params = web.input(track_id="default", fp_code="", artist=None, release=None, track=None, length=None, codever=None)
        if params.track_id == "default":
            track_id = fp.new_track_id()
        else:
            track_id = params.track_id
        if params.length is None or params.codever is None:
            return web.webapi.BadRequest()
        
        # First see if this is a compressed code
        if re.match('[A-Za-z\/\+\_\-]', params.fp_code) is not None:
           code_string = fp.decode_code_string(params.fp_code)
           if code_string is None:
               return json.dumps({"track_id":track_id, "ok":False, "error":"cannot decode code string %s" % params.fp_code})
        else:
            code_string = params.fp_code

        data = {"track_id": track_id, 
                "fp": code_string,
                "length": params.length,
                "codever": params.codever }
        if params.artist: data["artist"] = params.artist
        if params.release: data["release"] = params.release
        if params.track: data["track"] = params.track
        fp.ingest(data, do_commit=True, local=False)
	
	
	web.header('Content-Type', 'text/plain')
        return json.dumps({"track_id":track_id, "status":"ok"})
        
    
class query:
    def POST(self):
        return self.GET()
        
    def GET(self):
        stuff = web.input(fp_code="")
        response = fp.best_match_for_query(stuff.fp_code)

	web.header('Content-Type', 'text/plain')
        return json.dumps({"ok":True, "query":stuff.fp_code, "message":response.message(), "match":response.match(), "score":response.score, \
                        "qtime":response.qtime, "track_id":response.TRID, "total_time":response.total_time})

class query:
    def POST(self):
        return self.GET()

    def GET(self):
        stuff = web.input(fp_code="")
        response = fp.best_match_for_query(stuff.fp_code)

	web.header('Content-Type', 'text/plain')
        return json.dumps({"ok":True, "query":stuff.fp_code, "message":response.message(), "match":response.match(), "score":response.score, \
                        "qtime":response.qtime, "track_id":response.TRID, "total_time":response.total_time})

class delete:
    def POST(self):
        return self.GET()

    def GET(self):
        params = web.input(track_id="")
        # DEC strings come in as unicode so we have to force them to ASCII
        track_id = params.track_id.encode("utf8")
        response = fp.delete(track_id)

	web.header('Content-Type', 'text/plain')
        return json.dumps({"ok":True, "delete":track_id, "deleteResponse":response})

class APILogger(object):
    def write(self, data):
        pass
        #logger.info(data.strip())

sys.stdout = APILogger()
sys.stderr = APILogger()

application = web.application(urls, globals()).wsgifunc()
        
if __name__ == "__main__":
    application.run()

