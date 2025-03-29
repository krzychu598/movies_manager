import os, re, json, cv2, random, shutil
from enum import Enum
from MovieInfo import Movie
from pathlib import Path


class Tag(Enum):
    TITLE = "title"
    YEAR = "year"
    RESOLUTION = "resolution"
    PATH = "path"
    DIRECTOR = "director"
    ACTORS = "actors"
    ACTRESSES = "actresses"


class NoInitException(Exception):
    pass


class FolderManager:
    def __init__(self):
        pass

    def initialize(self, dir=None):
        if not dir:
            try:
                self.init_info = self._get_info_from_file("init.json")
            except:
                raise NoInitException("No init file")
            self.path = self.init_info["dir"]
        else:
            self._write_to_file("init.json", {"dir": dir})
            self.init_info = {"dir": dir}
            self.path = dir
        self.movies: dict[str, Movie] = {}  # title : movie_object
        self.create_movies()
        self.save_new_info(dir)

    def save_new_info(self, dir):
        new_movies_info = [movie.info for movie in self.movies.values()]
        new_info = {"dir": dir, "movies": new_movies_info}
        self._write_to_file("init.json", new_info)

    def initialize_json(self):
        pass

    def set_path(self, path):
        self.path = path

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
        init_movies_info = self.init_info.get("movies", [{}])
        init_movies_titles = [a.get("title", None) for a in init_movies_info]
        for folder_name in os.listdir(self.path):
            if folder_name in init_movies_titles:
                self.movies[folder_name] = Movie(init_movies_info[folder_name])
            else:
                folder_name = self._process_movie(folder_name)
                info = self._get_info_from_name(folder_name)
                new_folder_name = f"{info["title"]} ({info["year"]})"
                if new_folder_name != folder_name:
                    os.rename(
                        os.path.join(self.path, folder_name),
                        os.path.join(self.path, new_folder_name),
                    )
                info["path"] = os.path.join(self.path, folder_name)
                self.movies[new_folder_name] = Movie(info)

        self.update_movie_info()

    def _process_movie(self, ent_name):
        ent_path = os.path.join(self.path, ent_name)
        if os.path.isfile(ent_path):
            return self._move_to_folder(ent_name)
        return ent_name

    def _move_to_folder(self, ent_name):
        ent_path = os.path.join(self.path, ent_name)
        new_folder_path = os.path.splitext(ent_path)[0]
        new_movie_path = os.path.join(new_folder_path, ent_name)
        os.makedirs(new_folder_path)
        shutil.move(ent_path, new_movie_path)
        return Path(new_folder_path).name

    def reset_movie_info(self):
        self.movies: dict[str, Movie] = {}
        for folder_name in os.listdir(self.path):
            info = self._get_info_from_name(folder_name)
            info["path"] = os.path.join(self.path, folder_name)
            self.movies[info["title"]] = Movie(info)
            self.movies[info["title"]]._save_info_to_file()

    def update_movie_info(self, force=False):
        for movie in self.movies.values():
            movie.update_movie(force=force)

    def rename(self):
        pass

    def _get_info_from_file(self, path) -> dict:
        with open(path) as f:
            return json.load(f)

    def _write_to_file(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f)

    def _get_info_from_name(self, file_name) -> dict:
        year_match = re.search(r"(?:^|\D)(19\d{2}|20\d{2})(?:\D|$)", file_name)
        if year_match:
            year = int(year_match.group(1))
        else:
            year = "unknown"
        parts = re.split(r" \(|\.|\[", file_name)
        match = re.search(r"^(.*?)[ ]*(?=\d{4})", file_name)
        if match:
            parts2 = match.group(1)
        else:
            parts2 = file_name
        if len(parts[0]) < len(parts2):
            title = parts[0]
        else:
            title = parts2
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
    fm.update_movie_info(force=False)
