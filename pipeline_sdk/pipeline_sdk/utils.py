from .proxies.primitives import ServiceSpecs


def compose_url(service_specs: ServiceSpecs,
                path_postfix: str) -> str:
    relative_resource_url = compose_relative_resource_url(
        service_name=service_specs.service_name,
        service_version=service_specs.version,
        path_postfix=path_postfix
    )
    return f"{service_specs.host}:{service_specs.port}{relative_resource_url}"


def compose_relative_resource_url(service_name: str,
                                  service_version: str,
                                  path_postfix: str
                                  ) -> str:
    if path_postfix.startswith('/'):
        path_postfix = path_postfix.lstrip('/')
    return f"/{service_version}/{service_name}/{path_postfix}"
