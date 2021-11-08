from lib.base import PowerDNSClient

class GetRecords(PowerDNSClient):
    def _run(self):
      return self.api.records
