import os, re, json, cv2, random
from enum import Enum
from MovieInfo import Movie


class Tag(Enum):
    TITLE = "title"
    YEAR = "year"
    RESOLUTION = "resolution"
    PATH = "path"
    DIRECTOR = "director"
    ACTORS = "actors"
    ACTRESSES = "actresses"


class FolderManager:
    def __init__(self):
        pass

    def initialize(self, dir=None):
        if not dir:
            with open("init.json", "r") as f:
                self.info = json.load(f)
                self.path = self.info["dir"]
        else:
            with open("init.json", "w") as f:
                json.dump({"dir": dir}, f)
                self.path = dir
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

    def initialize_json(self):
        pass

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
    fm.update_movie_info(force=False)
