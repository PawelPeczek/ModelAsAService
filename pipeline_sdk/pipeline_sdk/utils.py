from .proxies.primitives import ServiceSpecs


def compose_url(service_specs: ServiceSpecs,
                path_postfix: str) -> str:
    relative_resource_url = compose_relative_resource_url(
        service_specs=service_specs,
        path_postfix=path_postfix
    )
    return f"{service_specs.host}:{service_specs.port}{relative_resource_url}"


def compose_relative_resource_url(service_specs: ServiceSpecs,
                                  path_postfix: str
                                  ) -> str:
    if path_postfix.startswith('/'):
        path_postfix = path_postfix.lstrip(chars='/')
    return f"/{service_specs.version}/{service_specs.service_name}/" \
        f"{path_postfix}"
