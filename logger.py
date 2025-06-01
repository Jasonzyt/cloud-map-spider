from datetime import datetime

import push


def log_info(*args):
    print(datetime.now().isoformat() + ":", *args)


def log_error(*args):
    print(datetime.now().isoformat() + ":[ERROR]", *args)
    push.new_push(
        datetime.now().isoformat() + ": " + " ".join(str(arg) for arg in args)
    )
