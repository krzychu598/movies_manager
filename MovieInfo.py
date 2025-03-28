import requests, os, json


class Movie:
    def __init__(self, info):
        self.year = int(info.get("year", 0))
        self.res = info.get("resolution", "-")
        self.path = info.get("path", "-")
        self.title = info.get("title", "-")
        self.director = info.get("director", "-")
        self.screenplay = info.get("screenplay", "-")
        self.cast = info.get("cast", "-")
        id = info.get("api", "-")
        if id != "-":
            self.id = info["api"].get("id", "-")
        else:
            self.id = "-"
        self.info = info
        self.info["year"] = int(self.info["year"])

    def displayable_info(self):
        dis = self.info.copy()
        dis.pop("api", None)
        dis.pop("cast", None)
        dis.pop("screenplay", None)
        dis.pop("path", None)
        return dis

    def get_image_path(self):
        if self._is_poster():
            return self._get_poster_path()
        elif self._is_frame():
            return self._get_frame_path()
        else:
            print(f"Couldn't find image for {self.title}")

    def update_movie_info(self, base_url, api_key, force=False):
        if self.info.get("api", "-") != "-" and not force:
            return
        url = f"{base_url}search/movie?include_adult=true&query={self.title}&api_key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for movie in data["results"]:
                if movie["release_date"].split("-")[0] == str(self.year):
                    self._update_api_dict(movie)
                    return
            print(f"Movie {self.title} wasn't found")
        else:
            print(f"Error {response.status_code}")

    def update_cast_info(self, api_key, force=False):
        if self.info.get("director", "-") != "-" and not force:
            return
        url = f"https://api.themoviedb.org/3/movie/{self.id}/credits?api_key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            self._update_cast_dict(response.json())
        else:
            print(f"Credits not found for {self.title}")

    def update_poster(self, api_key, force=False):
        if self._is_poster() and not force:
            return
        try:
            url = f"https://image.tmdb.org/t/p/original{self.info["api"]["poster_path"]}?api_key={api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                with open(
                    f"{os.path.join(self.path, "images", "poster.jpg")}", "wb"
                ) as f:
                    f.write(response.content)
            else:
                print(f"Could't get poster for {self.title}")
        except:
            print(f"Could't get poster for {self.title}")

    def _update_api_dict(self, new_dict):
        self.id = new_dict["id"]
        self.info["api"] = {
            "id": self.id,
            "genre_ids": new_dict["genre_ids"],
            "poster_path": new_dict["poster_path"],
        }
        self._save_info_to_file()

    def _update_cast_dict(self, new_dict):
        # cast: name, id, popularity, order, character
        # crew: job(Director, Screenplay), name, id
        screenplay = []
        director = []
        cast = []
        for person in new_dict["crew"]:
            if person["job"] == "Director":
                director.append(person["name"])
            if person["job"] == "Screenplay" or person["job"] == "Dialogue":
                screenplay.append(person["name"])
        self.info["director"] = director[0]
        self.info["screenplay"] = list(set(screenplay))
        self.director = director[0]
        self.screenplay = screenplay
        for person in new_dict["cast"]:
            if person["order"] > 4:
                break
            if person["gender"] == 2:
                gender = "Male"
            else:
                gender = "Female"
            cast.append(
                {"name": person["name"], "as": person["character"], "gender": gender}
            )

        self.info["cast"] = cast
        self._save_info_to_file()

    def _save_info_to_file(self):
        with open(os.path.join(self.path, "tags.json"), "w", encoding="utf-8") as f:
            json.dump(self.info, f, ensure_ascii=False, indent=4)

    def _get_poster_path(self):
        return os.path.join(self.path, "images", "poster.jpg")

    def _get_frame_path(self):
        for image in os.listdir(os.path.join(self.path, "images")):
            return os.path.join(self.path, "images", image)

    def _is_poster(self):
        try:
            with open(self._get_poster_path(), "rb"):
                return True
        except:
            return False

    def _is_frame(self):
        try:
            with open(self._get_frame_path(), "rb"):
                return True
        except:
            return False
