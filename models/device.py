import sys
import os
import binascii

from ..base_request import BaseRequest
from ..resources import Message
from .config import Config
from ..settings import Settings

class Device(object):

    def __init__(self):
        self.base_request = BaseRequest()
        self.config = Config()
        self.settings = Settings()

    def get(self, uuid):
        params = {
            'filter': 'uuid',
            'eq': uuid
        }
        try:
            return self.base_request.request('device', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))['d'][0]
        except IndexError:
            # found no device
            print(Message.NO_DEVICE_FOUND.format(value=uuid, dev_att="uuid"))
        except:
            # unexpected exception
            raise

    def get_all(self):
        return self.base_request.request('device', 'GET', endpoint=self.settings.get('pine_endpoint'))['d']

    def get_all_by_application(self, name):
        params = {
            'filter': 'app_name',
            'eq': name
        }
        app = self.base_request.request('application', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))['d']
        if app:
            params = {
                'filter': 'application',
                'eq': app[0]['id']
            }
            return self.base_request.request('device', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))['d']

    def get_by_name(self, name):
        params = {
            'filter': 'name',
            'eq': name
        }
        return self.base_request.request('device', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))['d']

    def get_name(self, uuid):
        return self.get(uuid)['name']

    def get_application_name(self, uuid):
        app_id = self.get(uuid)['application']['__id']
        params = {
            'filter': 'id',
            'eq': app_id
        }
        return self.base_request.request('application', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))['d'][0]['app_name']
        
    def has(self, uuid):
        params = {
            'filter': 'uuid',
            'eq': uuid
        }
        if len(self.base_request.request('device', 'GET', params=params, endpoint=self.settings.get('pine_endpoint'))) > 0:
            return True
        return False 

    def is_online(self, uuid):
        return self.get(uuid)['is_online']

    def get_local_ip_address(self, uuid):
        if self.is_online(uuid):
            device = self.get(uuid)
            ips = device['ip_address'].split()
            ips.remove(device['vpn_address'])
            return ips
        else:
            print(Message.DEVICE_OFFLINE.format(uuid=uuid))

    def remove(self, uuid):
        params = {
            'filter': 'uuid',
            'eq': uuid
        }
        return self.base_request.request('device', 'DELETE', params=params, endpoint=self.settings.get('pine_endpoint'))

    def identify(self, uuid):
        data = {
            'uuid': uuid
        }
        return self.base_request.request('/blink', 'POST', data=data)

    def rename(self, uuid, new_name):
        if self.has(uuid):
            params = {
                'filter': 'uuid',
                'eq': uuid
            }
            data = {
                'name': new_name
            }
            return self.base_request.request('device', 'PATCH', params=params, data=data, endpoint=self.settings.get('pine_endpoint'))
        else:
            print(Message.NO_DEVICE_FOUND.format(value=uuid, dev_att="uuid"))


    def note(self, uuid, note):
        if self.has(uuid):
            params = {
                'filter': 'uuid',
                'eq': uuid
            }
            data = {
                'note': note
            }
            return self.base_request.request('device', 'PATCH', params=params, data=data, endpoint=self.settings.get('pine_endpoint'))
        else:
            print(Message.NO_DEVICE_FOUND.format(value=uuid, dev_att="uuid"))

    def get_display_name(self, device_type_slug):
        device_type_found = self.config.get_device_type()
        display_name = [device['name'] for device in device_type_found
                        if device['slug'] == device_type_slug]
        if display_name:
            return display_name[0]
        else:
            print(Message.UNSUPPORTED_DEVICE.format(value=device_type_slug))

    def get_device_slug(self, device_type_name):
        device_type_found = self.config.get_device_type()
        slug_name = [device['slug'] for device in device_type_found
                        if device['name'] == device_type_name]
        if slug_name:
            return slug_name[0]
        else:
            print(Message.UNSUPPORTED_DEVICE.format(value=device_type_name))

    def get_supported_device_types(self):
        device_type_found = self.config.get_device_type()
        supported_device = [device['name'] for device in device_type_found]
        return supported_device

    def get_manifest_by_slug(self, slug):
        device_type_found = self.config.get_device_type()
        manifest = [device for device in device_type_found
                        if device['slug'] == slug]
        if manifest:
            return manifest
        else:
            print(Message.UNSUPPORTED_DEVICE.format(value=slug))

    def generate_uuid(self):
        # From resin-sdk
        # I'd be nice if the UUID matched the output of a SHA-256 function,
        # but although the length limit of the CN attribute in a X.509
        # certificate is 64 chars, a 32 byte UUID (64 chars in hex) doesn't
        # pass the certificate validation in OpenVPN This either means that
        # the RFC counts a final NULL byte as part of the CN or that the
        # OpenVPN/OpenSSL implementation has a bug.
        rand_string = os.urandom(31)
        return binascii.hexlify(rand_string)

    # NOT YET IMPLEMENTED, WAITING FOR AUTH
    #def register(self, app_name, uuid):
