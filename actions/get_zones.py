from lib.base import PowerDNSClient

class GetZones(PowerDNSClient):
    def _run(self):
      return self.api.zones
