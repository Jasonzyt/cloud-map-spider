import time
import config
import threading
from logger import log_error, log_info
from network import delay, delay_until, poll, process_queue


def load_config():
    with open("config.json", "r") as file:
        content = file.read()
        conf = config.Config.from_json(content)
        log_info("Configuration loaded successfully.")
        for target in conf.targets:
            log_info(target)
        return conf


def do_polling(target: config.Target, preset: config.Preset):
    log_info(f"Starting polling for target: {target.name} with preset: {preset.export}")
    while True:
        next_poll = time.time() + target.interval
        poll(target, preset)
        if time.time() < next_poll:
            log_info(f"Polling for {target} completed, waiting for next poll.")
            delay_until(next_poll)


def start_threads(conf: config.Config):
    threading.Thread(target=process_queue, daemon=True).start()
    log_info("Started thread for processing queue.")
    for target in conf.targets:
        log_info(f"Starting thread for target: {target.name}")
        threading.Thread(
            target=do_polling,
            args=(target, conf.get_preset(target.preset)),
            daemon=True,
        ).start()


def main():
    conf = None
    try:
        conf = load_config()
    except Exception as e:
        log_error("Failed to load configuration:", e)
    if conf is None:
        log_error("Exiting due to configuration load failure.")
        return
    start_threads(conf)
    log_info("All threads started, entering main loop.")
    while True:
        try:
            delay(1)  # Main loop delay
        except KeyboardInterrupt:
            log_info("Keyboard interrupt received, exiting.")
            break


if __name__ == "__main__":
    main()
