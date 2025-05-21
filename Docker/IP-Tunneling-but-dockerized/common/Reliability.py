from scapy.all import Packet, IntField, ShortField, send, sniff

class ReliableProtocol(Packet):
    name = "ReliableProtocol"
    fields_desc = [
        IntField("seq_num", 0),  # Sequence number for reliable transmission
        IntField("ack_num", 0),  # Acknowledgment number
        IntField("no_more", 0),  # Custom flags (e.g., bit 0 for ACK, bit 1 for data)
    ]