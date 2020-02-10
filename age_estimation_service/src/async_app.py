import io
import json
import logging
import random
from time import sleep
from typing import List, Dict, Tuple

import cv2
import pika
import numpy as np
import requests
from flask import Response

from .config import SERVICE_NAME, SERVICE_SECRET, SERVER_IDENTITY_URL, \
    DISCOVERY_URL
from .async_config import AGE_ESTIMATION_CHANNEL


INTER_SERVICES_TOKEN = None
CHANNEL = None
BASE_RESOURCES_URL = None


def create_app() -> None:
    global INTER_SERVICES_TOKEN
    _, INTER_SERVICES_TOKEN = _fetch_config_from_identity_service()
    services_info = _fetch_services_info(
        services=['message_broker', 'resource_manager_service']
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=services_info['message_broker']['service_address'],
            port=services_info['message_broker']['service_port']
        )
    )
    global BASE_RESOURCES_URL
    BASE_RESOURCES_URL = \
        f"{services_info['resource_manager_service']['service_address']}:" \
        f"{services_info['resource_manager_service']['service_port']}"
    global CHANNEL
    CHANNEL = connection.channel()
    CHANNEL.queue_declare(queue=AGE_ESTIMATION_CHANNEL)
    CHANNEL.basic_consume(
        queue=AGE_ESTIMATION_CHANNEL,
        on_message_callback=async_callback
    )
    CHANNEL.start_consuming()


def _fetch_config_from_identity_service() -> Tuple[str, str]:
    payload = {'service_name': SERVICE_NAME, 'password': SERVICE_SECRET}
    response = requests.post(
        SERVER_IDENTITY_URL, json=payload, verify=False
    )
    if response.status_code == 200:
        logging.info('Obtained access token and token secret.')
        content = response.json()
        return content['token_secret'], content['service_access_token']
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_config_from_identity_service()


def _fetch_services_info(services: List[str]) -> Dict[str, dict]:
    response = _call_discovery_resource(services)
    if response.status_code == 200:
        response_content = response.json()
        return _fetch_services_info_from_response(
            content=response_content
        )
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_services_info(services)


def _call_discovery_resource(services: List[str]) -> Response:
    headers = {'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'}
    payload = {'service_names': services}
    return requests.post(
        DISCOVERY_URL, headers=headers, json=payload, verify=False
    )


def _fetch_services_info_from_response(content: dict) -> Dict[str, dict]:
    services_found = content.get('services_found', [])
    return dict(map(lambda s: (s['service_name'], s), services_found))


def _fetch_port() -> int:
    response = _call_discovery_resource(services=[SERVICE_NAME])
    if response.status_code == 200:
        response_content = response.json()
        return _fetch_port_from_response(content=response_content)
    else:
        content = response.json()
        logging.error(content)
        sleep(5)
        return _fetch_port()


def _fetch_port_from_response(content: dict) -> int:
    services_found = content.get('services_found', [])
    services_matching = list(filter(
        lambda srv_desc: srv_desc['service_name'] == SERVICE_NAME,
        services_found
    ))
    if len(services_matching) != 1:
        raise RuntimeError('Cannot get proper response from discovery service.')
    return services_matching[0]['service_port']


def async_callback(ch, method, properties, body) -> None:
    message_content = json.loads(body)
    print(f"Handling message: {message_content}")
    try:
        image = _fetch_processing_input(
            requester_login=message_content["requester_login"],
            request_identifier=message_content["request_identifier"]
        )
        print(f"Fetched image: {image.shape}")
        faces = _fetch_face_detection(
            requester_login=message_content["requester_login"],
            request_identifier=message_content["request_identifier"]
        )
        age_estimation = list(map(
            lambda bbox: {'bounding_box': bbox, 'age': random.randint(4, 99)},
            faces
        ))
        result = {'age_estimation': age_estimation}
        _send_back_processing_results(
            requester_login=message_content["requester_login"],
            request_identifier=message_content["request_identifier"],
            resource_type="age_estimation",
            resource_content=result
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logging.error(e)
        _signal_processing_error(
            requester_login=message_content["requester_login"],
            request_identifier=message_content["request_identifier"]
        )


def _fetch_processing_input(requester_login: str,
                            request_identifier: str
                            ) -> np.ndarray:
    headers = {
        'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'
    }
    payload = {
        'requester_login': requester_login,
        'resource_identifier': request_identifier
    }
    url = f'{BASE_RESOURCES_URL}' \
        f'/v1/resource_manager_service/fetch_input_image'
    response = requests.get(
        url, data=payload, headers=headers, verify=False
    )
    if response.status_code != 200:
        raise RuntimeError("Could not process request")
    data = np.fromstring(response.content, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def _fetch_face_detection(requester_login: str,
                          request_identifier: str
                          ) -> list:
    headers = {
        'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'
    }
    payload = {
        'requester_login': requester_login,
        'resource_identifier': request_identifier,
        'resources_types': ['faces_detection']
    }
    url = f'{BASE_RESOURCES_URL}' \
        f'/v1/resource_manager_service/fetch_intermediate_results'
    response = requests.get(
        url, data=payload, headers=headers, verify=False
    )
    if response.status_code != 200:
        raise RuntimeError("Could not process request")
    response_content = response.json()
    return response_content['faces_detection']['faces']


def _signal_processing_error(requester_login: str,
                             request_identifier: str):
    try:
        _send_back_processing_results(
            requester_login=requester_login,
            request_identifier=request_identifier,
            resource_type="error",
            resource_content={
                "error_message": "Issue in age estimation service."
            }
        )
    except Exception:
        logging.error("Error while handling internal processing exception.")


def _send_back_processing_results(requester_login: str,
                                  request_identifier: str,
                                  resource_type: str,
                                  resource_content: dict
                                  ) -> None:
    headers = {
        'Authorization': f'Bearer {INTER_SERVICES_TOKEN}'
    }
    payload = {
        'requester_login': requester_login,
        'resource_identifier': request_identifier,
        'result_type': resource_type
    }
    url = f'{BASE_RESOURCES_URL}' \
        f'/v1/resource_manager_service/register_intermediate_result'
    resource_content = json.dumps(resource_content)
    files = {"resource_content": resource_content}
    response = requests.post(
        url, files=files, data=payload, headers=headers, verify=False
    )
    if response.status_code != 200:
        raise RuntimeError("Could not send back results.")


if __name__ == '__main__':
    create_app()
