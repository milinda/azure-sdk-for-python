#-------------------------------------------------------------------------
# Copyright 2012 Milinda Pathirage
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
                                 _hosted_service_error_handler, _convert_hosted_service_to_xml,
                                 DEPLOYMENT_SLOT_PRODUCTION, DEPLOYMENT_SLOT_STAGING,
                                 _convert_deployment_to_xml)
from azure import (_validate_not_none, _dont_fail_on_exist,
                   WindowsAzureError,  HOSTED_SERVICE_HOST_BASE, _ERROR_VALUE_SHOULD_NOT_BE_NULL)

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

    def delete_hosted_service(self, hosted_service=None,hosted_service_name=None):
        '''
        Deletes a already created hosted service.
        '''
        hosted_service_to_delete = None
        if hosted_service is not None:
            hosted_service_to_delete = hosted_service.name
        elif hosted_service_name is not None:
            hosted_service_to_delete = hosted_service_name
        else:
            raise TypeError('Both hosted_service and hosted_service_name should not be None.')

        _validate_not_none(hosted_service_to_delete, 'hosted_service_to_delete')
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = HOSTED_SERVICE_HOST_BASE
        request.path = '/' + self.subscription_id + '/services/hostedservices/' + hosted_service_to_delete
        request.headers = _update_hosted_service_header(request)
        try:
            self._perform_request(request)
            return True
        except WindowsAzureError as e:
            _dont_fail_on_exist(e)
            return False

    def create_deployment(self, deployment=None, service_name=None, deployment_slot=DEPLOYMENT_SLOT_STAGING):

        request = HTTPRequest()
        request.method = 'POST'
        request.host = HOSTED_SERVICE_HOST_BASE
        request.path = '/' + self.subscription_id + '/services/hostedservices/' + service_name + '/deploymentslots/'  + deployment_slot
        request.headers = _update_hosted_service_header(request)
        request.body = _convert_deployment_to_xml(deployment)

        try:
            resp = self._perform_request(request)
            for name, value in resp.headers:
                if name.lower() == 'x-ms-request-id':
                    return value
            raise WindowsAzureError('Cannot find header x-ms-request-id in response.')
        except WindowsAzureError as e:
            raise e

    def delete_deployment(self, hosted_service_name=None, deployment_name=None, deployment_slot=None):
        request = HTTPRequest()
        request.method = 'DELETE'
        request.host = HOSTED_SERVICE_HOST_BASE

        if deployment_slot is not None:
            request.path = '/' + self.subscription_id + '/services/hostedservices/' + hosted_service_name + '/deploymentslots/' + deployment_slot
        elif deployment_name is not None:
            request.path = '/' + self.subscription_id + '/services/hostedservices/' + hosted_service_name + '/deployments/' + deployment_name
        else:
            raise TypeError('Both deployment_name and deployment_slot cannot be None.')

        request.headers = _update_hosted_service_header(request)

        try:
            resp = self._perform_request(request)
            for name, value in resp.headers:
                if name.lower() == 'x-ms-request-id':
                    return value
            raise WindowsAzureError('Cannot find header x-ms-request-id in response.')
        except WindowsAzureError as e:
            raise e


def _perform_request(self, request):
        try:
            resp = self._filter(request)
        except HTTPError as e:
            return _hosted_service_error_handler(e)

        if not resp:
            return None
        return resp

