import numpy as np
import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
from auth import register_user, authenticate_user, get_user_data, update_user_data
from database import load_data_from_db
from recommender import recommend_songs, get_song_data
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import requests


def load_musicurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def display_recommendations(recommendations):
    st.write("Recommended Songs Are:")
    for track in recommendations:
        st.write(f"{track['name']} by {track['artists']} from the album {track.get('album', 'Unknown Album')}")
        track_id = track.get("id")
        if track_id:
            track_url = f"https://open.spotify.com/embed/track/{track_id}"
            st.markdown(
                f'<iframe src="{track_url}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
                unsafe_allow_html=True)
        else:
            st.write("No album art available")


def main():
    st.title("Music Recommendation System")

    music_data = load_data_from_db()
    number_cols = list(music_data.select_dtypes(np.number).columns)

    song_cluster_pipeline = Pipeline([('scaler', StandardScaler()), ('kmeans', KMeans(n_clusters=20, verbose=False))])
    song_cluster_pipeline.fit(music_data[number_cols])
    song_cluster_labels = song_cluster_pipeline.predict(music_data[number_cols])
    music_data['cluster_label'] = song_cluster_labels

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Logged in successfully")
            else:
                st.error("Invalid username or password")

        st.subheader("Register")
        reg_username = st.text_input("New Username")
        reg_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            message = register_user(reg_username, reg_password)
            st.success(message) if "successfully" in message else st.error(message)
    else:
        st.sidebar.button("Вийти з облікового запису",
                          on_click=lambda: st.session_state.update({"authenticated": False}))
        st.sidebar.button("Редагування профілю користувача",
                          on_click=lambda: st.session_state.update({"profile_tab": True}))

        st.success("You are logged in. Enjoy the music recommendations!")

        if st.session_state.get("profile_tab"):
            st.session_state.profile_tab = False
            st.subheader("Profile")
            user_data = get_user_data(st.session_state.username)

            st.write("Username:", user_data["username"].values[0])
            new_password = st.text_input("Введіть новий пароль для оновлення даних", type="password")
            new_username = st.text_input("Введіть нову пошту для оновлення даних")
            if st.button("Update Profile"):
                if new_password:
                    update_user_data(st.session_state.username, "password", new_password)
                    st.success("Password updated successfully")
                if new_username:
                    update_user_data(st.session_state.username, "username", new_username)
                    st.success("Username updated successfully")
                    st.session_state.username = new_username

            st.button("Вернуться к рекомендациям", on_click=lambda: st.session_state.update({"profile_tab": False}))

            st.write("Profile customization options coming soon...")
        else:
            lottie_music = load_musicurl("https://assets5.lottiefiles.com/packages/lf20_V9t630.json")
            st_lottie(lottie_music, speed=1, height=200, key="initial")

            track_name = st.text_input("Впишіть назву пісні:")
            artist_name = st.text_input("Впишіть ім'я виконавця пісні:")

            if st.button("Отримати рекомендації"):
                if track_name and artist_name:
                    song_list = [{'name': track_name, 'artist': artist_name}]
                    recommendations = recommend_songs(song_list, music_data, number_cols, song_cluster_pipeline)
                    if recommendations:
                        display_recommendations(recommendations)
                    else:
                        st.error("No recommendations found")
                else:
                    st.error("Please fill in both fields.")


if __name__ == "__main__":
    main()
