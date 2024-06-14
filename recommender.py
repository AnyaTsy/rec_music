import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scipy.spatial.distance import cdist
from collections import defaultdict

def get_mean_vector(song_list, spotify_data, number_cols):
    song_vectors = []
    for song in song_list:
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            continue
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)
    song_matrix = np.array([vec for vec in song_vectors if len(vec) == len(number_cols)])
    return np.mean(song_matrix, axis=0) if len(song_matrix) > 0 else np.zeros(len(number_cols))

def flatten_dict_list(dict_list):
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []

    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)

    return flattened_dict

def recommend_songs(song_list, spotify_data, number_cols, song_cluster_pipeline, n_songs=9):
    metadata_cols = ['name', 'artists', 'id']
    if 'album' in spotify_data.columns:
        metadata_cols.append('album')

    song_dict = flatten_dict_list(song_list)
    song_center = get_mean_vector(song_list, spotify_data, number_cols)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))
    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[metadata_cols].to_dict(orient='records')

def get_song_data(song, spotify_data):
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name']) & (spotify_data['artists'] == song['artist'])].iloc[0]
        return song_data
    except IndexError:
        return None
