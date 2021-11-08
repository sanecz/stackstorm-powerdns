from lib.base import PowerDNSClient

class GetServers(PowerDNSClient):
    def _run(self):
      return self.api.servers
