import Jetson.GPIO as GPIO
import os, time, argparse, sys
import json, yaml
from dotenv import load_dotenv

load_dotenv()
log_path = os.getenv("LOG_PATH")
sys.path.append(log_path)
from logger import Logger  # noqa


class GpioFunctions:
    def __init__(self):
        """
        This class contains functions that will be called when an event is detected
        There are some basic functions below that are all responsible of changing the
        state of a pin. LED is used here for test purpose. Any device that can be
        connected to a pin may have a function dedicated in this class.
        Thus, for future use functions may be changed/added/deleted.

        """
        self.output_pin = None

    def led_constant_on(self):
        """
        Turn on the LED

        """
        GPIO.output(self.output_pin, GPIO.HIGH)
        log.info(
            f"GpioFunctions.led_constant_on: pin {self.output_pin}"
            / "has been set to HIGH"
        )

    def led_constant_off(self):
        """
        Turn off the LED

        """
        GPIO.output(self.output_pin, GPIO.LOW)
        log.info(
            f"GpioFunctions.led_constant_off: pin {self.output_pin}"
            / "has been set to LOW"
        )

    def led_simple_blink(self, duration):
        """
        Turn on the LED temporary during <duration> seconds

        :param duration int: duration of the blink in seconds
        """
        GPIO.output(self.output_pin, GPIO.HIGH)
        time.sleep(duration)
        GPIO.output(self.output_pin, GPIO.LOW)
        log.info(
            "GpioFunctions.led_simple_blink: one blinked has been triggered"
            / f"in the pin {self.output_pin}"
        )

    def led_blink(self, mode, duration):
        """
        Blink the LED every 0.3s for slow <mode> or 0.1s for fast <mode>,
        both during <duration> seconds.

        :param duration int: duration of the blink in seconds
        """
        log.info(
            f"GpioFunctions.led_blink: {mode} has been triggered with pin"
            / "{self.output_pin}"
        )
        time_start = time.time()
        while time.time() < time_start + duration:
            GPIO.output(self.output_pin, GPIO.HIGH)
            time.sleep(0.3) if mode == "slow_blink" else time.sleep(0.1)
            GPIO.output(self.output_pin, GPIO.LOW)
            time.sleep(0.3) if mode == "slow_blink" else time.sleep(0.1)
        log.info(
            f"GpioFunctions.led_blink: a {duration} seconds blink has been triggered"
            / "in the pin {self.output_pin}"
        )

    def function_mapper(self, output_pin, event, mode, duration):
        """
        Given the variabes in the yaml file triggers one of the dedicated
        functions above

        :param output_pin int: output pin number on which a dedicated function
        will be triggered

        :param event string: type of event. For now this variable shouldn't
        matter that much as well as functions above are dedicated for LED.
        However in case of using different type of device like motors,
        changing 'event' may be useful to implement their own dedicated functions

        :param mode string: string that contain the name of the function to call

        :param duration int: duration of the blink in seconds
        """
        self.output_pin = output_pin
        # prevents led blinking forever
        if duration > 60:
            duration = 60

        if event == "LED":
            if mode == "constant_on":
                self.led_constant_on()
                log.info(f"GpioFunctions.function_mapper: {mode} has been triggered")

            elif mode == "constant_off":
                self.led_constant_off()
                log.info(f"GpioFunctions.function_mapper: {mode} has been triggered")

            elif mode == "simple_blink":
                self.led_simple_blink(duration)
                log.info(f"GpioFunctions.function_mapper: {mode} has been triggered")

            elif mode == "fast_blink":
                self.led_blink(mode, duration)
                log.info(f"GpioFunctions.function_mapper: {mode} has been triggered")

            elif mode == "slow_blink":
                self.led_blink(mode, duration)
                log.info(f"GpioFunctions.function_mapper: {mode} has been triggered")


class GpioInit:
    def __init__(self, path=None):
        """
        Initialises/maps gpio pins given a config file

        :param path string: config file path
        """
        GPIO.setmode(GPIO.BOARD)

        if path is None:
            log.error("GpioInit.__init__: config file path has not been provided")
        else:
            self.config_path = path
            log.info("GpioInit.__init__: config file path has been set properly")

    def yaml_reader(self):
        """
        Returns a yaml dictionnary given the config file path

        """
        try:
            with open(self.config_path) as file:
                yaml_dict = yaml.full_load(file)
                return yaml_dict
        except Exception:
            log.error(
                "GpioInit.yaml_reader: Config file hasn't been set properly"
                / "or does not exist"
            )

    def main(self):
        """
        Main loop in which all gpio pins are mapped given the config file

        """
        yaml_dict = self.yaml_reader()
        try:
            for _, elem in yaml_dict.items():
                output_pin = int(elem["output_pin"])
                GPIO.setup(output_pin, GPIO.OUT)
                # set default pin state to low to initiliase the pin.
                # LOW state meaning turn off
                GPIO.output(output_pin, GPIO.LOW)
        except KeyError:
            log.error("GpioInit.main: config file has an invalid key")
        except Exception:
            log.error("GpioInit.main: yaml file hasn't been loaded properly")


class Listener:
    def __init__(self, yaml_dict=None, path=None):
        """
        Listens a named pipe and checks if there is a trigger message that may trigger
        a pin-dependent function while checking the conditions in the config file

        :param yaml_dict dict: yaml dictionnary
        """
        self.gpio_functions = GpioFunctions()

        if path is None:
            log.error(
                "Listener.__init__: current hook directory hasn't been loaded properly"
            )
        else:
            self.path = path
            log.info(
                "Listener.__inti__: current hook directory has been loaded properly"
            )

        self.read_path = self.path + "pipe.in"
        self.write_path = self.path + "pipe.out"

        if yaml_dict is None:
            log.error("Listener.__init__: yaml_dict has not been provided")
        else:
            self.yaml_dict = yaml_dict
            log.info("Listener.__init__: yaml_dict has been loaded properly")

    def named_pipe_opener(self):
        """
        Initiliases a read and a write named pipe, opens them and returns the contents

        """
        if os.path.exists(self.read_path):
            os.remove(self.read_path)
        if os.path.exists(self.write_path):
            os.remove(self.write_path)
        try:
            os.mkfifo(self.write_path)
            os.mkfifo(self.read_path)
        except Exception:
            log.error("Listener.named_pipe_opener: pipes's path are incorrect")

        rf = os.open(self.read_path, os.O_RDONLY)
        wf = os.open(self.write_path, os.O_SYNC | os.O_CREAT | os.O_RDWR)

        return (rf, wf)

    def pipe_listener(self, readfile):
        """
        Reads a read-named pipe and returns the json string inside
        Since the message is a byte-like object and not a string, the decode() method
        is used to convert it to a string
        Json.loads is used to load the dictionnary that is inside the string

        :param readfile file_descriptor_obj: pipe that contains the message to listen
        """
        pipe = os.read(readfile, 4096)
        pipe = pipe.decode()
        return json.loads(pipe)

    def pipe_writer(self, writefile, message):
        """
        Updates the writer named pipe
        Since the message inside the pipe is a byte-like object,
        a conversion string to byte-like object is needed

        :param writefile file_descriptor_obj: pipe in which the message is written
        :param message string: message that come from an external pipe and that
        may trigger the pin_dependent function
        """
        os.write(writefile, str.encode(json.dumps(message)))

    def pipe_closer(self, readfile, writefile):
        """
        Closes properly both read and write named pipe

        :param readfile file_descriptor_obj: pipe in which the message is written
        :param writefile file_descriptor_obj: pip that contains the message to listen
        """
        os.close(readfile)
        os.close(writefile)

    def gpio_trigger(self, message):
        """
        Loops inside the yaml dictionnary and compares the message received from
        an external pipe to the message inside the dictionnary and calls the function
        mapper that will map a dedicated function given the external message

        :param message string: message that come from an external pipe and that may
        trigger the pin_dependent function
        """
        try:
            for _, elem in self.yaml_dict.items():
                output_pin = int(elem["output_pin"])
                event = str(elem["event"])
                mode = str(elem["mode"])
                trigger_msg = str(elem["trigger_msg"])
                duration = int(elem["duration"])
                if trigger_msg in message:
                    self.gpio_functions.function_mapper(
                        output_pin, event, mode, duration
                    )
        except Exception:
            log.error(
                "Listener.gpio_trigger: yaml dictionnary hasn't been loaded properly"
            )

    def main(self):
        """
        Main loop that opens named pipes and keeps listenig them.

        """
        rf, wf = self.named_pipe_opener()
        boolean = True
        exit_msg = "exit"

        while boolean:
            msg = self.pipe_listener(rf)
            payload = msg["payload"]
            message = payload["message"]

            log.info(f"Listener.main: received message is : {message}")

            if len(msg) == 0:
                time.sleep(1)
                continue

            self.gpio_trigger(message)

            # if an exit_msg is sent from the external pipe break the loop
            if exit_msg in message:
                log.info("Listener.main: <exit> has been sent. Closing pipe ...")
                break

            self.pipe_writer(wf, msg)
        self.pipe_closer(rf, wf)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="event2io")
    parser.add_argument(
        "-p",
        "--path",
        help="path of the output_key config file",
        default=os.getenv("EV_YAML_PATH"),
    )
    parser.add_argument(
        "-p2",
        "--current_path",
        help="current path of this hook. Needed for the pipes path",
        default=os.getenv("EV_PATH"),
    )
    args = parser.parse_args()

    # instanciate the logger
    log = Logger("logs-event2io.log")

    gpio = GpioInit(args.path)
    gpio.main()

    yaml_dictionnary = gpio.yaml_reader()

    listener = Listener(yaml_dictionnary, args.current_path)
    listener.main()
