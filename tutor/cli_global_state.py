__GLOBAL_STATE = {}
__MODEL = "__MODEL"
__DEBUG = "__DEBUG"
__SKIP_CONFIRM = "__SKIP_CONFIRM"


def set_model(model: str) -> None:
    __GLOBAL_STATE[__MODEL] = model


def get_model():
    return __GLOBAL_STATE[__MODEL]


def set_debug(debug: bool) -> None:
    __GLOBAL_STATE[__DEBUG] = debug


def get_debug():
    return __GLOBAL_STATE[__DEBUG]


def set_skip_confirm(skip_confirm: bool) -> None:
    __GLOBAL_STATE[__SKIP_CONFIRM] = skip_confirm


def get_skip_confirm():
    return __GLOBAL_STATE[__SKIP_CONFIRM]
