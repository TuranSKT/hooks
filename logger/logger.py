class Singleton(object):
    """
    Singleton

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class Logger(Singleton):
    """
    Log

    """

    def __init__(self, file_name):
        self.filename = file_name
        self.path = "/var/log/cel-apus/" + self.filename

    def _write_log(self, level, msg):
        with open(self.path, "a") as log_file:
            log_file.write("[{0}]{1}\n".format(level, msg))

    def critical(self, msg):
        self._write_log("CRITICAL", msg)

    def error(self, msg):
        self._write_log("ERROR", msg)

    def warn(self, msg):
        self._write_log("WARN", msg)

    def info(self, msg):
        self._write_log("INFO", msg)

    def debug(self, msg):
        self._write_log("DEBUG", msg)
