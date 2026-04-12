# Ошибки валидации HttpProfile и резерв под строгий реестр.


class HttpProfileError(ValueError):
    pass


class ProfileRegistryError(ValueError):
    pass
