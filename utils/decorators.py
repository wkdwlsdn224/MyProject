import functools
from .notifier import send_telegram
from .logger import log_event

def exception_notifier(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            msg = f"❗ 예외 발생 in {func.__name__}: {e}"
            send_telegram(msg)
            log_event(msg, level="ERROR")
            raise
    return wrapper
