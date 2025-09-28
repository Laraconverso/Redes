#!/bin/bash

# Usage: ./run_topo.sh <number_of_switches>
# Note: This script assumes POX is already running in a separate terminal

TOPOLOGY_SCRIPT="topology.py"

if [ $# -ne 1 ]; then
  echo "Usage: $0 <number_of_switches>"
  echo "Note: Make sure POX is already running in a separate terminal"
  exit 1
fi

SWITCHES=$1

# Start Mininet topology
echo "Starting Mininet topology with $SWITCHES switches..."
sudo python3 "$TOPOLOGY_SCRIPT" "$SWITCHES"