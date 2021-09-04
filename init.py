# # Spotify Playlist Analysis



# - Passes a username
# - Get public playlists for provided username
# - Loop through each song in each playlist
# - Analyze using Spotipy

# +
# Imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np

# Static Params
client_id = '0c6a16bdfe8e44b59e06c0b8142a294c'
client_secret = '371eb3ba005a44859d2297234e3ebbd3'
scope = 'playlist-read-private'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

# Dynamic Params
user = 'FlynancialAnalyst'

# Optional Params (for non-public or specific playlists)
extraIDArray = [
    '1XaqTYrxGv1PVKZag8Bulg','6NPbE4WDbQA3pGTNn1SxK0','5BjgUh7bUh0dxOQfGecrBc','2RuewB7QViLIKDXLgvXyFl','5vKWEZyWLeySNen5NIOe6O'
                ,'2OZVlENh6kAfqpRyPIPyl7','7ff16ei2NdpN42coQJxsE2', '37i9dQZF1DXby8tlLbzqaH', '3a54WQYSUPwjgGmfd4JIII',
    '1ZRJxFAd8hBk4v5Ag3D1zM', '1XaqTYrxGv1PVKZag8Bulg', '4hV7KvQUKQjtlXbcVYWFS9'
#     ,'1PKYiQbbX3Fak5c9SiYpFQ'
]


# +
def getUserPublicPlaylists(user, extraIDArray=''):
    playlistArray = []
    response = sp.user_playlists(user, limit=50)
    for i, item in enumerate(response['items']):
        playlistArray.append(item['id'])
        
    if extraIDArray:
        for i in range(len(extraIDArray)):
            if extraIDArray[i] not in playlistArray:
                print(" --- Non-Public ID Added")
                playlistArray.append(extraIDArray[i])
    return playlistArray

def getList(dict):
    list = []
    for key in dict.keys():
        list.append(key)
    return list

def get_playlist_tracks(username, playlist_id):
    results = sp.user_playlist_tracks(username, playlist_id)
    print(getList(results))
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


# +
def playlistAnalysis(playListId):
    results = pd.DataFrame([], columns=['TrackName','TrackURI','Danceability','Energy','Key','Loudness','Mode','Speechiness','Acousticness','Instrumentalness',
                                     'Liveness','Valence','Tempo','Duration (s)'])
    
    data = sp.playlist(playListId, fields=None, market=None, additional_types=('track', ))
    description = data['description']
    playlistName = data['name']
    print("Analayzing Playlist --> " + playlistName)
    firstPage = data['tracks']
    tracks = firstPage['items']
    expecting = data['tracks']['total']
    print('Length of initial tracks ' + str(len(tracks)))
    print('Expecting ' + str(expecting) + ' tracks')
    
    while firstPage['next']:
    # Here we are changing firstpage with each new call to 'next'
    # by changing the page, the while checks again for 'next'
    # if next is not present, while cuts off
        firstPage = sp.next(firstPage)
        tracks.extend(firstPage['items'])
        
    print(str(len(tracks)) + ' retrieved')

    for i in range(len(tracks)):
        track = pd.DataFrame([
            [tracks[i]['track']['name'],
            tracks[i]['track']['uri']]], 
            columns=['TrackName','TrackURI'])
        
        if pd.isnull(track.loc[0, 'TrackURI']):
            continue
        else:
            audioData = sp.audio_features(tracks[i]['track']['uri'])
            if audioData[0] == None:
                continue
            else:
                track['Danceability'] = audioData[0]['danceability'] or 0
                track['Energy'] = audioData[0]['energy'] or 0
                track['Key'] = audioData[0]['key'] or 0
                track['Loudness'] = audioData[0]['loudness'] or 0
                track['Mode'] = audioData[0]['mode'] or 0
                track['Speechiness'] = audioData[0]['speechiness'] or 0
                track['Acousticness'] = audioData[0]['acousticness'] or 0
                track['Instrumentalness'] = audioData[0]['instrumentalness'] or 0
                track['Liveness'] = audioData[0]['liveness'] or 0
                track['Valence'] = audioData[0]['valence'] or 0
                track['Tempo'] = audioData[0]['tempo'] or 0
                track['Duration (s)'] = audioData[0]['duration_ms'] / 1000 or 0
                results = results.append(track)
    
    playlistAvgs = pd.DataFrame([], columns=['PlaylistName','NumTracks','Danceability','Energy','Key','Loudness','Mode','Speechiness','Acousticness','Instrumentalness',
                                 'Liveness','Valence','Tempo','Duration (s)'])
    average = pd.DataFrame(
            [
                [
                    playlistName,
                    len(results),
                    results['Danceability'].mean() or 0,
                    results['Energy'].mean() or 0,
                    results['Key'].mean() or 0,
                    results['Loudness'].mean() or 0,
                    results['Mode'].mean() or 0,
                    results['Speechiness'].mean() or 0,
                    results['Acousticness'].mean() or 0,
                    results['Instrumentalness'].mean() or 0,
                    results['Liveness'].mean() or 0,
                    results['Valence'].mean() or 0,
                    results['Tempo'].mean() or 0,
                    results['Duration (s)'].mean() or 0
                ]
            ], 
                columns=['PlaylistName','NumTracks','Danceability','Energy', 'Key', 'Loudness', 'Mode', 'Speechiness', 'Acousticness', 'Instrumentalness', 'Liveness', 'Valence',
                         'Tempo', 'Duration (s)']
            )
    playlistAvgs = playlistAvgs.append(average)
    
    return [results, playlistAvgs]

def execute(user, extraIDArray=''):
    playlistURIs = getUserPublicPlaylists(user, extraIDArray)
    print("Pulling data for first URI to create DF: " + str(playlistURIs[0]))
    allPlaylists = playlistAnalysis(playlistURIs[0])[1]
    print(" --- Complete --- \n")

    for uri in playlistURIs[1:]:
        print("Pulling data for URI: " + str(uri))
        allPlaylists = allPlaylists.append(playlistAnalysis(uri)[1])
        print(" --- Complete --- \n")

    allPlaylists.sort_values(by=['Duration (s)']).reset_index(drop=True)
    
    return allPlaylists
    


# -

allPlaylists = execute(user, extraIDArray)

# +

allPlaylists['NumTracks'] = allPlaylists['NumTracks'].astype(float)
for column in allPlaylists.columns:
    if column in ['PlaylistName','NumTracks']:
        continue
    print(column + ' Top Three')
    topThree = allPlaylists.nlargest(3, column).loc[:,'PlaylistName']
    topThree = topThree.values
    for i in range(len(topThree)):
        print(str(i+1) + ': ' + topThree[i])
    print('- - - - - - - - - - - - - - - - -')
# -

allPlaylists.sort_values('Danceability', ascending=False)
