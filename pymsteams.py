import urllib3
import json
from socket import timeout


class TeamsWebhookException(Exception):
    """custom exception for failed webhook call"""
    pass


class ConnectorCard:
    def __init__(self, hookurl, http_timeout=60):
        self.http = urllib3.PoolManager()
        self.payload = {}
        self.hookurl = hookurl
        self.http_timeout = http_timeout

    def text(self, mtext):
        self.payload["text"] = mtext
        return self

    def send(self):
        headers = {"Content-Type":"application/json"}
        r = self.http.request(
                'POST',
                f'{self.hookurl}',
                body=json.dumps(self.payload).encode('utf-8'),
                headers=headers, timeout=self.http_timeout)
        if r.status == 200: 
            return True
        else:
            raise TeamsWebhookException(r.reason)


if __name__ == "__main__":
    myTeamsMessage = ConnectorCard("https://raxglobal.webhook.office.com/webhookb2/958f9af0-e01e-4dd7-a71d-9d6e8f85e1e3@570057f4-73ef-41c8-bcbb-08db2fc15c2b/IncomingWebhook/ba01367e4b864dcbaa9b3df47f354687/03c80c6a-e55a-4acf-ab93-0ed10e8993aa")
    myTeamsMessage.text("this is my test message to the teams channel.")
    myTeamsMessage.send()
