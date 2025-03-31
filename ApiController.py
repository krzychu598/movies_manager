import requests


def get_api_key():
    try:
        with open("api_key.txt", "r") as f:
            return f.readline()
    except:
        print("No api key found!")


def get_movie_info(title, year):
    url = f"https://api.themoviedb.org/3/search/movie?include_adult=true&query={title}&api_key={get_api_key()}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for movie in data["results"]:
            if movie["release_date"].split("-")[0] == str(year):
                return movie
    else:
        print(f"Error {response.status_code}")


def get_cast_info(id):
    url = f"https://api.themoviedb.org/3/movie/{id}/credits?api_key={get_api_key()}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()


def get_poster(poster_path):
    url = f"https://image.tmdb.org/t/p/original{poster_path}?api_key={get_api_key()}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content


def get_imdb_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/external_ids?api_key={get_api_key()}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["imdb_id"]
