import io
import json
import os
from datetime import datetime
from functools import reduce, partial
from glob import glob
from typing import List, Union, Dict, Optional, Tuple
from uuid import uuid4

import numpy as np
import cv2
from flask import Response, request, make_response, send_from_directory
from flask_restful import Resource, reqparse

from resources_manager_service.src.config import PERSISTENCE_DIR, \
    INPUT_IMAGE_NAME, DATE_TIME_FORMAT

RawResourceDescription = Tuple[str, List[str]]
ResourceDescription = Dict[str, Union[str, List[str]]]
ResourcesDescription = List[ResourceDescription]


def persist_json_result(target_path: str, content: dict) -> None:
    with open(target_path, "w") as f:
        json.dump(f, content)


def safe_load_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return None


class InputRegistrationResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    def post(self) -> Response:
        if 'image' not in request.files:
            return make_response(
                {'msg': 'Field called "image" must be specified'}, 500
            )
        data = self.__parser.parse_args()
        requester_login = data['login']
        resource_identifier = f'{uuid4()}'
        target_path = os.path.join(
            PERSISTENCE_DIR,
            resource_identifier,
            requester_login,
            INPUT_IMAGE_NAME
        )
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        input_image = self.__decode_input_image()
        cv2.imwrite(target_path, input_image)
        return make_response(
            {
                "requester_login": requester_login,
                "request_identifier": resource_identifier
            },
            200
        )

    def __decode_input_image(self) -> np.ndarray:
        in_memory_file = io.BytesIO()
        request.files['image'].save(in_memory_file)
        data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'login',
            help='Field "login" must be specified in this request.',
            required=True
        )
        return parser


class IntermediateResultRegistrationResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    def post(self) -> Response:
        if 'result_content' not in request.files:
            return make_response(
                {'msg': 'Field called "result_content" must be specified'}, 500
            )
        data = self.__parser.parse_args()
        requester_login = data['requester_login']
        resource_identifier = data['resource_identifier']
        result_type = data['result_type']
        target_path = os.path.join(
            PERSISTENCE_DIR,
            resource_identifier,
            requester_login,
            f'{result_type}.json'
        )
        if not os.path.isdir(os.path.dirname(target_path)):
            return make_response(
                {'msg': 'Wrong resource identifier or requester login'}, 500
            )
        content = json.load(request.files['people'])
        persist_json_result(target_path=target_path, content=content)
        return make_response({"msg": "OK"}, 200)

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'requester_login',
            help='Field "requester_login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'resource_identifier',
            help='Field "resource_identifier" must '
                 'be specified in this request.',
            required=True
        )
        parser.add_argument(
            'result_type',
            help='Field "result_type" must be specified in this request.',
            required=True
        )
        return parser


class IntermediateResultFetchingResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    def get(self) -> Response:
        data = self.__parser.parse_args()
        requester_login = data['requester_login']
        resource_identifier = data['resource_identifier']
        resources_dir = os.path.join(
            PERSISTENCE_DIR, resource_identifier, requester_login
        )
        if not os.path.isdir(resources_dir):
            return make_response(
                {'msg': 'Incorrect resource identifiers.'}, 500
            )
        resources = self.__load_resources(
            resources_types=data['resources_types'],
            resources_dir=resources_dir
        )
        return make_response(resources, 200)

    def __load_resources(self,
                         resources_types: Union[str, List[str]],
                         resources_dir: str
                         ) -> Dict[str, Union[None, dict, np.ndarray]]:
        if type(resources_types) is str:
            resources_types = [resources_types]
        result = {}
        for resource_type in resources_types:
            resource_content = safe_load_json(
                os.path.join(resources_dir, f'{resource_type}.json')
            )
            result[resource_type] = resource_content
        return result

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'requester_login',
            help='Field "requester_login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'resource_identifier',
            help='Field "resource_identifier" must '
                 'be specified in this request.',
            required=True
        )
        parser.add_argument(
            'resources_types',
            help='Field "resources_types" must be specified in this request.',
            required=True,
            action='append'
        )
        return parser


class InputFetchingResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    def get(self) -> Response:
        data = self.__parser.parse_args()
        requester_login = data['requester_login']
        resource_identifier = data['resource_identifier']
        resources_dir = os.path.join(
            PERSISTENCE_DIR, resource_identifier, requester_login
        )
        if not os.path.isdir(resources_dir):
            return make_response(
                {'msg': 'Incorrect resource identifiers.'}, 500
            )
        try:
            return send_from_directory(
                directory=resources_dir,
                filename=INPUT_IMAGE_NAME,
                as_attachment=True
            )
        except FileNotFoundError:
            return make_response(
                {'msg': 'There is no input file detected.'}, 500
            )

    def __load_resources(self,
                         resources_types: Union[str, List[str]],
                         resources_dir: str
                         ) -> Dict[str, Union[None, dict, np.ndarray]]:
        if type(resources_types) is str:
            resources_types = [resources_types]
        result = {}
        for resource_type in resources_types:
            resource_content = safe_load_json(
                os.path.join(resources_dir, f'{resource_type}.json')
            )
            result[resource_type] = resource_content
        return result

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'requester_login',
            help='Field "requester_login" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'resource_identifier',
            help='Field "resource_identifier" must '
                 'be specified in this request.',
            required=True
        )
        return parser


class BatchFetchingResource(Resource):

    def __init__(self):
        self.__parser = self.__initialize_request_parser()

    def get(self) -> Response:
        data = self.__parser.parse_args()
        range_start = datetime.strptime(data['range_start'], DATE_TIME_FORMAT)
        if 'range_end' in data:
            range_end = datetime.strptime(data['range_end'], DATE_TIME_FORMAT)
        else:
            range_end = datetime.now()
        resources_description = self.__get_resources_description_from_range(
            range_start=range_start,
            range_end=range_end
        )
        return make_response(resources_description, 200)

    def __get_resources_description_from_range(self,
                                               range_start: datetime,
                                               range_end: datetime
                                               ) -> ResourcesDescription:
        subdir_content = self.__flatten_subdir_content(
            start_dir=PERSISTENCE_DIR,
            level=2
        )
        grouped_subdir_content = self.__group_files_by_directory(
            to_be_grouped=subdir_content
        )
        directory_in_range = partial(
            self.__is_directory_in_range,
            range_start=range_start,
            range_end=range_end
        )
        filtered_directories = [
            d for d in grouped_subdir_content if directory_in_range(d)
        ]
        filtered_resources = {
            d: grouped_subdir_content[d] for d in filtered_directories
        }
        return self.__produce_resources_description(
            resources=filtered_resources
        )

    def __flatten_subdir_content(self,
                                 start_dir: str,
                                 level: int,
                                 files_only: bool = True
                                 ) -> List[str]:
        path_wild_card = start_dir
        for _ in range(level + 1):
            path_wild_card = os.path.join(
                path_wild_card, "*"
            )
        content = glob(path_wild_card)
        if files_only:
            content = list(filter(os.path.isfile, content))
        return content

    def __group_files_by_directory(self,
                                   to_be_grouped: List[str]
                                   ) -> Dict[str, List[str]]:
        to_be_grouped = list(map(os.path.split, to_be_grouped))
        return reduce(
            self.__collect_files_by_directory, to_be_grouped, {}
        )

    def __collect_files_by_directory(self,
                                     already_collected: Dict[str, List[str]],
                                     to_be_collected: Tuple[str, str]
                                     ) -> Dict[str, List[str]]:
        dir_name, file_name = to_be_collected
        if dir_name in already_collected:
            already_collected[dir_name].append(file_name)
        else:
            already_collected[dir_name] = [file_name]
        return already_collected

    def __is_directory_in_range(self,
                                dir_path: str,
                                range_start: datetime,
                                range_end: datetime
                                ) -> bool:
        dir_modification_time = self.__get_modification_modification_time(
            path=dir_path
        )
        return range_start < dir_modification_time < range_end

    def __get_modification_modification_time(self, path: str) -> datetime:
        unix_time = os.path.getmtime(path)
        return datetime.strptime(unix_time, "%a %b %d %H:%M:%S %Y")

    def __produce_resources_description(self,
                                        resources: Dict[str, List[str]]
                                        ) -> ResourcesDescription:
        flatten_resources = [(d, fs) for d, fs in resources.items()]
        return list(map(self.__create_resource_description, flatten_resources))

    def __create_resource_description(self,
                                      raw_description: RawResourceDescription
                                      ) -> ResourceDescription:
        dir_name, directory_files = raw_description
        parent_dir_name, requester_login = os.path.split(dir_name)
        resource_identifier = os.path.basename(parent_dir_name)
        return {
            "requester_login": requester_login,
            "resource_identifier": resource_identifier,
            "resources": directory_files
        }

    def __initialize_request_parser(self) -> reqparse.RequestParser:
        parser = reqparse.RequestParser()
        parser.add_argument(
            'range_start',
            help='Field "range_start" must be specified in this request.',
            required=True
        )
        parser.add_argument(
            'range_end',
            help='Field "range_end" is optional.',
            required=False
        )
        return parser
