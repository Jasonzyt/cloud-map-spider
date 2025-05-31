from datetime import datetime


def log_info(*args):
    print(datetime.now().isoformat() + ":", *args)


def log_error(*args):
    print(datetime.now().isoformat() + ":[ERROR]", *args)
