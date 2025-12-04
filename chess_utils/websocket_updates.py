from chess_utils.websocket_manager import manager
from chess_piece.pollen_db import PollenJsonEncoder
import json
import logging


async def send_story_grid_update(
    client_user: str,
    prod: bool,
    revrec: dict,
    toggle_view_selection: str = 'queen',
    # qk_chessboard: dict = None
) -> bool:
    """
    Generate story grid data and send via WebSocket.
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        logging.info(f"🔄 Generating story grid for {client_user}...prod: {prod}")
        
        # Ensure toggle_view_selection is a string
        if not isinstance(toggle_view_selection, str):
            toggle_view_selection = str(toggle_view_selection)
        
        list_of_dict = revrec.get('storygauge', None)

        if list_of_dict is None:
            logging.error(f"❌ story_return() returned None for {client_user}")
            return False

        # Convert to row updates format
        row_updates = []
        for idx, row_dict in enumerate(list_of_dict):
            idx = row_dict.get('symbol', idx)  # Use 'row_id' if available
            row_updates.append({
                'row_id': str(idx),
                'updates': row_dict
            })
        
        # Serialize with PollenJsonEncoder
        message = json.dumps(row_updates, cls=PollenJsonEncoder)
        
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
        success = await manager.send_to_user(client_user, message, prod)
        
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