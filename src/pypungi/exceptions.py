import yum

class PungiError(yum.Errors.MiscError):
    pass

class MissingPackageError(PungiError):
    pass