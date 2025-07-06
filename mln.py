import requests
from urllib.parse import urlencode

from mln_secret import MLN_SECRET  # not tracked in git

COAST_GUARD_URL = "http://localhost:5000"
MLN_BASE_URL = "https://mln.lcdruniverse.org"
# MLN_BASE_URL = "http://localhost:8000"
MLN_MAILBOX_URL = f"{MLN_BASE_URL}/mln/private_view/default"
MLN_API_RANK = "/api/coastguard/rank"  # see mln-docs/mln.md

SESSION_TO_USERNAME = {}

def get_login_url(session_id):
  # NOTE: The session_id goes into the redirect url, NOT the normal query paramters
  # This is because MLN doesn't care about our session_id, but we want MLN to pass
  # it back to us untouched so we can use that to know who signed in.
  post_login_url = f"{COAST_GUARD_URL}/api/login?session_id={session_id}"
  query_string = urlencode({
    "respond_with_username": "yes",
    "next": post_login_url,
  })
  return f"{MLN_BASE_URL}/accounts/login/?{query_string}"

def on_login(session_id, username):
  SESSION_TO_USERNAME[session_id] = username

def submit_rank(username, rank):
  body = {
    "secret": MLN_SECRET,
    "username": username,
    "rank": rank,
  }
  url = f"{MLN_BASE_URL}{MLN_API_RANK}"
  response = requests.post(url, json=body)
  print(f"Submitted rank {rank} for {username}. Got response: {response.status_code}, {response.text}")
