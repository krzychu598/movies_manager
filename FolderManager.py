import os, re, json, cv2, random, requests
from enum import Enum


class Tag(Enum):
    TITLE = "title"
    YEAR = "year"
    RESOLUTION = "resolution"
    PATH = "path"
    DIRECTOR = "director"
    ACTORS = "actors"
    ACTRESSES = "actresses"


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


class FolderManager:
    def __init__(self, path="D:\\movies"):
        self.path = path
        self.movies: dict[str, Movie] = {}  # title : movie_object
        self.create_movies()
        self.initialize_api()

    def initialize_api(self):
        try:
            with open("api_key.txt", "r") as f:
                self.api_key = f.readline()
        except:
            print("No api key found!")
        self.url_base = "https://api.themoviedb.org/3/"

    def get_movies(self):
        return list(self.movies.values())

    def get_keys(self):
        return list(list(self.movies.values())[0].displayable_info().keys())

    def apply_filter(self, filter_type, filter_method, filter_value):
        filtered_movies = []
        for item in self.movies.values():
            if filter_type in item.info:
                item_value = item.info[filter_type]

                try:
                    if isinstance(item_value, (int, float)):
                        filter_value_converted = int(filter_value)
                    else:
                        filter_value_converted = filter_value
                except ValueError:
                    item_value = str(item_value)
                    filter_value_converted = filter_value

                if filter_method == "equals":
                    if str(item_value) == str(filter_value_converted):
                        filtered_movies.append(item)
                elif filter_method == "greater than":
                    if (
                        isinstance(item_value, (int, float))
                        and item_value > filter_value_converted
                    ):
                        filtered_movies.append(item)
                elif filter_method == "less than":
                    if (
                        isinstance(item_value, (int, float))
                        and item_value < filter_value_converted
                    ):
                        filtered_movies.append(item)
                elif filter_method == "contains":
                    if str(filter_value_converted).lower() in str(item_value).lower():
                        filtered_movies.append(item)
        return filtered_movies

    def create_movies(self):
        for folder_name in os.listdir(self.path):
            file_info_path = os.path.join(self.path, folder_name, "tags.json")
            try:
                info = self._get_info_from_file(file_info_path)
                self.movies[info["title"]] = Movie(info)
            except:
                info = self._get_info_from_name(folder_name)
                info["path"] = os.path.join(self.path, folder_name)
                self.movies[info["title"]] = Movie(info)
                self.movies[info["title"]]._save_info_to_file()

    def reset_movie_info(self):
        self.movies: dict[str, Movie] = {}
        for folder_name in os.listdir(self.path):
            info = self._get_info_from_name(folder_name)
            info["path"] = os.path.join(self.path, folder_name)
            self.movies[info["title"]] = Movie(info)
            self.movies[info["title"]]._save_info_to_file()

    def update_movie_info(self, force=False):
        for movie in self.movies.values():
            movie.update_movie_info(self.url_base, self.api_key, force=force)
            movie.update_poster(self.api_key)
            movie.update_cast_info(self.api_key, force=force)

    def rename(self):
        pass

    def _get_info_from_file(self, path) -> dict:
        with open(path) as f:
            return json.load(f)

    def _get_info_from_name(self, file_name) -> dict:
        year_match = re.search(r"(?:^|\D)(19\d{2}|20\d{2})(?:\D|$)", file_name)
        if year_match:
            year = int(year_match.group(1))
        else:
            year = "unknown"
        parts = re.split(r" \(|\.|\[", file_name)
        title = parts[0]
        res = re.search(r"\[(.*?)\]", file_name)
        if res:
            res = res.group(1)
        else:
            res = "-"
        info = {"title": title, "year": year, "resolution": res}
        return info

    def remove_images(self):
        for folder in os.listdir(self.path):
            images = []
            images_folder = os.path.join(self.path, folder, "images")
            for image in os.listdir(images_folder):
                images.append(os.path.join(images_folder, image))
            for img in images:
                os.remove(img)

    def save_images(self):
        num_frames = 5

        for movie_folder in os.listdir(self.path):
            movie_folder_path = os.path.join(self.path, movie_folder)
            movie_folder_list = os.listdir(movie_folder_path)
            for file in movie_folder_list:
                if file.endswith((".mp4", ".avi", ".mkv")):
                    video_path = os.path.join(movie_folder_path, file)
                    images_folder = os.path.join(movie_folder_path, "images")
                    os.makedirs(images_folder, exist_ok=True)
                    cap = cv2.VideoCapture(str(video_path))

                    if not cap.isOpened():
                        print(f"Failed to open {file}")
                        continue

                    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    if frame_count > 10000:
                        selected_frames = random.sample(
                            range(1000, frame_count - 1000), num_frames
                        )
                    else:
                        selected_frames = random.sample(
                            range(frame_count), min(num_frames, frame_count)
                        )
                    selected_frames = sorted(selected_frames)
                    base_name = movie_folder.split(" (")[0]

                    for i, frame_num in enumerate(selected_frames):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                        ret, frame = cap.read()
                        if ret:
                            frame_name = f"{base_name}_frame{i}.jpg"
                            print(frame_name)

                            cv2.imwrite(os.path.join(images_folder, frame_name), frame)

                    cap.release()


if __name__ == "__main__":
    fm = FolderManager()
    fm.update_movie_info(force=True)
