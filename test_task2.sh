#!/bin/bash
# -*- coding: utf-8 -*-
#
# Test script for Task 2 - P2P Chat
#

echo "=========================================="
echo "Task 2: P2P Chat Test Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test tracker APIs
echo "Testing Tracker APIs..."
echo ""

# 1. Start tracker (manual - run in separate terminal)
echo "1. Start tracker server (manual):"
echo "   source venv2/bin/activate"
echo "   python start_sampleapp.py --server-port 8000"
echo ""
read -p "Press Enter when tracker is running..."

# 2. Test peer registration
echo ""
echo "2. Test peer registration (POST /submit-info/)..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/submit-info/ \
  -H "Content-Type: application/json" \
  -d '{"ip":"127.0.0.1","port":5001}')

if echo "$RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Peer registration SUCCESS${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Peer registration FAILED${NC}"
    echo "Response: $RESPONSE"
fi

# 3. Test get peer list
echo ""
echo "3. Test get peer list (GET /get-list/)..."
RESPONSE=$(curl -s http://127.0.0.1:8000/get-list/)

if echo "$RESPONSE" | grep -q "peers"; then
    echo -e "${GREEN}✓ Get peer list SUCCESS${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Get peer list FAILED${NC}"
    echo "Response: $RESPONSE"
fi

# 4. Test heartbeat
echo ""
echo "4. Test heartbeat (POST /heartbeat/)..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/heartbeat/ \
  -H "Content-Type: application/json" \
  -d '{"peer_id":"127.0.0.1:5001"}')

if echo "$RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Heartbeat SUCCESS${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Heartbeat FAILED${NC}"
    echo "Response: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "Tracker API tests completed!"
echo "=========================================="
echo ""

# Instructions for P2P testing
echo "To test P2P communication:"
echo ""
echo "Terminal 1 (Tracker):"
echo "  source venv2/bin/activate"
echo "  python start_sampleapp.py --server-port 8000"
echo ""
echo "Terminal 2 (Peer Alice):"
echo "  source venv2/bin/activate"
echo "  python apps/peer.py --tracker http://127.0.0.1:8000 --port 5001 --name Alice"
echo ""
echo "Terminal 3 (Peer Bob):"
echo "  source venv2/bin/activate"
echo "  python apps/peer.py --tracker http://127.0.0.1:8000 --port 5002 --name Bob"
echo ""
echo "Terminal 4 (Peer Charlie):"
echo "  source venv2/bin/activate"
echo "  python apps/peer.py --tracker http://127.0.0.1:8000 --port 5003 --name Charlie"
echo ""
echo "Commands in peer console:"
echo "  /help       - Show help"
echo "  /peers      - List connected peers"
echo "  /discover   - Discover new peers"
echo "  Hello!      - Broadcast message"
echo "  /direct 127.0.0.1:5002 Hi Bob  - Direct message to Bob"
echo "  /quit       - Exit"
echo ""
