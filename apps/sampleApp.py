# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# Task 2: Hybrid Chat Application - Tracker Server (Demo with WeApRous)
#

"""
sampleApp.py - Task 2 Tracker Server (DEMO ONLY)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a DEMO showing how WeApRous routing works for Task 2.
WeApRous only supports PRINTING LOG, not returning JSON responses.

For REAL Task 2 testing, use peer.py application which implements
full P2P functionality including tracker communication.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import argparse
from daemon.weaprous import WeApRous

# ============================================
# TASK 2: TRACKER SERVER DEMO
# ============================================

app = WeApRous()

# In-memory peer storage (for demo)
peers = {}
PEER_TTL = 300


def cleanup_expired_peers():
    """Remove expired peers"""
    current_time = time.time()
    expired = [pid for pid, info in peers.items() 
               if current_time - info['last_seen'] > PEER_TTL]
    for pid in expired:
        del peers[pid]
        print "[Tracker] Removed expired peer: {}".format(pid)


@app.route('/submit-info/', methods=['POST'])
def submit_info(headers="", body=""):
    """
    Task 2: POST /submit-info/ - Peer registration
    Returns HTTP response string with JSON body
    """
    print "[Tracker] POST /submit-info/"
    print "[Tracker] Body: {}".format(body)
    
    try:
        data = json.loads(body) if body else {}
        peer_ip = data.get('ip', '')
        peer_port = data.get('port', 0)
        
        if not peer_ip or not peer_port:
            print "[Tracker] ERROR: Missing ip or port"
            response_body = json.dumps({'error': 'Missing ip or port'})
            return (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: {}\r\n"
                "\r\n"
                "{}".format(len(response_body), response_body)
            )
        
        peer_id = "{}:{}".format(peer_ip, peer_port)
        peers[peer_id] = {
            'ip': peer_ip,
            'port': int(peer_port),
            'peer_id': peer_id,
            'last_seen': time.time()
        }
        print "[Tracker] Registered: {} - Total: {}".format(peer_id, len(peers))
        
        response_body = json.dumps({
            'status': 'ok',
            'peer_id': peer_id
        })
        return (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(response_body), response_body)
        )
        
    except Exception as e:
        print "[Tracker] ERROR: {}".format(e)
        response_body = json.dumps({'error': str(e)})
        return (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(response_body), response_body)
        )


@app.route('/get-list/', methods=['GET'])
def get_list(headers="", body=""):
    """
    Task 2: GET /get-list/ - Get peer list
    Returns HTTP response string with JSON body
    """
    print "[Tracker] GET /get-list/"
    
    try:
        cleanup_expired_peers()
        
        peer_list = [
            {
                'ip': info['ip'],
                'port': info['port'],
                'peer_id': info['peer_id']
            }
            for info in peers.values()
        ]
        
        print "[Tracker] Returning {} peers".format(len(peer_list))
        
        response_body = json.dumps({
            'status': 'ok',
            'count': len(peer_list),
            'peers': peer_list
        })
        return (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(response_body), response_body)
        )
        
    except Exception as e:
        print "[Tracker] ERROR: {}".format(e)
        response_body = json.dumps({'error': str(e)})
        return (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(response_body), response_body)
        )


@app.route('/remove/', methods=['POST'])
def remove_peer(headers="", body=""):
    """
    Task 2: POST /remove/ - Unregister peer
    Returns HTTP response string with JSON body
    """
    print "[Tracker] POST /remove/"
    print "[Tracker] Body: {}".format(body)
    
    try:
        data = json.loads(body) if body else {}
        peer_id = data.get('peer_id', '')
        
        if not peer_id:
            print "[Tracker] ERROR: Missing peer_id"
            response_body = json.dumps({'error': 'Missing peer_id'})
            return (
                "HTTP/1.1 400 Bad Request\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: {}\r\n"
                "\r\n"
                "{}".format(len(response_body), response_body)
            )
        
        if peer_id in peers:
            del peers[peer_id]
            print "[Tracker] Unregistered: {} - Total: {}".format(peer_id, len(peers))
            response_body = json.dumps({'status': 'ok', 'message': 'Peer unregistered'})
            status = "HTTP/1.1 200 OK\r\n"
        else:
            print "[Tracker] WARNING: Peer not found: {}".format(peer_id)
            response_body = json.dumps({'status': 'ok', 'message': 'Peer not found (already removed)'})
            status = "HTTP/1.1 200 OK\r\n"
        
        return (
            "{}Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(status, len(response_body), response_body)
        )
        
    except Exception as e:
        print "[Tracker] ERROR: {}".format(e)
        response_body = json.dumps({'error': str(e)})
        return (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(response_body), response_body)
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Tracker Server DEMO',
        description='Task 2 - WeApRous Demo (NOT for real testing)'
    )
    parser.add_argument('--server-ip', default='0.0.0.0')
    parser.add_argument('--server-port', type=int, default=8000)
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Task 2: Tracker Server DEMO (WeApRous)")
    print("=" * 60)
    print("IMPORTANT: This is DEMO ONLY!")
    print("- WeApRous routes only PRINT logs")
    print("- They do NOT return JSON responses")
    print("- For REAL Task 2 testing, use peer.py")
    print("=" * 60)
    print("IP: {}".format(args.server_ip))
    print("Port: {}".format(args.server_port))
    print("Routes registered:")
    print("  - POST /submit-info/  : Print registration info")
    print("  - GET  /get-list/     : Print peer list")
    print("  - POST /remove/       : Unregister peer")
    print("=" * 60)
    
    app.prepare_address(args.server_ip, args.server_port)
    app.run()
