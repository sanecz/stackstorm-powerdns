from lib.base import PowerDNSClient

class GetConfig(PowerDNSClient):
    def _run(self):
      return self.api.config
