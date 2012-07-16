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

import base64
from azure import (_validate_not_none, _ERROR_VALUE_SHOULD_NOT_BE_NULL,
                   WindowsAzureError, WindowsAzureConflictError,
                   WindowsAzureMissingResourceError, xml_escape)
import azure

x_ms_version = '2010-10-28'

DEPLOYMENT_SLOT_PRODUCTION = 'production'
DEPLOYMENT_SLOT_STAGING = 'staging'

class HostedService:

    def __init__(self):
        self.name = None
        self.label = None
        self.description = None
        self.location = None
        self.affinity_group = None
        self.extended_properties = []

    def add_property(self, name, value):
        self.extended_properties.append((name, value))

class Deployment:

    def __init__(self):
        self.name = None
        self.package_url = None
        self.label = None
        self.configuration = None
        self.start_deployment = True
        self.treat_wranings_as_errors = True
        self.extended_properties = []

    def add_property(self, name, value):
        self.extended_properties.append((name, value))

def _update_hosted_service_header(request):
    ''' Add additional headers for service bus. '''

    # version of the service is required for management service.
    request.headers.append(('x-ms-version', x_ms_version))

    # if method is PUT, POST, MERGE or DELETE content length is required
    if request.method in ['PUT', 'POST', 'MERGE', 'DELETE']:
        request.headers.append(('Content-Length', str(len(request.body))))

    # if it is not GET, HEAD request, must set content-type.
    if not request.method in ['GET', 'HEAD']:
        for name, value in request.headers:
            if 'content-type' == name.lower():
                break
        else:
            request.headers.append(('Content-Type', 'application/xml'))

    return request.headers

def _hosted_service_error_handler(http_error):
    ''' Simple error handler for service bus service. Will add more specific cases '''

    if http_error.status == 409:
        raise WindowsAzureConflictError(azure._ERROR_CONFLICT)
    elif http_error.status == 404:
        raise WindowsAzureMissingResourceError(azure._ERROR_NOT_FOUND)
    else:
        raise WindowsAzureError(azure._ERROR_UNKNOWN % http_error.message)

def _convert_hosted_service_to_xml(hosted_service):
    xml_content = '<?xml version="1.0" encoding="utf-8"?> \
<CreateHostedService xmlns="http://schemas.microsoft.com/windowsazure"> \
    <ServiceName>{name}</ServiceName> \
    <Label>{label}</Label> \
    <Description>{desc}</Description> \
    <Location>{location}</Location> \
</CreateHostedService>'
    xml_content = xml_content.format(name=hosted_service.name, label=base64.b64encode(hosted_service.label),
    desc=xml_escape(hosted_service.description), location=xml_escape(hosted_service.location))

    return xml_content

def _convert_deployment_to_xml(deployment):
    xml_content = '<?xml version="1.0" encoding="utf-8"?> \
<CreateDeployment xmlns="http://schemas.microsoft.com/windowsazure">\
    <Name>{deployment_name}</Name>\
    <PackageUrl>{package_url}</PackageUrl>\
    <Label>{deployment_label}</Label>\
    <Configuration>{configuration_file}</Configuration>\
    <StartDeployment>{start_deployment}</StartDeployment>\
    <TreatWarningsAsError>{warnings_as_errors}</TreatWarningsAsError>\
</CreateDeployment>'

    return xml_content.format(deployment_name=deployment.name, package_url=deployment.package_url,
                            deployment_label=base64.b64encode(deployment.label),
                            configuration_file=base64.b64encode(deployment.configuration),
                            start_deployment=str(deployment.start_deployment).lower(),
                            warnings_as_errors=str(deployment.treat_wranings_as_errors).lower())