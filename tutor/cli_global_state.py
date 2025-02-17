from typing import Dict, Any

__GLOBAL_STATE: Dict[str, Any] = {}
__MODEL: str = "__MODEL"
__DEBUG: str = "__DEBUG"
__SKIP_CONFIRM: str = "__SKIP_CONFIRM"


def set_model(model: str) -> None:
    __GLOBAL_STATE[__MODEL] = model


def get_model() -> str:
    return __GLOBAL_STATE[__MODEL]


def set_debug(debug: bool) -> None:
    __GLOBAL_STATE[__DEBUG] = debug


def get_debug() -> bool:
    return __GLOBAL_STATE.get(__DEBUG, False)


def set_skip_confirm(skip: bool) -> None:
    __GLOBAL_STATE[__SKIP_CONFIRM] = skip


def get_skip_confirm() -> bool:
    return __GLOBAL_STATE.get(__SKIP_CONFIRM, False)
