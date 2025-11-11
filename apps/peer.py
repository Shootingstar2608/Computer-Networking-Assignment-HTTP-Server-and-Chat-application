# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 pdnguyen of HCMC University of Technology VNU-HCM.
# Task 2: Hybrid Chat Application - Peer Application
#

"""
peer.py - Task 2 Peer Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module implements a peer in the hybrid P2P chat application.

Architecture:
1. Client-Server paradigm (initialization):
   - HTTP client to register with tracker
   - HTTP client to discover other peers

2. Peer-to-Peer paradigm (chatting):
   - WeApRous server for receiving P2P messages
   - HTTP client for sending P2P messages to other peers

P2P APIs (WeApRous):
- POST /connect-peer/    : Accept connection from another peer
- POST /broadcast-peer/  : Receive broadcast message
- POST /send-peer/       : Receive direct message

Usage:
    python apps/peer.py --tracker http://127.0.0.1:8000 --port 5001 --name Alice
"""

from __future__ import print_function
import sys
import os
# Add parent directory to path so we can import daemon module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import argparse
import threading
import urllib2
from daemon.weaprous import WeApRous


class PeerApp:
    """
    Hybrid P2P Chat Peer Application
    
    Combines client-server and peer-to-peer paradigms:
    - Client: registers with tracker, discovers peers
    - Server: accepts P2P connections and messages
    """
    
    def __init__(self, tracker_url, my_port, peer_name="Anonymous"):
        self.tracker_url = tracker_url
        self.my_port = my_port
        self.my_ip = '127.0.0.1'  # Localhost for testing
        self.peer_name = peer_name
        self.peer_id = "{}:{}".format(self.my_ip, self.my_port)
        
        # WeApRous app for P2P server
        self.app = WeApRous()
        
        # Connected peers
        self.connected_peers = {}  # {peer_id: {"ip": ..., "port": ..., "name": ...}}
        
        # Message history
        self.messages = []
        
        # Setup P2P routes
        self.setup_routes()
        
        # Heartbeat thread
        self.running = True
        self.heartbeat_thread = None
    
    def setup_routes(self):
        """Setup P2P API routes using WeApRous"""
        
        @self.app.route('/connect-peer/', methods=['POST'])
        def connect_peer(headers="", body=""):
            """
            API for other peers to connect to this peer
            
            Request JSON: {"ip": "...", "port": ..., "peer_id": "...", "name": "..."}
            """
            try:
                data = json.loads(body) if body else {}
                peer_id = data.get('peer_id', '')
                peer_ip = data.get('ip', '')
                peer_port = data.get('port', 0)
                peer_name = data.get('name', 'Unknown')
                
                if peer_id and peer_id not in self.connected_peers:
                    self.connected_peers[peer_id] = {
                        'ip': peer_ip,
                        'port': peer_port,
                        'name': peer_name
                    }
                    print("\n[P2P] Peer connected: {} ({})".format(peer_name, peer_id))
                    print("[{}] > ".format(self.peer_name), end='')
                
                response_body = json.dumps({
                    'status': 'ok',
                    'message': 'Connected',
                    'peer_id': self.peer_id,
                    'name': self.peer_name
                })
                
                return (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(response_body), response_body)
                )
                
            except Exception as e:
                error_body = json.dumps({'error': str(e)})
                return (
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(error_body), error_body)
                )
        
        @self.app.route('/broadcast-peer/', methods=['POST'])
        def broadcast_peer(headers="", body=""):
            """
            Receive broadcast message from another peer
            
            Request JSON: {"from": "...", "name": "...", "msg": "...", "timestamp": ...}
            """
            try:
                data = json.loads(body) if body else {}
                from_peer = data.get('from', 'Unknown')
                from_name = data.get('name', 'Unknown')
                message = data.get('msg', '')
                timestamp = data.get('timestamp', time.time())
                
                # Store message
                self.messages.append({
                    'type': 'broadcast',
                    'from': from_peer,
                    'name': from_name,
                    'msg': message,
                    'timestamp': timestamp
                })
                
                # Display message
                print("\n[BROADCAST] {} ({}): {}".format(from_name, from_peer, message))
                print("[{}] > ".format(self.peer_name), end='')
                
                response_body = json.dumps({'status': 'received'})
                return (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(response_body), response_body)
                )
                
            except Exception as e:
                error_body = json.dumps({'error': str(e)})
                return (
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(error_body), error_body)
                )
        
        @self.app.route('/send-peer/', methods=['POST'])
        def send_peer(headers="", body=""):
            """
            Receive direct message from another peer
            
            Request JSON: {"from": "...", "name": "...", "msg": "...", "timestamp": ...}
            """
            try:
                data = json.loads(body) if body else {}
                from_peer = data.get('from', 'Unknown')
                from_name = data.get('name', 'Unknown')
                message = data.get('msg', '')
                timestamp = data.get('timestamp', time.time())
                
                # Store message
                self.messages.append({
                    'type': 'direct',
                    'from': from_peer,
                    'name': from_name,
                    'msg': message,
                    'timestamp': timestamp
                })
                
                # Display message
                print("\n[DIRECT] {} ({}): {}".format(from_name, from_peer, message))
                print("[{}] > ".format(self.peer_name), end='')
                
                response_body = json.dumps({'status': 'received'})
                return (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(response_body), response_body)
                )
                
            except Exception as e:
                error_body = json.dumps({'error': str(e)})
                return (
                    "HTTP/1.1 500 Internal Server Error\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: {}\r\n"
                    "\r\n"
                    "{}".format(len(error_body), error_body)
                )
    
    # ========================================
    # HTTP Client methods (talk to tracker)
    # ========================================
    
    def register_with_tracker(self):
        """Register this peer with the centralized tracker"""
        try:
            data = json.dumps({
                'ip': self.my_ip,
                'port': self.my_port,
                'peer_id': self.peer_id
            })
            
            req = urllib2.Request(
                self.tracker_url + '/submit-info/',
                data,
                {'Content-Type': 'application/json'}
            )
            
            response = urllib2.urlopen(req)
            result = json.loads(response.read())
            
            print("[Tracker] Registration successful: {}".format(result.get('message', 'OK')))
            return True
            
        except Exception as e:
            print("[Tracker] Registration failed: {}".format(e))
            return False
    
    def get_peer_list(self):
        """Get list of active peers from tracker"""
        try:
            req = urllib2.Request(self.tracker_url + '/get-list/')
            response = urllib2.urlopen(req)
            result = json.loads(response.read())
            
            peers = result.get('peers', [])
            print("[Tracker] Found {} peers".format(len(peers)))
            
            return peers
            
        except Exception as e:
            print("[Tracker] Failed to get peer list: {}".format(e))
            return []
    
    def send_heartbeat(self):
        """Send heartbeat to tracker to stay alive"""
        try:
            data = json.dumps({'peer_id': self.peer_id})
            req = urllib2.Request(
                self.tracker_url + '/heartbeat/',
                data,
                {'Content-Type': 'application/json'}
            )
            urllib2.urlopen(req)
        except:
            pass  # Silent fail for heartbeat
    
    def unregister_from_tracker(self):
        """Unregister from tracker when shutting down"""
        try:
            data = json.dumps({'peer_id': self.peer_id})
            req = urllib2.Request(
                self.tracker_url + '/remove/',
                data,
                {'Content-Type': 'application/json'}
            )
            urllib2.urlopen(req)
            print("[Tracker] Unregistered successfully")
        except Exception as e:
            print("[Tracker] Unregister failed: {}".format(e))
    
    # ========================================
    # P2P methods (talk to other peers)
    # ========================================
    
    def connect_to_peer(self, peer_ip, peer_port, peer_id):
        """Establish P2P connection with another peer"""
        try:
            data = json.dumps({
                'ip': self.my_ip,
                'port': self.my_port,
                'peer_id': self.peer_id,
                'name': self.peer_name
            })
            
            peer_url = "http://{}:{}".format(peer_ip, peer_port)
            req = urllib2.Request(
                peer_url + '/connect-peer/',
                data,
                {'Content-Type': 'application/json'}
            )
            
            response = urllib2.urlopen(req)
            result = json.loads(response.read())
            
            if result.get('status') == 'ok':
                self.connected_peers[peer_id] = {
                    'ip': peer_ip,
                    'port': peer_port,
                    'name': result.get('name', 'Unknown')
                }
                print("[P2P] Connected to peer: {} ({})".format(result.get('name'), peer_id))
                return True
            
        except Exception as e:
            print("[P2P] Failed to connect to {}: {}".format(peer_id, e))
            return False
    
    def discover_and_connect_peers(self):
        """Discover peers from tracker and connect to them"""
        peers = self.get_peer_list()
        
        for peer in peers:
            peer_id = peer.get('peer_id', '')
            
            # Don't connect to ourselves
            if peer_id == self.peer_id:
                continue
            
            # Don't reconnect if already connected
            if peer_id in self.connected_peers:
                continue
            
            # Connect to peer
            self.connect_to_peer(
                peer.get('ip'),
                peer.get('port'),
                peer_id
            )
    
    def broadcast_message(self, message):
        """Send broadcast message to all connected peers"""
        if not self.connected_peers:
            print("[P2P] No connected peers to broadcast to")
            return
        
        data = json.dumps({
            'from': self.peer_id,
            'name': self.peer_name,
            'msg': message,
            'timestamp': time.time()
        })
        
        success_count = 0
        for peer_id, peer_info in self.connected_peers.items():
            try:
                peer_url = "http://{}:{}".format(peer_info['ip'], peer_info['port'])
                req = urllib2.Request(
                    peer_url + '/broadcast-peer/',
                    data,
                    {'Content-Type': 'application/json'}
                )
                urllib2.urlopen(req)
                success_count += 1
            except Exception as e:
                print("[P2P] Failed to broadcast to {}: {}".format(peer_id, e))
        
        print("[P2P] Broadcast sent to {}/{} peers".format(success_count, len(self.connected_peers)))
    
    def send_direct_message(self, peer_id, message):
        """Send direct message to specific peer"""
        if peer_id not in self.connected_peers:
            print("[P2P] Peer {} not connected".format(peer_id))
            return False
        
        peer_info = self.connected_peers[peer_id]
        
        try:
            data = json.dumps({
                'from': self.peer_id,
                'name': self.peer_name,
                'msg': message,
                'timestamp': time.time()
            })
            
            peer_url = "http://{}:{}".format(peer_info['ip'], peer_info['port'])
            req = urllib2.Request(
                peer_url + '/send-peer/',
                data,
                {'Content-Type': 'application/json'}
            )
            urllib2.urlopen(req)
            
            print("[P2P] Direct message sent to {}".format(peer_id))
            return True
            
        except Exception as e:
            print("[P2P] Failed to send message to {}: {}".format(peer_id, e))
            return False
    
    # ========================================
    # Background tasks
    # ========================================
    
    def heartbeat_loop(self):
        """Background thread to send periodic heartbeats"""
        while self.running:
            time.sleep(30)  # Send heartbeat every 30 seconds
            if self.running:
                self.send_heartbeat()
    
    # ========================================
    # Console UI
    # ========================================
    
    def print_help(self):
        """Print available commands"""
        print("\n" + "=" * 60)
        print("Available commands:")
        print("  /help              - Show this help")
        print("  /peers             - List connected peers")
        print("  /discover          - Discover and connect to new peers")
        print("  /direct <peer_id> <msg>  - Send direct message")
        print("  /quit              - Exit application")
        print("  <message>          - Broadcast message to all peers")
        print("=" * 60 + "\n")
    
    def list_peers(self):
        """List connected peers"""
        if not self.connected_peers:
            print("\nNo connected peers")
        else:
            print("\nConnected peers ({})".format(len(self.connected_peers)))
            for peer_id, info in self.connected_peers.items():
                print("  - {} ({})".format(info.get('name', 'Unknown'), peer_id))
        print()
    
    def run_console(self):
        """Run interactive console for user input"""
        print("\n" + "=" * 60)
        print("Peer Console - Type /help for commands")
        print("=" * 60)
        
        while self.running:
            try:
                user_input = raw_input("[{}] > ".format(self.peer_name))
                
                if not user_input.strip():
                    continue
                
                if user_input == '/help':
                    self.print_help()
                
                elif user_input == '/peers':
                    self.list_peers()
                
                elif user_input == '/discover':
                    print("Discovering peers...")
                    self.discover_and_connect_peers()
                
                elif user_input.startswith('/direct '):
                    parts = user_input.split(' ', 2)
                    if len(parts) >= 3:
                        peer_id = parts[1]
                        message = parts[2]
                        self.send_direct_message(peer_id, message)
                    else:
                        print("Usage: /direct <peer_id> <message>")
                
                elif user_input == '/quit':
                    print("Shutting down...")
                    self.running = False
                    break
                
                else:
                    # Broadcast message
                    self.broadcast_message(user_input)
                
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                self.running = False
                break
            except EOFError:
                self.running = False
                break
    
    # ========================================
    # Main run method
    # ========================================
    
    def run(self):
        """Start the peer application"""
        print("=" * 60)
        print("Task 2: Peer Application Starting...")
        print("Peer Name: {}".format(self.peer_name))
        print("Peer ID: {}".format(self.peer_id))
        print("Listening on: {}:{}".format(self.my_ip, self.my_port))
        print("Tracker: {}".format(self.tracker_url))
        print("=" * 60)
        
        # Register with tracker
        if not self.register_with_tracker():
            print("Failed to register with tracker. Exiting...")
            return
        
        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        self.heartbeat_thread.setDaemon(True)
        self.heartbeat_thread.start()
        
        # Discover initial peers
        print("\nDiscovering peers...")
        self.discover_and_connect_peers()
        
        # Start P2P server in background thread
        def run_server():
            self.app.prepare_address('0.0.0.0', self.my_port)
            self.app.run()
        
        server_thread = threading.Thread(target=run_server)
        server_thread.setDaemon(True)
        server_thread.start()
        
        # Give server time to start
        time.sleep(1)
        
        # Run console UI
        try:
            self.run_console()
        finally:
            # Cleanup
            self.unregister_from_tracker()
            print("Goodbye!")


# ============================================
# Main entry point
# ============================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Peer Application',
        description='Task 2 - P2P Chat Peer',
        epilog='Hybrid P2P chat participant'
    )
    parser.add_argument('--tracker', required=True, help='Tracker URL (e.g., http://127.0.0.1:8000)')
    parser.add_argument('--port', type=int, required=True, help='Port for P2P server (e.g., 5001)')
    parser.add_argument('--name', default='Anonymous', help='Peer display name (e.g., Alice)')
    
    args = parser.parse_args()
    
    # Create and run peer
    peer = PeerApp(args.tracker, args.port, args.name)
    peer.run()
