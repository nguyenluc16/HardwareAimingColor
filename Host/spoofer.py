import os
import re
import time
import random
import requests
import zipfile
import subprocess
import win32com.client
import logging

# Cấu hình logging: hiển thị thời gian, mức độ và thông điệp.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Spoofer:
    """
    The Spoofer class handles setting up the Arduino CLI, detecting connected mouse devices,
    configuring Arduino Leonardo board settings, and compiling/uploading the Arduino sketch.
    """
    SKETCH_FILE = "arduino/arduino.ino"
    BOARDS_TXT_PATH = os.path.expandvars("%LOCALAPPDATA%/Arduino15/packages/arduino/hardware/avr/1.8.6/boards.txt")

    def __init__(self):
        """
        Initializes the Spoofer class, setting up the Arduino CLI path.
        """
        self.arduino_cli_path = os.path.join(os.getcwd(), "arduino", "arduino-cli.exe")
        logging.info("Initialized Spoofer with Arduino CLI path: %s", self.arduino_cli_path)

    def download_arduino_cli(self):
        """
        Downloads and extracts the Arduino CLI if it doesn't already exist.
        """
        try:
            os.makedirs("arduino", exist_ok=True)
            if os.path.exists(self.arduino_cli_path):
                logging.info("Arduino CLI already exists.")
                return
            zip_path = os.path.join(os.getcwd(), "arduino", "arduino-cli.zip")
            if not os.path.exists(zip_path):
                logging.info("Downloading Arduino CLI...")
                response = requests.get("https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip", stream=True)
                with open(zip_path, "wb") as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)
                logging.info("Download completed.")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("./arduino/")
            logging.info("Arduino CLI extracted successfully.")
        except Exception as e:
            logging.error("Error downloading or extracting Arduino CLI: %s", e)
            raise

    def update_boards(self, vendor_id, product_id):
        """
        Updates the 'boards.txt' file to replace the VID and PID for the Arduino Leonardo board.
        
        Args:
            vendor_id (str): Vendor ID (VID) in hexadecimal format (e.g., '0x2341').
            product_id (str): Product ID (PID) in hexadecimal format (e.g., '0x8036').
        """
        try:
            with open(self.BOARDS_TXT_PATH, 'r') as boards_file:
                board_config_lines = boards_file.readlines()
        except Exception as e:
            logging.error("Error reading boards.txt: %s", e)
            raise

        random_name = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=6))
        updated_lines = []
        for line in board_config_lines:
            if line.startswith("leonardo.name="):
                updated_lines.append(f"leonardo.name={random_name}\n")
            elif line.startswith("leonardo.vid."):
                suffix = line.split("leonardo.vid.")[1].split("=")[0]
                updated_lines.append(f"leonardo.vid.{suffix}={vendor_id}\n")
            elif line.startswith("leonardo.pid."):
                suffix = line.split("leonardo.pid.")[1].split("=")[0]
                updated_lines.append(f"leonardo.pid.{suffix}={product_id}\n")
            elif line.startswith("leonardo.build.vid="):
                updated_lines.append(f"leonardo.build.vid={vendor_id}\n")
            elif line.startswith("leonardo.build.pid="):
                updated_lines.append(f"leonardo.build.pid={product_id}\n")
            elif line.startswith("leonardo.build.usb_product="):
                updated_lines.append(f"leonardo.build.usb_product=\"{random_name}\"\n")
            else:
                updated_lines.append(line)

        try:
            with open(self.BOARDS_TXT_PATH, 'w') as boards_file:
                boards_file.writelines(updated_lines)
            logging.info("Boards.txt updated with new VID/PID and board name.")
        except Exception as e:
            logging.error("Error writing boards.txt: %s", e)
            raise

    def detect_mouse_devices(self):
        """
        Detects all connected mouse devices using WMI and returns a list of tuples containing the device name, VID, and PID.
        
        Returns:
            list: A list of tuples where each tuple contains the device name, VID, and PID.
        """
        try:
            wmi_service = win32com.client.GetObject("winmgmts:")
            mouse_devices = wmi_service.InstancesOf("Win32_PointingDevice")
            detected_mice = []
            for device in mouse_devices:
                device_name = device.Name
                id_match = re.search(r'VID_(\w+)&PID_(\w+)', device.PNPDeviceID)
                vid, pid = id_match.groups() if id_match else (None, None)
                detected_mice.append((device_name, vid, pid))
            logging.info("Detected %d mouse devices.", len(detected_mice))
            return detected_mice
        except Exception as e:
            logging.error("Error detecting mouse devices: %s", e)
            return []

    def prompt_mouse_selection(self):
        """
        Prompts the user to select a mouse device and configures the Arduino Leonardo board settings accordingly.
        """
        detected_mice = self.detect_mouse_devices()
        if not detected_mice:
            logging.error("No mouse device found. Exiting in 10 seconds...")
            time.sleep(10)
            exit(1)

        os.system('cls' if os.name == 'nt' else 'clear')
        valid_mice = {}
        for device_name, vid, pid in detected_mice:
            if "USB Input Device" in device_name and vid and pid:
                device_key = (vid, pid)
                if device_key not in valid_mice:
                    valid_mice[device_key] = device_name

        if not valid_mice:
            logging.error("No valid USB Input Device found. Exiting in 10 seconds...")
            time.sleep(10)
            exit(1)

        for index, ((vid, pid), device_name) in enumerate(valid_mice.items(), 1):
            print(f"{index} → {device_name}\tVID: {vid}, PID: {pid}")

        while True:
            try:
                selected_mouse_index = int(input("\nSelect your mouse number: ")) - 1
                if selected_mouse_index < 0 or selected_mouse_index >= len(valid_mice):
                    print("Invalid selection. Try again.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")

        selected_device_key = list(valid_mice.keys())[selected_mouse_index]
        selected_vid, selected_pid = selected_device_key
        self.update_boards("0x" + selected_vid, "0x" + selected_pid)
        logging.info("Mouse device selected: VID=%s, PID=%s", selected_vid, selected_pid)

    def install_avr_core(self):
        """
        Checks if the AVR core and Mouse library are already installed. If not, installs them using the Arduino CLI.
        """
        try:
            result = subprocess.run([self.arduino_cli_path, "core", "list"], capture_output=True, text=True)
            if "arduino:avr" not in result.stdout and "1.8.6" not in result.stdout:
                logging.info("Installing AVR core 1.8.6...")
                subprocess.run([self.arduino_cli_path, "core", "install", "arduino:avr@1.8.6"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result = subprocess.run([self.arduino_cli_path, "lib", "list"], capture_output=True, text=True)
            if "Mouse" not in result.stdout:
                logging.info("Installing Mouse library...")
                subprocess.run([self.arduino_cli_path, "lib", "install", "Mouse"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logging.error("Error installing AVR core or Mouse library: %s", e)
            raise

    def compile_sketch(self):
        """
        Compiles the Arduino sketch using the Arduino CLI.
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        com_port = input("Enter your Arduino Leonardo COM-Port (e.g., COM3): ").strip()
        logging.info("Compiling sketch...")
        if not os.path.exists(self.SKETCH_FILE):
            logging.error("Error: Sketch file '%s' not found!", self.SKETCH_FILE)
            return
        try:
            subprocess.run([self.arduino_cli_path, "compile", "--fqbn", "arduino:avr:leonardo", self.SKETCH_FILE],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.upload_sketch(com_port)
        except Exception as e:
            logging.error("Compilation error: %s", e)
            raise

    def upload_sketch(self, com_port):
        """
        Uploads the compiled sketch to the Arduino Leonardo board.
        """
        if not os.path.exists(self.SKETCH_FILE):
            logging.error("Error: Sketch file '%s' not found!", self.SKETCH_FILE)
            return
        logging.info("Uploading sketch to Arduino on port %s...", com_port)
        try:
            upload_command = [self.arduino_cli_path, "upload", "-p", com_port, "--fqbn", "arduino:avr:leonardo", self.SKETCH_FILE]
            result = subprocess.run(upload_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                logging.info("Spoof finished successfully, you can now use the colorbot!")
            else:
                logging.error("Failed to upload sketch. Return code: %s", result.returncode)
                logging.error("Output: %s", result.stdout)
                logging.error("Error: %s", result.stderr)
        except Exception as e:
            logging.error("Upload error: %s", e)
            raise

    def run(self):
        """
        Executes the entire process of setting up and configuring the Arduino Leonardo.
        """
        try:
            self.download_arduino_cli()
            self.install_avr_core()
            self.prompt_mouse_selection()
            self.compile_sketch()
        except Exception as e:
            logging.error("An error occurred during execution: %s", e)
            exit(1)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("title github.com/nguyenluc16/HardwareAimingColor")
    Spoofer().run()
