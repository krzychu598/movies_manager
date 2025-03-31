import requests, os, json
import ApiController


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
            self.imdb_id = info["api"].get("imdb_id", "-")
        else:
            self.id = "-"
            self.imdb_id = "-"

        self.info = info
        self.info["year"] = int(self.info["year"])

    def update_movie(self, force=False):
        self.update_movie_info(force=force)
        self.update_poster()
        self.update_cast_info(force=force)
        self.get_imdb_link(force=force)

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

    def update_movie_info(self, force=False):
        if self.info.get("api", "-") != "-" and not force:
            return
        movie_info = ApiController.get_movie_info(self.title, self.year)
        if not movie_info:
            print(f"Movie {self.title} wasn't found")
            return
        self._update_api_dict(movie_info)

    def update_cast_info(self, force=False):
        if self.info.get("director", "-") != "-" and not force:
            return
        cast_info = ApiController.get_cast_info(self.id)
        if not cast_info:
            print(f"Credits not found for {self.title}")
            return
        self._update_cast_dict(cast_info)

    def get_imdb_link(self, force=False):
        if self.imdb_id != "-" and not force:
            return
        if self.info.get("api", "-") != "-":
            if self.info["api"].get("imdb_id", "-") == "-":
                imdb_id = ApiController.get_imdb_id(self.id)
                self.info["api"]["imdb_id"] = imdb_id
                self.imdb_id = imdb_id

    def update_poster(self, force=False):
        if self._is_poster() and not force:
            return
        img = None
        if self.info.get("api", None) is not None:
            if self.info["api"].get("poster_path", None) is not None:
                img = ApiController.get_poster(self.info["api"]["poster_path"])
        if not img:
            print(f"Could't get poster for {self.title}")
            return
        poster_path = self._get_poster_path()
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        with open(poster_path, "wb") as f:
            f.write(img)

    def _update_api_dict(self, new_dict):
        self.id = new_dict["id"]
        self.info["api"] = {
            "id": self.id,
            "genre_ids": new_dict["genre_ids"],
            "poster_path": new_dict["poster_path"],
        }

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
