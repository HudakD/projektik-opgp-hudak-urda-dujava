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
    COUNTDOWN = "COUNTDOWN"
    GAME_BEGIN = "GAME_BEGIN"
    GAME_STATE = "GAME_STATE"
    LOBBY_STATE = "LOBBY_STATE"
    CHAT = "CHAT"
    NAME = "NAME"
    SERVER_FULL = "SERVER_FULL"
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
    def __init__(self, bind_ip="0.0.0.0", port=5000, backlog=1, max_clients=1):
        self.bind_ip = bind_ip
        self.port = port
        self.backlog = backlog
        self.max_clients = max(1, max_clients)
        self.listener = None
        self.clients = {}
        self.client_addresses = {}
        self.next_client_id = 1
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
                if len(self.clients) >= self.max_clients:
                    overflow_peer = TcpPeer(client_sock)
                    overflow_peer.connected = True
                    overflow_peer.send_packet({"type": PacketType.SERVER_FULL})
                    overflow_peer.stop()
                    continue

                client_id = self.next_client_id
                self.next_client_id += 1
                peer = TcpPeer(client_sock)
                peer.connected = True
                peer.client_id = client_id
                peer.start_receiver()
                self.clients[client_id] = peer
                self.client_addresses[client_id] = address
                self.connected = True
            except socket.timeout:
                continue
            except Exception:
                self.connection_lost = True
                break

    def stop(self):
        self.accepting = False
        for peer in list(self.clients.values()):
            peer.stop()
        self.clients.clear()
        self.client_addresses.clear()
        if self.listener:
            try:
                self.listener.close()
            except Exception:
                pass
        self.connected = False

    def send_packet(self, packet, client_id=None):
        if client_id is not None:
            peer = self.clients.get(client_id)
            if peer and peer.connected:
                peer.send_packet(packet)
            return

        dead = []
        for cid, peer in list(self.clients.items()):
            if peer.connected:
                peer.send_packet(packet)
            else:
                dead.append(cid)
        for cid in dead:
            self.clients.pop(cid, None)
            self.client_addresses.pop(cid, None)
        self.connected = bool(self.clients)

    def get_packets(self):
        packets = []
        dead = []
        for cid, peer in list(self.clients.items()):
            if not peer.connected:
                dead.append(cid)
                continue
            for packet in peer.get_packets():
                if isinstance(packet, dict):
                    packet["_client_id"] = cid
                packets.append(packet)
        for cid in dead:
            self.clients.pop(cid, None)
            self.client_addresses.pop(cid, None)
            packets.append({"type": PacketType.DISCONNECT, "_client_id": cid})
        self.connected = bool(self.clients)
        return packets

    def is_connected(self):
        return self.accepting or bool(self.clients)

    def get_client_count(self):
        return len(self.clients)


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
