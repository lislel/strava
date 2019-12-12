#!/usr/bin/env python
from flask import Flask, abort, request, render_template, redirect, session
from uuid import uuid4
import requests
import requests.auth
import urllib
import csv
import polyline
import os
import math
import json
import pandas

CLIENT_ID = 28599  # Fill this in with your client ID
CLIENT_SECRET = '0b89acaaafd09735ed93707d135ebf3519bfbfd7' # Fill this in with your client secret
REDIRECT_URI = "http://localhost:65010/reddit_callback"
MTS = {"washington": [44.2706, -71.3033, []], "adams": [44.3203, -71.2909, []], "jefferson": [44.3045, -71.3176, []], "monroe": [44.2556, -71.3220, []], 'Madison':[44.32833333,-71.27833333, []],'Lafayette': [44.16055556,-71.64416667, []], 'Lincoln': [44.15972222,-71.65166667, []], 'South Twin': [44.19027778,-71.55888889, []], 'Carter Dome':[43.26694444,-71.17888889,[]]}
mts_dict = {'washington': [], 'adams': [], 'monroe': [], 'jefferson': [], 'Madison':[], 'Lafayette':[], 'South Twin': [], 'Lincoln':[], 'Carter Dome':[]}
basedir = os.path.abspath(os.path.dirname(__file__))


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
app.secret_key = 'blah'

@app.route('/')
def authorize():
    #text = '<a href="%s">Authenticate with strava</a>'
    #return text % make_authorization_url()
    x=make_authorization_url()
    return render_template('authorize.html', myurl=x)

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

@app.route('/results')
def results():
    fin = session.get('fin')
    unfin = session.get('unfin')
    return render_template('index.html', dkeys = fin.keys(), nh = fin, unfin = unfin)


@app.route('/home')
def home2():
    return render_template('home2.html')

@app.route('/visualize')
def my_runs():
    runs = []
    with open("runs.csv", "r") as runs_file:
        reader = csv.DictReader(runs_file)

        for row in reader:
            runs.append(row["polyline"])

    m2 = session.get('marks', None)
    m3 = []
    for key in m2.keys():
        m3.append(m2[key])

    print('m3 =', m3)
    return render_template("leaflet.html", runs = json.dumps(runs), map_markers = m3)


@app.route('/reddit_callback')
def index():
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
    fin, unfin = get_username(access_token)
    session['fin'] = fin
    session['unfin'] = unfin
    return render_template('home2.html')


def get_token(code):
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

def get_hypot(pt, lat, lon):
    x_ind = pt[0] - lat
    y_ind = pt[1] - lon
    hypot = math.sqrt(math.pow(x_ind, 2) + math.pow(y_ind, 2))
    return hypot

def get_username(access_token):
    headers = base_headers()
    headers.update({'Authorization': 'Bearer ' + access_token})
    page = 1
    with open("runs.csv", "w") as runs_file:
        writer = csv.writer(runs_file, delimiter=",")
        writer.writerow(["id", "polyline"])

    while True:
        json_response = requests.get("https://www.strava.com/api/v3/activities", headers=headers, params={'page': page, 'per_page': 200})
        response = json_response.json()
        print(response)
        if page == 40:
            break
        else:
            page += 1
            i = 0
            for item in response:
                i += 1
                if item['start_latlng'] is not None:
                    if item['type'] != 'Bike' and item['start_latlng'][0] >= 43.82 and item['start_latlng'][0] <= 44.62 and item['start_latlng'][1] >= -71.97 and item['start_latlng'][1] <= -71.012:
                        if item['elev_high'] > 1219:
                            line = item['map']['summary_polyline']
                            points = polyline.decode(line)
                            mts_bagged = []
                            for key in MTS.keys():
                                min_dist = 10000000
                                for pt in points:
                                    hypot = get_hypot(pt, MTS[key][0], MTS[key][1])
                                    if hypot < min_dist:
                                        min_dist = hypot
                                if min_dist <= 0.000833:
                                    #add id to list of activities that have touched this mountain
                                    MTS[key][2].append(item['id'])
                                    # map the peaks summited on this activity to the activity
                                    mts_dict[key].append([item['name'], item['id']])
                                    with open("runs.csv", "a") as runs_file:
                                        writer = csv.writer(runs_file, delimiter=",")
                                        writer.writerow([item["id"], item['map']['summary_polyline']])

    unfin = []
    finished = {}
    for key in MTS.keys():
        if len(MTS[key][2]) == 0:
            MTS[key][2] = 'missing'
            unfin.append(key)
        else:
            finished[key] = mts_dict[key]


    session['marks'] = MTS
    return finished, unfin


if __name__ == '__main__':
    app.run(debug=True, port=65010)
    session.init_app(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'