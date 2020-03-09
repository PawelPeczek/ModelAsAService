from .proxies.primitives import ServiceSpecs


def compose_url(service_specs: ServiceSpecs, path_postfix: str) -> str:
    if path_postfix.startswith('/'):
        path_postfix = path_postfix.lstrip(chars='/')
    return f"{service_specs.host}:{service_specs.port}/" \
        f"{service_specs.service_name}/{path_postfix}"
