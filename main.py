import os
import tokens
from notionapi import NotionClient
from keepalive import keepalive


os.system("cls" if os.name == "nt" else "clear")
print("Monitoring..")
try:
    client = NotionClient(tokens.notion_token, tokens.database_id)
    keepalive()
    client.monitor_database()
except KeyboardInterrupt:
    print("Closed Program !")
