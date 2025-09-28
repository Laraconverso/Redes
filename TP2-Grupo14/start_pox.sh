#!/bin/bash
set -e

POX_DIR="pox"
EXT_DIR="$POX_DIR/ext"
FIREWALL_SRC="firewall.py"
FIREWALL_DST="$EXT_DIR/firewall.py"
FLOWBUILDER_SRC="flow_builder.py"
FLOWBUILDER_DST="$EXT_DIR/flow_builder.py"

# Check if target switch parameter is provided
if [ $# -gt 1 ]; then
  echo "Usage: $0 [target_switches]"
  echo "Examples:"
  echo "  $0           # Install firewall on all switches"
  echo "  $0 1         # Install firewall on switch 1"
  echo "  $0 1,3       # Install firewall on switches 1 and 3"
  echo "  $0 1,2,3     # Install firewall on switches 1, 2, and 3"
  exit 1
fi

TARGET_SWITCHES=$1

# Check if required files exist
if [ ! -f "$FIREWALL_SRC" ]; then
  echo "ERROR: $FIREWALL_SRC is required but not found!"
  echo "Please make sure $FIREWALL_SRC exists in the current directory."
  exit 1
fi

if [ ! -f "$FLOWBUILDER_SRC" ]; then
  echo "ERROR: $FLOWBUILDER_SRC is required but not found!"
  echo "Please make sure $FLOWBUILDER_SRC exists in the current directory."
  exit 1
fi

# Copy firewall files
echo "Copying $FIREWALL_SRC to $FIREWALL_DST"
cp "$FIREWALL_SRC" "$FIREWALL_DST"

echo "Copying $FLOWBUILDER_SRC to $FLOWBUILDER_DST"
cp "$FLOWBUILDER_SRC" "$FLOWBUILDER_DST"

# Start POX controller
if [ -z "$TARGET_SWITCHES" ]; then
  echo "Starting POX controller with firewall on all switches..."
  python2 $POX_DIR/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall
else
  echo "Starting POX controller with firewall on switches: $TARGET_SWITCHES..."
  python2 $POX_DIR/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning firewall --target_switches=$TARGET_SWITCHES
fi

echo "Press Ctrl+C to stop POX" 