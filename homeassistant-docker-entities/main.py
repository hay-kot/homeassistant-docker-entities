import json
from requests import get
from tqdm import tqdm
import os
import configparser
from pathlib import Path
from glob import glob


class ReadContainer:
    def __init__(self, api_response):
        name = response[i]["Names"]
        name = name[0].replace("/", "")
        alias = name
        for overrides in config_list:
            if overrides == name:
                alias = config.get(overrides, "alias")
                print(f"Overriding... {overrides} with {alias}")
        self.alias = alias
        self.name = name


def pre_clean():
    yaml_dir_list = os.listdir("./Outputs/Yaml")
    json_dir = glob("./Outputs/Node-Red/*")
    for dir_1 in yaml_dir_list:
        yaml_dir = glob(f"./Outputs/Yaml/{dir_1}/*")
        for files in yaml_dir:
            if os.path.isfile(files):
                os.remove(files)
    for files in json_dir:
        if os.path.isfile(files):
            os.remove(files)


def find_replace_write(file, dest, container):
    with open(file, "r") as f:
        for lines in f:
            if "CONTAINER_NAME" in lines:
                lines = lines.replace("CONTAINER_NAME", container.name.capitalize())
            if "ALIAS" in lines:
                lines = lines.replace("ALIAS", container.alias)
            if "DOCKER_URL" in lines:
                lines = lines.replace("DOCKER_URL", url)
            with open(dest, "a") as f1:
                f1.write(lines)


def main(container):
    for files in glob("./Outputs/Templates/*"):
        template = Path(files)
        if "Node-Red" in files:
            flow_type, extension = os.path.splitext(os.path.basename(template))
            flow_type = flow_type.replace("Node-Red", "")
            dest = Path(
                f"./Outputs/Node-Red/{os.path.basename(container.name.capitalize())}_{flow_type}.json"
            )
        else:
            file_name, extension = os.path.splitext(os.path.basename(template))
            dest_individual = Path(
                f"./Outputs/Yaml/{os.path.basename(file_name)}/{container.name}.yaml"
            )
            dest_all = Path(f"./Outputs/Yaml/all/{os.path.basename(template)}")
        find_replace_write(template, dest_individual, container)
        find_replace_write(template, dest_all, container)


# Reading the Config
config = configparser.ConfigParser()
config.read("config.ini")
config_list = config.sections()

# Hit Docker API
url = config["settings"]["url"]
response = get(f"{url}/containers/json").json()
response = json.loads(json.dumps(response))

# Remove Old Data
pre_clean()

# Process Responses
i = 0
for containers in tqdm(response):
    active_container = ReadContainer(response)
    main(active_container)
    i += 1
