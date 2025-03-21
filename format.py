import os, re, json, cv2, random, locale
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
        # self.title = info["title"]
        # self.year = int(info["year"])
        # self.res = info["resolution"]
        self.path = info["path"]
        # self.director = info.get("director")
        self.info = info

    def add_tag(self, tag):
        self.info[tag[0]] = tag[1]

    def save_info_to_file(self):
        with open(os.path.join(self.path, "tags.json"), "w") as f:
            json.dump(self.info, f)


class FolderManager:
    def __init__(self, path="D:\\movies"):
        self.path = path
        self.movies = {}  # title : movie_object
        self.create_movies()

    def create_movies(self):
        for folder_name in os.listdir(self.path):
            file_info_path = os.path.join(self.path, folder_name, "tags.json")
            try:
                info = self._get_info_from_file(file_info_path)
                self.movies[info[0]] = Movie(info)
            except:
                title, year, res = self._get_info_from_name(folder_name)
                path = os.path.join(self.path, folder_name)
                info = {"title": title, "year": year, "resolution": res, "path": path}
                self.movies[info["title"]] = Movie(info)
                self.movies[info["title"]].save_info_to_file()

    def rename(self):
        pass

    def _get_info_from_file(self, path) -> str:
        with open(path) as f:
            return json.load(f)

    def _get_info_from_name(self, file_name) -> str:
        ret = []
        parts = re.split(r"[\(\)\[\]]", file_name)
        parts[0] = parts[0][:-1]
        for part in parts:
            if part and part != " ":
                ret.append(part)
        return ret

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

                    for i, frame_num in enumerate(selected_frames):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                        ret, frame = cap.read()
                        if ret:
                            frame_name = f"{movie_folder.split(' (')[0]}_frame{i}.jpg"
                            print(frame_name)

                            cv2.imwrite(os.path.join(images_folder, frame_name), frame)

                    cap.release()
