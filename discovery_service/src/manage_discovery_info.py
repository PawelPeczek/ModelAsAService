import argparse
import json
import logging
from typing import List, Dict

from sqlalchemy.exc import SQLAlchemyError

from .app import app
from .model import ServiceLocation, persist_model_instance, remove_from_db, \
    commit_db_changes

logging.getLogger().setLevel(logging.INFO)


def manage_services_interactively() -> None:
    app.app_context().push()
    _print_help()
    user_input = ''
    while user_input.lower() != 'q':
        user_input = _get_user_info(description='Type command')
        _handle_user_input(user_input=user_input)


def manage_services_from_config(config: List[Dict[str, str]]) -> None:
    app.app_context().push()
    for service_description in config:
        _add_service_location(
            service_name=service_description['service_name'],
            service_host=service_description['service_host'],
            service_port=int(service_description['service_port'])
        )


def _print_help():
    print(
        '''Tool to manage services database.
        q - quit
        a - add service location
        d - delete service location
        l - list all services locations
        '''
    )


def _get_user_info(description: str) -> str:
    print(description)
    return input()


def _handle_user_input(user_input: str) -> None:
    user_input = user_input.lower()
    if user_input == 'a':
        _add_service_location_interactively()
    elif user_input == 'd':
        _delete_service_location()
    elif user_input == 'l':
        _list_services_locations()
    elif user_input != 'q':
        logging.warning(f'Wrong command.')


def _add_service_location_interactively() -> None:
    service_name = _get_user_info(description='Type service name')
    service_host = _get_user_info(description='Type service host')
    service_port = int(_get_user_info(description='Type service port'))
    _add_service_location(
        service_name=service_name,
        service_host=service_host,
        service_port=service_port
    )


def _add_service_location(service_name: str,
                          service_host: str,
                          service_port: int
                          ) -> None:
    service_location = ServiceLocation.find_by_name(service_name=service_name)
    try:
        if service_location is None:
            service_location = ServiceLocation(
                service_name=service_name,
                service_address=service_host,
                service_port=service_port
            )
            persist_model_instance(instance=service_location)
        else:
            service_location.service_address = service_host
            service_location.service_port = service_port
            commit_db_changes()
    except SQLAlchemyError as e:
        logging.error(f'Exception occurred: {e}')


def _delete_service_location() -> None:
    service_name = _get_user_info(description='Type service name')
    service_location = ServiceLocation.find_by_name(service_name=service_name)
    if service_location is None:
        logging.warning(f'Service {service_name} does not exists.')
    else:
        remove_from_db(instance=service_location)


def _list_services_locations() -> None:
    all_services = ServiceLocation.get_all()
    for service in all_services:
        print(
            f'{service.service_name} - '
            f'{service.service_address} - {service.service_port}'
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database management tool')
    parser.add_argument(
        '--config_path',
        type=str,
        help='Path to JSON config with database content.'
    )
    args = parser.parse_args()
    if args.config_path is None:
        manage_services_interactively()
    else:
        with open(args.config_path, "r") as f:
            config = json.load(fp=f)
            manage_services_from_config(config=config)
