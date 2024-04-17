from inspect import getframeinfo, stack

from tutor.cli_global_state import get_debug


def dprint(*args, **kwargs):
    caller = getframeinfo(stack()[1][0])
    callinfo = "%s:%d" % (caller.filename, caller.lineno)
    if get_debug():
        print(f"DEBUG({callinfo}):", *args, **kwargs)
