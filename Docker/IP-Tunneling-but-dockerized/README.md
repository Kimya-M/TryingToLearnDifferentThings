# IP Tunneling with Reliable Protocol


This project implements a simple IP tunneling system that transmits data reliably using a custom protocol. It is designed to simulate a reliable communication channel between two devices by ensuring that packets are sent and acknowledged, and retransmitting lost packets if necessary. The project uses Scapy, a powerful Python library for network packet manipulation, to handle the packet sending, receiving, and processing.

## Overview
- **Sender (Client `A.py`):** Reads a file, splits it into chunks, and sends the chunks over the network using a custom reliable protocol.
- **Receiver (Server `B.py`):** Listens for incoming packets, processes them, and acknowledges them. It also handles packet retransmissions if acknowledgments are not received within a timeout period.
- **Reliable Protocol:** A custom protocol (`ReliableProtocol`) used for encapsulating data packets. It includes sequence numbers, acknowledgment numbers, and flags to indicate whether more data remains to be sent.
  
## Requirements
- Python 3.6+
- Scapy: Install it with pip install scapy
- A network environment with at least two devices for testing (can be simulated locally using virtual machines or Docker containers).
  
## Features

- **IP Tunneling:** System A encapsulates IP packets inside another IP packet and forwards them to System B.
- **Reliability:** : Data is divided into chunks and each chunk is assigned a sequence number. The receiver sends acknowledgments for each chunk, and the sender retransmits any chunks not acknowledged within a certain timeout period.
- **Multithreading:** The project uses multiple threads to handle sending packets, receiving packets, listening for acknowledgments, and resending lost packets concurrently.
- **Packet Resending:** If a packet is not acknowledged within the timeout, it is resent to ensure reliable delivery.
- **Custom Protocol:** The project uses a custom `ReliableProtocol` to simulate reliable communication, with sequence numbers, acknowledgment numbers, and a flag to indicate whether more packets are coming.

## Files
- `A.py`:The sender code that reads data from a file, splits it into chunks, and sends it using the `ReliableProtocol`.
- `B.py`:The receiver code that listens for incoming packets, acknowledges them, and processes them once received.
- `rely_on_me.py`: Defines the `ReliableProtocol` custom protocol.
- `salam.txt`: Sample file that can be used for testing the sender's functionality (replace with your own file).
- `salami_dobare.txt`: The output file where the received data is written.

## How It Works

### 1. **Sender**:

- The sender reads the file `salam.txt` and splits the content into 10-byte chunks.
- Each chunk is sent as a packet, with a sequence number attached.
- The sender waits for an acknowledgment from the receiver before sending the next chunk.
- If no acknowledgment is received within a specified timeout period, the sender retransmits the packet.

### 2. **Receiver**:

- The receiver listens for incoming packets.
- Once a packet is received, the receiver sends an acknowledgment for that packet.
- The received data is processed and saved to the file `salami_dobare.txt`.

### 3. **Reliable Protocol**:

- Each packet includes a sequence number (`seq_num`), acknowledgment number (`ack_num`), and a flag (`no_more`) indicating if it is the last packet.
- Acknowledgments are sent back to the sender with the sequence number of the received packet.


## Usage

### 1. **Setup**:

- Ensure that both the sender and receiver are running on different devices or different network interfaces if running on the same machine.
- Modify the IP addresses in both the sender and receiver code:
  - `SRC_IP`: The source IP address of the sender.
  - `DEST_IP`: The destination IP address of the receiver.
  - `INT_IP`: The internal IP used for tunneling.
 
  ### 2. **Running the Code**:

- Start the **receiver** first. This can be done by running the `receiver.py` script:

    ```bash
    python B.py
    ```

- Then start the **sender** by running the `sender.py` script:

    ```bash
    python A.py
    ```

### 3. **Stop the Process**:

- To stop the sender and receiver, press `Ctrl+C`. The threads will stop gracefully.

## Future Enhancements
- Error Handling: Improve the error handling mechanism to manage network disruptions or other unexpected issues more effectively.
- File Compression: Implement file compression to reduce the size of the data being sent over the network.
- Authentication: Add security features like packet authentication to ensure that the data is coming from a trusted source.
