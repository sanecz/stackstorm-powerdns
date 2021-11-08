# coding=utf-8
from st2common import log as logging
from st2common.runners.base_action import Action
from powerdns.exception import PDNSCanonicalError, PDNSError

import powerdns

__all__ = ["PowerDNSClient"]

LOG = logging.getLogger(__name__)


class PowerDNSClientError(Exception):
    def __init__(self, message):
        self.message = message
                    

class PowerDNSClient(Action):
    def __init__(self, config, timeout=5):
        super(PowerDNSClient, self).__init__(config)
        self.timeout = timeout
        self.api_key = config.get("api_key")
        self.api_url = config.get("api_url")

        self._init_powerdns()

    def _init_powerdns(self):
        self.api_client = powerdns.PDNSApiClient(
            api_endpoint=self.api_url,
            api_key=self.api_key,
            timeout=self.timeout
        )
        self._api = powerdns.PDNSEndpoint(self.api_client)

    def _run(self, *args, **kwargs):
        raise NotImplementedError

    def _select_server_id(self, server_id):
        for server in self._api.servers:
            if str(server) == server_id:
                self.api = server
        else:
            raise PowerDNSClientError("Server not found")

    def _select_zone(self, zone_name):
        self.api = self.api.get_zone(zone_name)
        if not self.api:
            raise PowerDNSClientError("Zone not found")
        
    def run(self, server_id, *args, **kwargs):
        try:
            self._select_server_id(server_id)
            # remove server_id from args
            args = list(args)
            args.pop(args.index(server_id))
            if "zone_name" in kwargs:
                self._select_zone(kwargs.pop("zone_name"))
            return (True, self._run(*args, **kwargs))
        except (PowerDNSClientError, PDNSError, PDNSCanonicalError) as e:
            return (False, e)
    
