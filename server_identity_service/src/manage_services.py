import logging

from werkzeug.security import generate_password_hash

from .app import app
from .model import Service, persist_model_instance, remove_from_db

logging.getLogger().setLevel(logging.INFO)


def manage_services_interactively() -> None:
    app.app_context().push()
    _print_help()
    user_input = ''
    while user_input.lower() != 'q':
        user_input = _get_user_info(description='Type command')
        _handle_user_input(user_input=user_input)


def _print_help():
    print(
        '''Tool to manage services database.
        q - quit
        a - add service
        d - delete service
        l - list all services
        '''
    )


def _get_user_info(description: str) -> str:
    print(description)
    return input()


def _handle_user_input(user_input: str) -> None:
    user_input = user_input.lower()
    if user_input == 'a':
        _add_service()
    elif user_input == 'd':
        _delete_service()
    elif user_input == 'l':
        _list_services()
    elif user_input != 'q':
        logging.warning(f'Wrong command.')


def _add_service() -> None:
    service_name = _get_user_info(description='Type service name')
    service_password = _get_user_info(description='Type service password')
    new_service = Service(service_name=service_name)
    print(f'serv passwd: {service_password} {len(service_password)}')
    print(generate_password_hash(password=service_password))
    new_service.set_password(password=service_password)
    persist_model_instance(instance=new_service)


def _delete_service() -> None:
    service_name = _get_user_info(description='Type service name')
    service = Service.find_by_name(service_name=service_name)
    if service is None:
        logging.warning(f'Service {service_name} does not exists.')
    else:
        remove_from_db(instance=service)


def _list_services() -> None:
    all_services = Service.get_all()
    for service in all_services:
        print(service.service_name)


if __name__ == '__main__':
    manage_services_interactively()
