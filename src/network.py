import socket
import threading
import json
import queue
import time
from enum import Enum


class PacketType(str, Enum):
    HELLO = "HELLO"
    SETUP = "SETUP"
    READY = "READY"
    START = "START"
    INPUT = "INPUT"
    CRASH = "CRASH"
    RESULT = "RESULT"
    REMATCH_REQUEST = "REMATCH_REQUEST"
    REMATCH_RESPONSE = "REMATCH_RESPONSE"
    KEEPALIVE = "KEEPALIVE"
    DISCONNECT = "DISCONNECT"


def serialize_packet(packet):
    return (json.dumps(packet) + "\n").encode("utf-8")


def deserialize_packets(buffer):
    messages = []
    while True:
        newline = buffer.find(b"\n")
        if newline == -1:
            break
        raw = buffer[:newline]
        buffer = buffer[newline + 1:]
        if raw:
            try:
                messages.append(json.loads(raw.decode("utf-8")))
            except json.JSONDecodeError:
                continue
    return messages, buffer


class TcpPeer:
    def __init__(self, sock=None):
        self.sock = sock
        self.sock.settimeout(0.5)
        self.recv_buffer = b""
        self.receive_queue = queue.Queue()
        self.running = False
        self.lock = threading.Lock()
        self.thread = None
        self.connected = False
        self.last_activity = time.time()

    def start_receiver(self):
        self.running = True
        self.thread = threading.Thread(target=self._recv_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        with self.lock:
            if self.sock:
                try:
                    self.sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
        self.connected = False

    def send_packet(self, packet):
        if not self.connected or packet is None:
            return
        data = serialize_packet(packet)
        with self.lock:
            try:
                self.sock.sendall(data)
                self.last_activity = time.time()
            except Exception:
                self.connected = False
                self.running = False

    def _recv_loop(self):
        while self.running and self.sock:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.connected = False
                    break
                self.last_activity = time.time()
                self.recv_buffer += data
                packets, self.recv_buffer = deserialize_packets(self.recv_buffer)
                for packet in packets:
                    self.receive_queue.put(packet)
            except socket.timeout:
                continue
            except Exception:
                self.connected = False
                break
        self.running = False
        self.connected = False

    def get_packets(self):
        packets = []
        while not self.receive_queue.empty():
            packets.append(self.receive_queue.get_nowait())
        return packets


class HostServer:
    def __init__(self, bind_ip="0.0.0.0", port=5000, backlog=1):
        self.bind_ip = bind_ip
        self.port = port
        self.backlog = backlog
        self.listener = None
        self.client_peer = None
        self.accept_thread = None
        self.accepting = False
        self.connected = False
        self.connection_lost = False

    def start(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.bind_ip, self.port))
        self.listener.listen(self.backlog)
        self.listener.settimeout(0.5)
        self.accepting = True
        self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.accept_thread.start()

    def _accept_loop(self):
        while self.accepting:
            try:
                client_sock, address = self.listener.accept()
                client_sock.settimeout(0.5)
                self.client_peer = TcpPeer(client_sock)
                self.client_peer.connected = True
                self.client_peer.start_receiver()
                self.connected = True
                self.accepting = False
                break
            except socket.timeout:
                continue
            except Exception:
                self.connection_lost = True
                break

    def stop(self):
        self.accepting = False
        if self.client_peer:
            self.client_peer.stop()
        if self.listener:
            try:
                self.listener.close()
            except Exception:
                pass
        self.connected = False

    def send_packet(self, packet):
        if self.client_peer and self.client_peer.connected:
            self.client_peer.send_packet(packet)
        else:
            self.connected = False

    def get_packets(self):
        if not self.client_peer:
            return []
        return self.client_peer.get_packets()

    def is_connected(self):
        return self.connected and self.client_peer and self.client_peer.connected


class ClientPeer:
    def __init__(self, server_ip, server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.peer = None
        self.connected = False
        self.connection_lost = False

    def connect(self, timeout=5.0):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((self.server_ip, self.server_port))
            sock.settimeout(0.5)
            self.peer = TcpPeer(sock)
            self.peer.connected = True
            self.peer.start_receiver()
            self.connected = True
        except Exception:
            self.connected = False
            self.connection_lost = True

    def stop(self):
        if self.peer:
            self.peer.stop()
        self.connected = False

    def send_packet(self, packet):
        if self.peer and self.peer.connected:
            self.peer.send_packet(packet)
        else:
            self.connected = False

    def get_packets(self):
        if not self.peer:
            return []
        return self.peer.get_packets()

    def is_connected(self):
        return self.connected and self.peer and self.peer.connected
