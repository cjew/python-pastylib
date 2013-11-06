# The MIT License (MIT)
#
# Copyright (c) 2013 Christopher Jewell <development@jewell.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Python 2.x library for pastyapp
# Pastyapp is a very useful tool to synchronize your clipboard across multiple 
# platforms and devices

# Written by Christopher W Jewell <development@jewell.de>
# 2013-11-05

import httplib2
import base64
import json

class NoValidAPIServer(Exception):
    pass

class RequestError(Exception):
    pass

class PastyAPI():
    APIVERSION = 2.1
    LIBVERSION = 0.1
    GET = "GET"
    POST = "POST"
    API_GETLIST = "/v2.1/clipboard/list.json"
    API_UPDATELIST = "/v2.1/clipboard/item"

    def __init__(self, api_server, login, ssl_validation=False):
        # Test if ssl_validation is a boolean - throw errors when api_server
        # is invalid or not available
        if type(ssl_validation) != bool:
            raise TypeError("Variable ssl_validation expected to be boolean")
        else:
            self.ssl_validation = ssl_validation
        if self.__checkAPIServer(api_server) is False:
            raise NoValidAPIServer("The API Server is not valid or available")

        # Set internal username and password - save it as a tuple
        self.login = login

    def __checkAPIServer(self, api_server):
        # @Param api_server API Server string
        # Returns boolean
        # Gets called by __init__

        api_server = str(api_server)
        
        # Test if return code is 200 and given server is available
        try:
            resp, content = httplib2.Http(disable_ssl_certificate_validation=self.ssl_validation)\
                                            .request(api_server, self.GET)
        except httplib2.SSLHandshakeError:
            raise SSLValidationError("Failed to verify the SSL certificate. Please try again with\
                                        validation disabled (ssl_validation=False)")
        if int(resp["status"]) == 200:
            # Status is 200 (OK) and we can return True to __init__
            # Strip last '/' if last character is '/'
            if api_server[-1:] == "/":
                self.api_server = api_server[:-1]
            else:
                self.api_server = api_server
            return(True)
        else:
            # Status is not 200 and we return False to __init__
            return(False)

    def __createHeaders(self, action):
        # Create and return header dictionary based on username and password
        if action == self.GET:
            return({'Authorization':'Basic %s' % base64.b64encode(':'.join(self.login))})
        if action == self.POST:
            return({'Authorization':'Basic %s' % base64.b64encode(':'.join(self.login)),
                    'Content-Type':'application/json'})

    def __createItemBody(self):
        # Create body for HTTP Request to send an item to PastyAPI to be stored in the clipboard
        return(json.dumps({'item':self.new_item}))
    
    def getClipboard(self):
        # getList connects to given API Server and requests whole clipboard
        # Returns list with all items stored in clipboard
        resp, content = httplib2.Http(disable_ssl_certificate_validation=self.ssl_validation)\
                                        .request(self.api_server+self.API_GETLIST, self.GET, \
                                        headers=self.__createHeaders(self.GET))
        if json.loads(content)['code'] != 200:
            raise RequestError(json.loads(content)["message"])
        else:
            # Code is 200
            # We return a list with all clipboard items
            json_list = json.loads(content)
            item_list = []
            for i in json_list["payload"]["items"]:
                item_list.append(i["item"])
            return(item_list)

    def updateClipboard(self, new_item):
        # @Param new_items has to be a string containing the item to be stored
        # Returns boolean update status
        if str(new_item) == "":
            raise ValueError("Missing string to add")
        self.new_item = str(new_item)
        resp, content = httplib2.Http(disable_ssl_certificate_validation=self.ssl_validation)\
                                        .request(self.api_server+self.API_UPDATELIST, self.POST, \
                                        body=self.__createItemBody(), headers=self.__createHeaders(self.POST))
        if json.loads(content)['code'] != 201:
            raise RequestError(json.loads(content)["message"])
        else:
            # Code is 201 (regarding API specification)
            # We do not return anything here as the list 
            pass
