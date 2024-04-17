from fastapi import FastAPI, Depends, Request
import urllib.parse
import requests
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import os
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
CLIENT_ID = "ID"
CLIENT_SECERT = "SECRET-KEY"
REDIRECT_URI = 'http://localhost:8000/callback'

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = 'https://oauth2.googleapis.com/token'
scope = 'https://www.googleapis.com/auth/youtube.readonly'
API_BASE_URL = 'https://www.googleapis.com/youtube/v3/playlists'
@app.get('/')
async def login():
    params = {
        'client_id' : CLIENT_ID,
        'redirect_uri' : REDIRECT_URI,
        'response_type' : 'code',
        'scope' : scope
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(auth_url)

@app.get('/callback')
async def callback(request: Request):
    session = request.session
    if 'error' in request.query_params:
        return JSONResponse({"error" : request.query_params['error']})
    if 'code' in request.query_params:
        req_body = {
            'client_id' : CLIENT_ID,
            'client_secret' : CLIENT_SECERT,
            'code' : request.query_params['code'],
            'grant_type' : 'authorization_code',
            'redirect_uri': REDIRECT_URI
        }
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded'
        }
        response = requests.post(TOKEN_URL, headers = headers, data=req_body)
        token_info = response.json()
        if 'access_token' not in token_info:
            return JSONResponse({"error" : "Access token not exist"})
        session['access_token'] = token_info['access_token']
        session['expires_in'] = token_info['expires_in']
        session['scope'] = token_info['scope']
        return RedirectResponse('/me')
    

@app.get('/me')
async def me(request: Request):
    session = request.session
    if 'access_token' not in session:
        return RedirectResponse('login')
    '''if datetime.now().timestamp() > session['expires_in']:
        return RedirectResponse('/refresh-token')'''
    
    headers = {
        'Authorization' : f"Bearer {session['access_token']}"
    }
    params = {
        'part' : 'snippet, status',
        'mine' : 'true',
        'maxResults' : 100
    }
    response = requests.get(API_BASE_URL,headers=headers, params=params)
    youtube_list = response.json()
    return JSONResponse(youtube_list)