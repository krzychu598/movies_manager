import os, re, json


def get_info(old_name: str):
    ret = []
    parts = re.split(r"[\(\)\[\]]", old_name)
    for part in parts:
        if part and part != " ":
            ret.append(part)
    return ret


def create_tags(folder):
    for folder_name in os.listdir(folder):
        name, year, res = get_info(folder_name)
        file_path = os.path.join(folder, folder_name, "tags.json")
        try:
            with open(file_path) as f:
                info = json.load(f)
                print(info)
        except:
            info = {"name": name, "year": year, "resolution": res}
            with open(file_path, "w") as f:
                json.dump(info, f)
        # os.system(f'attrib +h "{file_path}"')  # Hide a file


create_tags("..\\..\\movies")
# TODO add images to app (screens from movies), add functionality of giving new tags
