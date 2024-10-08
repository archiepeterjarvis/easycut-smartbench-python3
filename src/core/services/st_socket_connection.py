import socket
import sys
import threading
from time import sleep
from core.logging.logging_system import Logger

PORT = 65432


class ServerConnection:
    smartbench_name_filepath = "/home/pi/smartbench_name.txt"
    smartbench_name = "My SmartBench"
    sock = None
    HOST = ""
    prev_host = ""
    is_socket_available = True
    doing_reconnect = False
    poll_connection = None

    def __init__(self, settings_manager):
        self.set = settings_manager
        self.get_smartbench_name()
        server_thread = threading.Thread(target=self.initialise_server_connection)
        server_thread.daemon = True
        server_thread.start()
        self.connection_loop_thread = None

    def __del__(self):
        Logger.debug("Server connection class has been deleted")

    def initialise_server_connection(self):
        Logger.info("Initialising server connection...")
        self.HOST = self.set.ip_address
        Logger.info("IP address: " + str(self.HOST))
        self.prev_host = self.HOST
        self.doing_reconnect = True
        self.set_up_socket()
        checking_thread = threading.Thread(target=self.do_check_connection_loop)
        checking_thread.daemon = True
        checking_thread.start()

    def set_up_socket(self):
        Logger.debug("Attempting to set up socket with IP address: " + str(self.HOST))
        if sys.platform != "win32" and sys.platform != "darwin":
            if self.HOST != "":
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.sock.bind((self.HOST, PORT))
                    self.sock.listen(5)
                    self.sock.settimeout(20)
                    self.is_socket_available = True

                    if self.connection_loop_thread is not None:
                        self.connection_loop_thread.join()

                    self.connection_loop_thread = threading.Thread(target=self.do_connection_loop, daemon=True)
                    self.connection_loop_thread.start()
                except:
                    Logger.exception("Unable to set up socket")
            else:
                Logger.error("No IP address available to open socket with.")
        else:
            self.set.get_public_ip_address()
        self.doing_reconnect = False

    def do_connection_loop(self):
        Logger.info("Starting server connection loop...")
        while True:
            try:
                Logger.debug("Waiting for connection...")
                if self.is_socket_available:
                    self.set.get_public_ip_address()
                    conn, addr = self.sock.accept()
                    Logger.info("Accepted connection with IP address " + str(self.HOST))
                    self.set.start_ssh()
                    try:
                        self.get_smartbench_name()
                        conn.send(self.smartbench_name)
                    except:
                        Logger.exception("Message couldn't be sent")
                    conn.close()
                else:
                    sleep(20)
            except TimeoutError:
                sleep(2)
            except Exception:
                if self.is_socket_available:
                    self.close_and_reconnect_socket()
                    sleep(20)

    def do_check_connection_loop(self):
        Logger.info("Starting connection checking loop...")
        while True:
            if not self.doing_reconnect:
                self.check_connection()
            sleep(2)

    def close_and_reconnect_socket(self):
        if not self.doing_reconnect:
            self.doing_reconnect = True
            try:
                Logger.debug("Closing socket before attempting to reconnect...")
                self.is_socket_available = False
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except:
                Logger.exception("Attempted to close socket but failed")
            Logger.info("Try to reconnect...")
            sleep(2)
            self.set_up_socket()

    def check_connection(self):
        self.HOST = self.set.ip_address
        if self.HOST != self.prev_host and not self.doing_reconnect:
            self.prev_host = self.HOST
            self.close_and_reconnect_socket()

    def get_smartbench_name(self):
        try:
            file = open(self.smartbench_name_filepath)
            self.smartbench_name = str(file.read())
            file.close()
        except:
            self.smartbench_name = "My SmartBench"
        self.smartbench_name = self.smartbench_name.replace("\n", " ")
        self.smartbench_name = self.smartbench_name.strip()
