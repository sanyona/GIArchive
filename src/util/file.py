

import json
from pathlib import Path


def dump_to_json(obj, output_path: str|Path)-> None:
    """Dump an object to json, with sorted keys

    :param obj: _description_
    :param output_path: _description_
    """
        
    with open(output_path, "w") as fp:
        json.dump(obj, fp, indent=4, sort_keys=True)