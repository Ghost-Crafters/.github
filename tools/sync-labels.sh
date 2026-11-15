#!/bin/sh
# Usage: tools/sync-labels.sh <owner/repo> [--dry-run] [--prune]
exec python3 "$(dirname "$0")/sync_labels.py" "$@"
