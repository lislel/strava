#!/usr/bin/env python
from flask import Flask, abort, request, render_template
from uuid import uuid4
import requests
import requests.auth
import urllib
import csv


CLIENT_ID = 28599  # Fill this in with your client ID
CLIENT_SECRET = '0b89acaaafd09735ed93707d135ebf3519bfbfd7' # Fill this in with your client secret
REDIRECT_URI = "http://localhost:65010/reddit_callback"


def user_agent():
    '''reddit API clients should each have their own, unique user-agent
    Ideally, with contact info included.

    e.g.,
    '''
    user_age = request.headers.get('User-Agent')

    return "oauth2-sample-app by /u/%s" % user_age

    # raise NotImplementedError()


def base_headers():
    return {"User-Agent": user_agent()}


app = Flask(__name__)


@app.route('/')
def homepage():
    text = '<a href="%s">Authenticate with strava</a>'
    return text % make_authorization_url()


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": CLIENT_ID,
              "response_type": 'code',
              "redirect_uri": REDIRECT_URI,
              "approval_prompt": "auto",
              "scope": "activity:read_all"}
    url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode(params)
    return url


# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache.
def save_created_state(state):
    pass


def is_valid_state(state):
    return True


@app.route('/reddit_callback')
def reddit_callback():
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    state = request.args.get('state', '')
    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        abort(403)
    code = request.args.get('code')
    print('code =', code)
    access_token = get_token(code)
    print('access token', access_token)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    # return get_username(access_token)
    nh = get_username(access_token)
    return render_template('index.html', len = len(nh), nh = nh)



def get_token(code):
    #client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "client_id": CLIENT_ID,
                 "client_secret": CLIENT_SECRET,
                 "code": code,
                 "redirect_uri": REDIRECT_URI}
    headers = base_headers()
    response = requests.post("https://www.strava.com/oauth/token",
                             headers=headers,
                             data=post_data)
    token_json = response.json()
    print('token json', token_json)
    return token_json["access_token"]


def get_username(access_token):
    headers = base_headers()
    headers.update({'Authorization': 'Bearer ' + access_token})
    page = 1
    nh = []
    with open("runs.csv", "w") as runs_file:
        writer = csv.writer(runs_file, delimiter=",")
        writer.writerow(["id", "polyline"])

    while True:
        response = requests.get("https://www.strava.com/api/v3/activities", headers=headers, params={'page': page})
        me_json = response.json()
        #if len(me_json) == 0:
        if page == 10:
            break
        else:
            page += 1
            i = 0
            for item in me_json:
                i += 1
                if item['start_latlng'] is not None:
                    if item['type'] != 'Bike' and item['start_latlng'][0] >= 43.82 and item['start_latlng'][0] <= 44.62 and item['start_latlng'][1] >= -71.97 and item['start_latlng'][1] <= -71.012:
                        if item['elev_high'] > 1219:
                            nh.append(item)
                            print(item)
                            with open("runs.csv", "a") as runs_file:
                                writer = csv.writer(runs_file, delimiter=",")
                                writer.writerow([item["id"], item['map']['summary_polyline']])
    #return json.dumps(nh)
    return nh


if __name__ == '__main__':
    app.run(debug=True, port=65010)