import requests
from urllib.parse import urlencode

from mln_secret import MLN_API_TOKEN  # not tracked in git

COAST_GUARD_URL = "http://localhost:5000"
COAST_GUARD_CLIENT_ID = "bf74c09a-09a0-4cfe-a00c-40755c6a8ad2"

MLN_BASE_URL = "https://mln.lcdruniverse.org"
# MLN_BASE_URL = "http://localhost:8000"
MLN_MAILBOX_URL = f"{MLN_BASE_URL}/mln/private_view/default"
MLN_API_RANK = "/api/coastguard/rank"  # see mln-docs/mln.md
MLN_API_OAUTH = "/oauth/token"

SESSION_TO_TOKEN = {}

def get_login_url(session_id):
  query_string = urlencode({
    "client_id": COAST_GUARD_CLIENT_ID,
    "session_id": session_id,
    "redirect_url": f"{COAST_GUARD_URL}/api/login",
  })
  return f"{MLN_BASE_URL}/oauth?{query_string}"

def on_login(session_id, auth_code):
  # Use the auth_code to request an access token from MLN
  body = {
    "api_token": MLN_API_TOKEN,
    "auth_code": auth_code,
  }
  url = f"{MLN_BASE_URL}{MLN_API_OAUTH}"
  response = requests.post(url, json=body)
  if not response: return
  access_token = response.json()["access_token"]
  print(f"Got access token! {access_token}")
  SESSION_TO_TOKEN[session_id] = access_token

def submit_rank(username, rank):
  body = {
    "api_token": MLN_API_TOKEN,
    "username": username,
    "rank": rank,
  }
  url = f"{MLN_BASE_URL}{MLN_API_RANK}"
  response = requests.post(url, json=body)
  print(f"Submitted rank {rank} for {username}. Got response: {response.status_code}, {response.text}")
