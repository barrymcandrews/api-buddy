from bottle import route, run, request
import spotipy
from spotipy import oauth2

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '05525c6c58224d76bedcc89531844418'
SPOTIPY_CLIENT_SECRET = 'b1af7a3d81734930b85d78455e308c59'
SPOTIPY_REDIRECT_URI = 'http://192.52.164.102:8080'
SCOPE = 'user-read-playback-state'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE, cache_path=CACHE)


@route('/')
def index():

    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        sp = spotipy.Spotify(auth=access_token)
        current_song = sp.current_user_playing_track()
        if current_song is not None:
            song_display = "<message type=\"scroll\" color=\"#84bd00\"> NOW PLAYING:   " + \
                          current_song['item']['name'] + " - "
            for i in range(len(current_song['item']['artists'])):
                if i != len(current_song['item']['artists']) - 1:
                    song_display += (current_song['item']['artists'][i]['name'] + ", ")
                else:
                    song_display += (current_song['item']['artists'][i]['name'] + "</message>")
                    print(song_display)
                    out_file = open("/tmp/led-source-spotify", "w", encoding="utf-8")
                    out_file.write(song_display)
                    out_file.close()
        while True:
            check_song = sp.current_user_playing_track()
            if check_song is not None:
                if (current_song is None or current_song['item']['name'] != check_song['item']['name'] or
                        current_song['item']['name'][0] != check_song['item']['name'][0]):
                    current_song = sp.current_user_playing_track()
                    if current_song is not None:
                        song_display = "<message type=\"scroll\" color=\"#84bd00\">NOW PLAYING:   " + current_song['item'][
                            'name'] + " - "
                        for i in range(len(current_song['item']['artists'])):
                            if i != len(current_song['item']['artists']) - 1:
                                song_display += (current_song['item']['artists'][i]['name'] + ", ")
                            else:
                                song_display += (current_song['item']['artists'][i]['name'] + "</message>")
                                print(song_display)
                                out_file = open("/tmp/led-source-spotify", "w", encoding="utf-8")
                                out_file.write(song_display)
                                out_file.close()

        # print("Access token available! Trying to get user information...")
        # sp = spotipy.client.Spotify(access_token)
        # results = sp.current_playback()
        # return results

    else:
        return htmlForLoginButton()


def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton


def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


run(host="0.0.0.0", port=8080)
