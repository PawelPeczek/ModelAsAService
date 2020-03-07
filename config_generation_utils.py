import json
import os
from typing import Union


def dump_json_file(path: str,
                   content: Union[list, dict]
                   ) -> None:
    dir_path = os.path.dirname(path)
    os.makedirs(dir_path, exist_ok=True)
    with open(path, mode="w") as f:
        json.dump(obj=content, fp=f, indent=4)
