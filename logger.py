from datetime import datetime

import pusher


def log_info(*args):
    print(datetime.now().isoformat() + ":", *args)


def log_error(*args):
    print(datetime.now().isoformat() + ":[ERROR]", *args)
    pusher.new_push(
        datetime.now().isoformat() + ": " + " ".join(str(arg) for arg in args)
    )
