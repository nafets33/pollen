import requests
import json
import os
import time
from datetime import datetime
import random
import sys
import websocket

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chess_piece.queen_hive import init_queenbee
from chess_piece.pollen_db import PollenJsonEncoder

# Configuration
API_URL = "http://127.0.0.1:8000"  # Your FastAPI server
API_KEY = os.getenv('fastAPI_key', 'your_api_key_here')
CLIENT_USER = "stefanstapinski@gmail.com"

def test_trigger_story_grid_update():
    """
    Test triggering story grid update via WebSocket.
    This simulates what Queen Bee does when revrec refreshes.
    """
    
    print("=" * 80)
    print("🧪 Testing Story Grid WebSocket Update")
    print("=" * 80)
    
    # Load Queen Bee data
    print("📦 Loading Queen Bee data...")
    qb = init_queenbee(
        client_user=CLIENT_USER, 
        prod=False, 
        revrec=True, 
        queen_king=True, 
        pg_migration=True
    )
    
    revrec = qb.get('revrec')
    QUEEN_KING = qb.get('QUEEN_KING')

    # ✅ Modify BEFORE converting to dict
    print("🔧 Modifying SPY current_ask to 89 for testing...")
    if 'SPY' in revrec['storygauge'].index:
        revrec['storygauge'].at['SPY', 'current_ask'] = 89
        revrec['storygauge'].at['SPY', 'ticker_total_budget'] = 89
        print(f"   SPY current_ask set to: {revrec['storygauge'].at['SPY', 'current_ask']}")
    elif 'symbol' in revrec['storygauge'].columns:
        revrec['storygauge'].loc[revrec['storygauge']['symbol'] == 'SPY', 'current_ask'] = 89
        spy_row = revrec['storygauge'][revrec['storygauge']['symbol'] == 'SPY']
        if not spy_row.empty:
            print(f"   SPY ticker_total_budget set to: {spy_row.iloc[0]['ticker_total_budget']}")
            print(f"   SPY current_ask set to: {spy_row.iloc[0]['current_ask']}")
    
    print(f"✅ Loaded QUEEN_KING and revrec")
    
    # Convert DataFrames to dicts for JSON serialization
    revrec_for_ws = {
        'storygauge': revrec['storygauge'].to_dict('records') if 'storygauge' in revrec else [],
        'waveview': revrec['waveview'].to_dict('records') if 'waveview' in revrec else [],
        **{k: v for k, v in revrec.items() if k not in ['storygauge', 'waveview']}
    }
    
    # Verify SPY modification made it into the dict
    spy_record = next((r for r in revrec_for_ws['storygauge'] if r.get('symbol') == 'SPY'), None)
    if spy_record:
        print(f"✅ Verified: SPY current_ask in payload = {spy_record.get('current_ask')}")
    
    # Prepare payload
    payload = {
        'client_user': CLIENT_USER,
        'api_key': API_KEY,
        'QUEEN_KING': QUEEN_KING,
        'revrec': revrec_for_ws,
        'toggle_view_selection': 'queen',
        'qk_chessboard': None
    }
    
    # ✅ Try the endpoint (note: NO /api/data prefix in URL since router already has it)
    endpoint = f"{API_URL}/api/data/trigger_story_grid_update"
    
    print(f"\n📤 Sending update trigger to: {endpoint}")
    print(f"👤 Client User: {CLIENT_USER}")
    print(f"📊 Storygauge Rows: {len(revrec_for_ws['storygauge'])}")
    print(f"📊 Waveview Rows: {len(revrec_for_ws['waveview'])}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Send HTTP POST with PollenJsonEncoder
        response = requests.post(
            endpoint,
            data=json.dumps(payload, cls=PollenJsonEncoder),
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 404:
            print(f"❌ 404 NOT FOUND")
            print(f"💡 The endpoint might not exist. Check your fastapi_router.py")
            print(f"\nTrying to list available endpoints...")
            
            # Try to get OpenAPI docs
            try:
                docs_response = requests.get(f"{API_URL}/docs")
                if docs_response.status_code == 200:
                    print(f"✅ FastAPI docs available at: {API_URL}/docs")
                    print(f"   Check there for available endpoints")
            except:
                pass
            
            return False
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"💬 Message: {result.get('message')}")
            
            if result.get('status') == 'success':
                print(f"\n🎉 SUCCESS! Story grid update sent via WebSocket")
                print(f"✅ Check your Streamlit app (http://localhost:8501) for updates")
                print(f"🔍 Look for SPY with current_ask = 89")
                return True
            elif result.get('status') == 'warning':
                print(f"\n⚠️  WARNING: {result.get('message')}")
                print(f"💡 Connected users: {result.get('connected_users', [])}")
                print(f"💡 Make sure:")
                print(f"   1. Streamlit app is running on http://localhost:8501")
                print(f"   2. Grid has WebSocket connection established")
                print(f"   3. User '{CLIENT_USER}' is connected")
                return False
            else:
                print(f"\n❌ ERROR: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️  TIMEOUT: Request took longer than 15 seconds")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Could not connect to {API_URL}")
        print(f"💡 Make sure FastAPI server is running!")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_continuous_updates(num_updates=5, delay=3):
    """
    Test sending multiple updates in sequence.
    Simulates Queen Bee sending updates every few seconds.
    """
    print("\n" + "=" * 80)
    print(f"🔄 Testing Continuous Updates ({num_updates} updates, {delay}s delay)")
    print("=" * 80)
    
    for i in range(num_updates):
        print(f"\n📡 Update {i+1}/{num_updates}")
        success = test_trigger_story_grid_update()
        
        if success:
            print(f"✅ Update {i+1} sent successfully")
        else:
            print(f"❌ Update {i+1} failed")
        
        if i < num_updates - 1:
            print(f"\n⏳ Waiting {delay} seconds before next update...")
            time.sleep(delay)
    
    print("\n" + "=" * 80)
    print("✅ Continuous update test complete")
    print("=" * 80)


def check_websocket_connection():
    """
    Check if WebSocket endpoint is available.
    """
    print("\n" + "=" * 80)
    print("🔌 Checking WebSocket Endpoint")
    print("=" * 80)
    
    ws_url = API_URL.replace('http://', 'ws://') + '/api/data/ws_story'
    print(f"WebSocket URL: {ws_url}")
    
    try:
        ws = websocket.create_connection(ws_url)
        
        # Send handshake
        ws.send(json.dumps({
            'username': CLIENT_USER,
            'toggle_view_selection': 'queen',
            'api_key': API_KEY
        }))
        
        # Wait for confirmation
        result = ws.recv()
        print(f"✅ WebSocket connected!")
        print(f"Response: {result}")
        
        ws.close()
        return True
        
    except ImportError:
        print("⚠️  'websocket-client' not installed")
        print("Install with: pip install websocket-client")
        return False
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Story Grid WebSocket Updates')
    parser.add_argument('--url', default='http://127.0.0.1:8000', help='FastAPI server URL')
    parser.add_argument('--user', default='stefanstapinski@gmail.com', help='Client user email')
    parser.add_argument('--continuous', action='store_true', help='Run continuous updates')
    parser.add_argument('--num', type=int, default=5, help='Number of continuous updates')
    parser.add_argument('--delay', type=int, default=3, help='Delay between updates (seconds)')
    parser.add_argument('--check-ws', action='store_true', help='Check WebSocket connection')
    
    args = parser.parse_args()
    
    # Update globals
    API_URL = args.url
    CLIENT_USER = args.user
    
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                  Story Grid WebSocket Test Script                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

📍 FastAPI URL: {API_URL}
👤 Client User: {CLIENT_USER}
📊 Streamlit: http://localhost:8501
    """)
    
    # Check WebSocket if requested
    if args.check_ws:
        check_websocket_connection()
        print()
    
    # Run tests
    if args.continuous:
        test_continuous_updates(num_updates=args.num, delay=args.delay)
    else:
        test_trigger_story_grid_update()
    
    print("\n" + "=" * 80)
    print("🏁 Test Complete")
    print("=" * 80)
    print("""
Next Steps:
1. Check Streamlit app at http://localhost:8501
2. Look for console messages: "📥 Received X row updates"
3. Verify grid updated with new data
4. Check FastAPI logs for WebSocket activity
    """)