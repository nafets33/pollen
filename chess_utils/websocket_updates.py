from chess_utils.websocket_manager import manager
from chess_utils.conscience_utils import story_return
from chess_piece.pollen_db import PollenJsonEncoder
import json
import logging


async def send_story_grid_update(
    client_user: str,
    QUEEN_KING: dict,
    revrec: dict,
    toggle_view_selection: str = 'queen',
    qk_chessboard: dict = None
) -> bool:
    """
    Generate story grid data and send via WebSocket.
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        logging.info(f"🔄 Generating story grid for {client_user}...")
        
        # Ensure toggle_view_selection is a string
        if not isinstance(toggle_view_selection, str):
            toggle_view_selection = str(toggle_view_selection)
        
        # Generate story grid data
        df = story_return(
            QUEEN_KING=QUEEN_KING,
            revrec=revrec,
            toggle_view_selection=toggle_view_selection,
            qk_chessboard=qk_chessboard
        )
        
        if df is None:
            logging.error(f"❌ story_return() returned None for {client_user}")
            return False
        
        logging.info(f"✅ Generated {len(df)} rows for story grid")
        
        # Convert to row updates format
        row_updates = []
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            
            row_updates.append({
                'row_id': str(idx),
                'updates': row_dict
            })
        
        # Serialize with PollenJsonEncoder
        message = json.dumps(row_updates, cls=PollenJsonEncoder)
        
        # ✅ Critical: Replace NaN/Infinity strings in JSON output
        # Python's json.dumps() converts float('nan') to "NaN" which is invalid JSON
        # Maybe if we fix in RevRec first, but just in case, double-check here WORKERBEE
        message = message.replace(': NaN,', ': null,')
        message = message.replace(': NaN}', ': null}')
        message = message.replace(': Infinity,', ': null,')
        message = message.replace(': Infinity}', ': null}')
        message = message.replace(': -Infinity,', ': null,')
        message = message.replace(': -Infinity}', ': null}')
        
        logging.info(f"📦 Serialized message length: {len(message)} chars")
        logging.info(f"📤 Sending {len(row_updates)} updates to {client_user}...")
        
        # Send via WebSocket manager
        success = await manager.send_to_user(client_user, message)
        
        if success:
            logging.info(f"✅ Successfully sent {len(row_updates)} updates to {client_user}")
        else:
            logging.warning(f"⚠️  Failed to send updates to {client_user} (not connected?)")
        
        return success
        
    except Exception as e:
        logging.error(f"❌ Error sending story grid update: {e}")
        import traceback
        traceback.print_exc()
        return False