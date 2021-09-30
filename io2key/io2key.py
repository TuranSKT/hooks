import Jetson.GPIO as GPIO
import threading
import os, time, argparse, sys
import yaml
import subprocess
from dotenv import load_dotenv

load_dotenv()
log_path = os.getenv("LOG_PATH")
sys.path.append(log_path)
from logger import Logger  # noqa


class KeyStroke:
    def __init__(self, keystroke=None):
        """
        Throws a keystroke given a string in the input_keys config file.

        :param keystroke string: string that is the key to stroke <a> <F2>
        """
        self.keystroke = keystroke

    def keySimulator(self):
        """
        Keystroke simulation is done using xdotool library.
        There is some exemples in https://funprojects.blog/tag/xdotools/
        xdotool is orinally a bash command. Thus, subprocess is used to run the
        xdotool command through python.
        """

        if self.keystroke is not None:
            bash_command = f"xdotool key {self.keystroke}+Return"
            subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)  # noqa: E
            log.info(f"Keystroke.keySimulator: {self.keystroke} key has been stroken")
        else:
            log.error(
                "Keystroke.keySimulator: Keystroke variable is empty. Xdotool needs "
                / "a non-empty one."
            )


class GPIOThread(threading.Thread):
    def __init__(self, yaml_load=None):
        """
        Thread that extracts variables from a given yaml dict and maps the
        associated pin.

        :param yaml_load dict: Yaml dict loaded from YamlReader
        """

        threading.Thread.__init__(self)
        self.yaml_load = yaml_load
        GPIO.setmode(GPIO.BOARD)

        if self.yaml_load is not None:
            if len(self.yaml_load) != 0:
                try:
                    for pair, elem in self.yaml_load.items():
                        GPIO.setup(elem["input_pin"], GPIO.IN)
                    log.info("GPIOThread.__init__: Yaml file has been set properly")
                except Exception:
                    log.error("GPIOThread.__init__: Yaml file is not well configured")
            else:
                log.error(
                    "GPIOThread.__init__: Yaml file has been loaded but is empty "
                )
        else:
            log.error(
                "GPIOThread__init__: Cannot map GPIO input with an empty yaml file"
            )

    def run(self):
        """
        Reads the yaml dict and listens all pins writen inside and throws keystrokes
        linked to them.
        """
        boolean = True
        try:
            while boolean:
                time.sleep(0.1)
                for _, elem in self.yaml_load.items():
                    if GPIO.input(elem["input_pin"]):
                        keystroke = elem["keystroke"]
                        k = KeyStroke(keystroke)
                        k.keySimulator()
                        time.sleep(0.1)
                        log.info(
                            f"GPIOThread.run: Keystroke {keystroke} has been "
                            / "simulated"
                        )
        except Exception:
            log.error("GPIOThread.run: Yaml file hasn't been loaded properly")

        finally:
            GPIO.cleanup()


class YamlReader:
    def __init__(self, path=None):
        """
        Reads a yaml config file given a path and return a dictionnary.
        :param path string: path to the yaml config file
        """
        self.path = path

    def reader(self):
        if self.path is not None:
            try:
                with open(self.path) as file:
                    elements = yaml.full_load(file)
                    log.info("YamlReader.reader: path has been set properly")
                    return elements
            except Exception:
                log.error("YamlReader.reader: path is incorrect")
        else:
            log.error("YamlReader.reader: Cannot open an empty file")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="io2key")
    parser.add_argument(
        "-p",
        "--path",
        help="path of the input_key config file",
        default=os.getenv("IO_YAML_PATH"),
    )
    args = parser.parse_args()
    log = Logger("io2key.log")

    print(args.path)
    y = YamlReader(args.path)
    yaml_load = y.reader()

    t = GPIOThread(yaml_load)
    t.start()
