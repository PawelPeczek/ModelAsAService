class PipelineSDKError(Exception):
    pass


class ServiceSpecsNotProvided(PipelineSDKError):
    pass


class RequestProcessingError(PipelineSDKError):
    pass


class IdentityVerificationFailed(RequestProcessingError):
    pass

