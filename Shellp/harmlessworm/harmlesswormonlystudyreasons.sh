#!/bin/bash
set -x
#harmless self-replicator with depth limit

MAX_DEPTH=1000
CURRENT_DEPTH=${1:-1}

echo "Replicator running at depth $CURRENT_DEPTH on $(date)"

if [ "$CURRENT_DEPTH" -lt "$MAX_DEPTH" ]; then
	timestamp=$(date +%s)
	new_file="copy_${CURRENT_DEPTH}_$timestamp.sh"

	cp "$0" "$new_file"
	chmod +x "$new_file"

	echo "Created $new_file . now run..."
	./"$new_file" $((CURRENT_DEPTH + 1))

else 
	echo "Max depth $MAX_DEPTH readched. stopping replication" 
fi

