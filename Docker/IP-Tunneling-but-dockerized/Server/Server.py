from scapy.all import sniff, send, IP, bind_layers, Raw
import threading
from queue import PriorityQueue
import time 
from common.Reliability import ReliableProtocol


bind_layers(IP, ReliableProtocol, proto=253)  # Use an unused protocol number like 253
bind_layers(ReliableProtocol, IP)

# Shared resources
packet_buffer = PriorityQueue()
buffer_lock = threading.Lock()
pending_acks = {}
ack_lock = threading.Lock()

stop_threads = threading.Event()
#configuration 
SRC_IP = "server" 
DEST_IP = "client"
ACK_TIMEOUT = 10

# Function to send an acknowledgment
def send_ack(packet):
    seq_num = packet[ReliableProtocol].seq_num
    
    ack_packet = IP(dst=packet[IP].src) / ReliableProtocol(seq_num=seq_num)
    send(ack_packet, verbose=0)
    #print(f"ack sent for packet {seq_num}")

# Thread 1 - Packet Listener
def packet_listener():
    def packet_handler(packet):
        if packet.haslayer(ReliableProtocol):
            seq_num = packet[ReliableProtocol].seq_num 
            with buffer_lock:
                packet_buffer.put((seq_num, packet))
            send_ack(packet)

    sniff(filter=f"ip and src host {DEST_IP}", prn=packet_handler, store=False, stop_filter=lambda _: stop_threads.is_set())

# Thread 2 - Packet Processor
def packet_processor():
    while not stop_threads.is_set():
        try:
            with buffer_lock:
                if not packet_buffer.empty():
                    packet_id, packet = packet_buffer.get()
                    process_packet(packet)
        except Exception as e:
            print(f"Error processing packet: {e}")

# Function to process a packet
def process_packet(packet):
    time.sleep(0.1)
    #print(f"Processing packet with ID: {packet_id}")
    #packet.show()
    real_inner_packet = packet[ReliableProtocol].payload
    if real_inner_packet.haslayer(IP):
        # Extract the inner packet
        inner_ip_packet = real_inner_packet[IP]
        inner_payload = inner_ip_packet.payload
        
        #print(f"Received data: {inner_payload}")
        real_inner_packet.show()
        send(real_inner_packet)
        #print("inner packet sent")
        with ack_lock:
            seq_num = real_inner_packet[ReliableProtocol].seq_num
            pending_acks[seq_num] = (real_inner_packet, time.time())
        

def listen_for_acks():
    def ack_handler(packet):
        if packet.haslayer(ReliableProtocol) and packet[ReliableProtocol].ack_num == 1:
            seq_num = packet[ReliableProtocol].seq_num
            #print(pending_acks, "first time")
            
            with ack_lock:
                if seq_num in pending_acks:
                    del pending_acks[seq_num]
                    #print(pending_acks, "after deletion")
                    print(f"Received ack packet with sequence number: {seq_num}")

    sniff(filter=f"ip and src host {DEST_IP}", prn=ack_handler, stop_filter=lambda _: stop_threads.is_set(),
          store=False)


def resend_packets():
    while not stop_threads.is_set():
        time.sleep(ACK_TIMEOUT)
        with ack_lock:
            current_time = time.time()
            for seq_num, (packet, timestamp) in pending_acks.items():
                if current_time - timestamp > ACK_TIMEOUT:
                    print(f"Resending packet with sequence number: {seq_num}")
                    send(packet, verbose=0)

        

# Main function to start threads
def main():
    listener_thread = threading.Thread(target=packet_listener, daemon=True)
    processor_thread = threading.Thread(target=packet_processor, daemon=True)
    ack_listener_thread = threading.Thread(target=listen_for_acks, daemon=True)
    resend_thread = threading.Thread(target=resend_packets, daemon=True)
    
    
    
    listener_thread.start()
    processor_thread.start()
    ack_listener_thread.start()
    resend_thread.start()

    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Shutting down threads...")
        stop_threads.set()

    listener_thread.join()
    processor_thread.join()
    ack_listener_thread.join()
    resend_thread.join()
    print("All threads stopped.")

if __name__ == "__main__":
    main()
