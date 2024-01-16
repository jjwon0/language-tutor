from inspect import getframeinfo, stack


_DEBUG = False


def set_debug(debug: bool):
    global _DEBUG
    _DEBUG = debug


def dprint(*args, **kwargs):
    caller = getframeinfo(stack()[1][0])
    callinfo = "%s:%d" % (caller.filename, caller.lineno)
    if _DEBUG:
        print(f"DEBUG({callinfo}):", *args, **kwargs)
