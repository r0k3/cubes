# -*- coding=utf -*-

import cubes.browser
import urllib2
import json
import logging
import urllib
from ...common import get_logger

class SlicerBrowser(cubes.browser.AggregationBrowser):
    """Aggregation browser for Cubes Slicer OLAP server."""
    
    def __init__(self, cube, store, locale = None, **options):
        """Demo backend browser. This backend is serves just as example of a 
        backend. Uses another Slicer server instance for doing all the work. 
        You might use it as a template for your own browser.

        Attributes:

        * `cube` – obligatory, but currently unused here
        * `url` - base url of Cubes Slicer OLAP server

        """
        super(SlicerBrowser, self).__init__(cube, store)

        self.logger = get_logger()

        self.baseurl = "%s/cube/%s" % (store.url, cube.name)
        self.cube = cube
        
    def request(self, url):
        self.logger.debug("Request: %s" % url)
        handle = urllib2.urlopen(url)
        try:
            reply = json.load(handle)
        except Exception as e:
            raise Exception("Unable to load request %s. Reason: %s" % (url, e))
        finally:
            handle.close()
        
        return reply            
                
    def aggregate(self, cell, measures = None, drilldown = None, split=None, 
	          page=None, page_size=None, order=None, **kwargs):
        
        cut_string = cubes.browser.string_from_cuts(cell.cuts)
        params = [ ('cut', cut_string) ]

        levels = {}

        if drilldown:
            for dd in drilldown:
                params.append( ("drilldown", str(dd)) )
                levels[str(dd.dimension)] = [ str(l) for l in dd.levels ]
                
        if split:
            params.append( ('split', str(split)) ) 

        if measures:
            for m in measures:
                params.append( ("measure", str(m)) )
                    
	if order is not None:
	    params.append( ("order", str(order)) )
	if page is not None:
	    params.append( ("page", str(page)) )
	if page_size is not None:
	    params.append( ("page_size", str(page_size)) )


        url = self.baseurl + "/aggregate?" + urllib.urlencode(params)
        
        reply = self.request(url)
        result = cubes.browser.AggregationResult()
        result.cells = reply.get('cells', [])
	result.levels = reply.get('levels', {})
	result.cell = cell.to_dict()
	result.measures = reply.get('measures', [])
        if ( reply.get('summary') ):
            result.summary = reply.get('summary')

        return result
        
    def facts(self, cell, **options):
        raise NotImplementedError

    def fact(self, key):

        url = self.baseurl + "/fact/" + urllib.quote(str(key))
        return self.request(url)
