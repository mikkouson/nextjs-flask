from flask import Flask, jsonify
from supabase import create_client, Client
import websocket
import json
import os
from dotenv import load_dotenv
import threading

load_dotenv()

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def on_message(ws, message):
    print("Received message:", message)
    # Process the real-time update here
    try:
        data = json.loads(message)
        # Handle different types of updates (insert, update, delete)
        print(f"Event type: {data.get('event')}")
        print(f"Payload: {data.get('payload')}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### WebSocket Connection Closed ###")

def on_open(ws):
    print("WebSocket Connection Opened")
    
    # Subscribe to the inventory table
    subscribe_msg = {
        "event": "phx_join",
        "topic": "realtime:public:inventory",
        "payload": {},
        "ref": "1"
    }
    ws.send(json.dumps(subscribe_msg))

def start_websocket():
    # Construct WebSocket URL
    ws_url = SUPABASE_URL.replace('https://', 'wss://').replace('http://', 'ws://') + '/realtime/v1/websocket'
    
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        ws_url,
        header={"apikey": SUPABASE_KEY},
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.run_forever()

@app.route('/api/predict', methods=['GET'])
def get_inventory():
    try:
        # Fetch data from the 'inventory' table
        response = supabase.table("inventory").select("*").execute()
        
        # Check if data was retrieved
        if not response.data:
            return jsonify({"error": "No data found in the inventory table"}), 404
        
        # Return the data as JSON
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start WebSocket in a separate thread
    websocket_thread = threading.Thread(target=start_websocket, daemon=True)
    websocket_thread.start()
    
    # Run Flask app
    app.run(debug=True)