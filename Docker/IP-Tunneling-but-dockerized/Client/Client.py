import heapq

from scapy.all import IP, send, sniff, Raw, bind_layers
import threading
import time
from queue import PriorityQueue
from common.Reliability import ReliableProtocol

bind_layers(IP, ReliableProtocol, proto=253)
# bind_layers( ReliableProtocol, Raw)


# Configuration
DEST_IP = "server"  # Docker Compose service name
SRC_IP = "client"   # Docker Compose service name
INT_IP = "20.20.20.20"
PACKET_INTERVAL = 0.1
ACK_TIMEOUT = 2
FILE_PATH1 = "salam.txt"
FILE_PATH2 = "salami_dobare.txt"
# packet_buffer = PriorityQueue()
packet_buffer = []  # Using heapq as the priority queue
heapq.heapify(packet_buffer)

# Shared resources
pending_acks = {}
ack_lock = threading.Lock()
write_lock = threading.Lock()
stop_threads = threading.Event()


def send_packet(seq_num, chunk, no_more):
    inner_packet = IP(src=INT_IP, dst=SRC_IP, id=seq_num) / ReliableProtocol(seq_num=seq_num, no_more=no_more) / Raw(
        load=chunk)
    # inner_packet.show()
    outer_packet = IP(src=SRC_IP, dst=DEST_IP, id=seq_num, proto=253) / ReliableProtocol(seq_num=seq_num,
                                                                                         no_more=no_more) / inner_packet
    send(outer_packet, verbose=0)
    # print(f"Sent packet with ID: {packet_id}")

    with ack_lock:
        pending_acks[seq_num] = (outer_packet, time.time())


length = -1


def packet_listener():
    def packet_handler(packet):
        global length
        #packet.show()
        if packet.haslayer(ReliableProtocol):
            seq_num = packet[ReliableProtocol].seq_num
            # packet_buffer.put((seq_num, packet))
            if (seq_num, packet) not in packet_buffer:
                heapq.heappush(packet_buffer, (seq_num, packet))
            send_ack(packet)
            if packet[ReliableProtocol].no_more == 1:
                length = packet[ReliableProtocol].seq_num
                print("hey length now is ",length)

            if len(packet_buffer) == length + 1:
                print("hi")
                write_packet_to_file()

    sniff(filter=f"ip and src host {INT_IP}", prn=packet_handler, store=False,
          stop_filter=lambda _: stop_threads.is_set())


def listen_for_acks():
    def ack_handler(packet):
        if packet.haslayer(ReliableProtocol):
            seq_num = packet[ReliableProtocol].seq_num
            with ack_lock:
                if seq_num in pending_acks:
                    del pending_acks[seq_num]
                    print(f"Received ack packet with sequence number: {seq_num}")

    sniff(filter=f"ip and src host {DEST_IP}", prn=ack_handler, stop_filter=lambda _: stop_threads.is_set(),
          store=False)


def resend_packets():
    while not stop_threads.is_set():
        time.sleep(ACK_TIMEOUT)
        current_time = time.time()
        with ack_lock:
            for seq_num, (packet, timestamp) in pending_acks.items():
                if current_time - timestamp > ACK_TIMEOUT:
                    print(f"Resending packet with sequence number: {seq_num}")
                    send(packet, verbose=0)


def write_packet_to_file():
    with write_lock:
        with open(FILE_PATH2, 'a') as f:
            while packet_buffer:
                _,packet = heapq.heappop(packet_buffer)
                packet.show()
                inner_packet = packet[IP].payload
                if inner_packet.haslayer(Raw):
                    f.write(inner_packet[Raw].load.decode())
                else:
                    f.write("No Raw Data\n")


def packet_sender():
    with open(FILE_PATH1, 'r') as file:
        data = file.read()

    chunks = [data[i:i + 10] for i in range(0, len(data), 10)]
    no_more = 0
    for seq_num, chunk in enumerate(chunks):
        if stop_threads.is_set():
            break
        if seq_num == len(chunks) - 1:
            no_more = 1
        send_packet(seq_num, chunk, no_more)
        time.sleep(PACKET_INTERVAL)


def send_ack(packet):
    seq_num = packet[ReliableProtocol].seq_num
    ack_packet = IP(dst=DEST_IP) / ReliableProtocol(seq_num=seq_num, ack_num=1)
    send(ack_packet, verbose=0)
    print(f"ack sent for packet {seq_num}")


if __name__ == "__main__":
    sender_thread = threading.Thread(target=packet_sender, daemon=True)
    ack_listener_thread = threading.Thread(target=listen_for_acks, daemon=True)
    receiver_thread = threading.Thread(target=packet_listener, daemon=True)
    resend_thread = threading.Thread(target=resend_packets, daemon=True)

    sender_thread.start()
    ack_listener_thread.start()
    receiver_thread.start()
    resend_thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping sender threads...")
        stop_threads.set()

    sender_thread.join()
    receiver_thread.join()
    ack_listener_thread.join()
    resend_thread.join()

    print("Sender stopped.")
