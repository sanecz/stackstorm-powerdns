from lib.base import PowerDNSClient

class GetDetails(PowerDNSClient):
    def _run(self):
      return self.api.details
