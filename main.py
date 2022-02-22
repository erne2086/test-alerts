import os 
from datetime import datetime,timezone,timedelta
import urllib.parse
from google.cloud import bigquery
import pymsteams
import random


AMOUNT = 0.9
AMOUNT_CHANGED = 1
PERCENTAGE = 1.01

myTeamsMessage = pymsteams.ConnectorCard("https://raxglobal.webhook.office.com/webhookb2/958f9af0-e01e-4dd7-a71d-9d6e8f85e1e3@570057f4-73ef-41c8-bcbb-08db2fc15c2b/IncomingWebhook/ba01367e4b864dcbaa9b3df47f354687/03c80c6a-e55a-4acf-ab93-0ed10e8993aa")

with open("quotes.txt") as f:
    quotes = f.read().splitlines()

def post_teams():
    daily_costs = get_daily_costs()
    flagged_costs = parse_cost_changes(daily_costs)
    if not flagged_costs:
        myTeamsMessage.text(f"Nothing to alert today \n {random.choice(quotes)}")
        myTeamsMessage.send()
        return
    for cost in flagged_costs:
        # Add Additional Integrations Here 
        myTeamsMessage.text(f"Alert: {cost}")
        myTeamsMessage.send()
    return
        

# Query to get Daily Costs
def get_daily_costs():
    print('getting daily cost')
    client = bigquery.Client()
    now = datetime.now(timezone.utc)
    prev_utc = now -timedelta(2)
    curr_utc = now - timedelta(1)
    
    QUERY = (
        f"""SELECT
        project.name as project,
        sku.id as sku_id,
        sku.description as sku_def,
        service.id as service_id,
        service.description as service_def,
        SUM(CASE WHEN EXTRACT(DAY FROM usage_start_time) = {prev_utc.day} THEN cost ELSE 0 END) AS prev_day,
        SUM(CASE WHEN EXTRACT(DAY FROM usage_start_time) = {curr_utc.day} THEN cost ELSE 0 END) AS curr_day,
        FROM `rax-architecture-sandbox.rax_gcp_billing.gcp_billing_export_v1_018918_BC80F7_298FEC`
        WHERE DATE_TRUNC(usage_start_time, DAY) = "{prev_utc.strftime('%Y-%m-%d')}" or DATE_TRUNC(usage_start_time, DAY) = "{curr_utc.strftime('%Y-%m-%d')}"
        GROUP BY 1,2,3,4,5
        ORDER BY 1;"""
    )
    query_job = client.query(QUERY)  # API request
    rows = query_job.result()
    print("Query finished")
    return rows

# Extract Large Spikes from Costs
def parse_cost_changes(rows):
    print("parsing cost changes")
    flagged_items = []
    for item in rows:
        i1 = float(item["prev_day"])
        i2 = float(item["curr_day"])
        if (i1 > AMOUNT or i2 > AMOUNT) and i1 != 0 and i2 != 0 and ((i2 /i1) >= PERCENTAGE or (i1 /i2) >= PERCENTAGE) or abs(i2-i1) >= AMOUNT_CHANGED:
            flagged_items.append(item)
    return flagged_items
  
def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    print("Started posting to MS Teams")
    post_teams()
    print("Finished posting to MS Teams")
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'