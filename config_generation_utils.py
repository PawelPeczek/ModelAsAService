import json
import os
from typing import Union, List


def dump_json_file(path: str,
                   content: Union[list, dict]
                   ) -> None:
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with open(path, mode="w") as f:
        json.dump(obj=content, fp=f, indent=4)


def fetch_from_env(to_fetch: List[tuple]) -> List[tuple]:
    return [
        tuple(os.environ[env_name] for env_name in elements_to_fetch)
        for elements_to_fetch in to_fetch
    ]
