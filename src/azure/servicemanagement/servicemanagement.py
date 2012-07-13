#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------

from azure.http import (HTTPError, HTTPRequest)
from azure.http.httpclient import _HTTPClient
from azure.servicemanagement import (x_ms_version, _update_hosted_service_header,
                                 _hosted_service_error_handler, _convert_hosted_service_to_xml)
from azure import (_validate_not_none, _dont_fail_on_exist,
                   WindowsAzureError,  HOSTED_SERVICE_HOST_BASE)

class ServiceManagementService:
    '''
    This is the main class managing hosted services.
    subscription_id: your subscription id, required for all operations
    cert_file: certificate file for authentication, required for all operations
    '''

    def __init__(self, subscription_id=None, key_file=None, cert_file=None):
        self.subscription_id = subscription_id
        self.key_file = key_file
        self.cert_file = cert_file
        self.x_ms_version = x_ms_version
        self._httpclient = _HTTPClient(service_instance=self, cert_file=self.cert_file, key_file=self.key_file, x_ms_version=self.x_ms_version)
        self._filter = self._httpclient.perform_request

    def create_hosted_service(self, hosted_service):
        '''
        Creates a new hosted service in Windows Azure under given subscription.
        '''
        _validate_not_none('hosted_service', hosted_service)
        request = HTTPRequest()
        request.method = 'POST'
        request.host = HOSTED_SERVICE_HOST_BASE
        request.path = '/' + self.subscription_id + '/services/hostedservices'
        request.body = _convert_hosted_service_to_xml(hosted_service)
        request.headers = _update_hosted_service_header(request)

        try:
            self._perform_request(request)
            return True
        except WindowsAzureError as e:
            _dont_fail_on_exist(e)
            return False

    def _perform_request(self, request):
        try:
            resp = self._filter(request)
        except HTTPError as e:
            return _hosted_service_error_handler(e)

        if not resp:
            return None
        return resp

