import threading
from extensions import db, socketio
from models import Status

# A global timer object that can be accessed and controlled from different parts of the application
# Use a dictionary to manage multiple timers if needed, using the row ID as a key.
timers = {}
TIMEOUT_SECONDS = 60000  # 20 seconds

def trigger_timeout_event(row_id):
    """
    This function is executed when the timer expires.
    It emits a SocketIO event to all connected clients.
    """

    try:
        # Retrieve the specific row to update
        row_to_update = Status.query.get(row_id)
        if row_to_update:
            row_to_update.status = 'offline'
            db.session.commit()
            print(f"Status for row {row_id} updated to 'offline'.")
        else:
            print(f"Error: Row with id {row_id} not found.")
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Database update failed for row {row_id}: {e}")
    finally:
        # The context manager `with` will handle closing the session,
        # but it is good practice to be aware of the process.
        pass
    print(f"Timer for row {row_id} expired! Emitting 'timeout_event'.")
    socketio.emit('timeout_event', {'id': row_id}, namespace='/')
    # Clean up the timer reference
    del timers[row_id]

def reset_or_create_timer(row_id):
    """
    Resets the timer if it exists, otherwise creates a new one.
    """
    if row_id in timers and timers[row_id].is_alive():
        print(f"Resetting timer for row {row_id}")
        timers[row_id].cancel()
    
    new_timer = threading.Timer(TIMEOUT_SECONDS, trigger_timeout_event, args=[row_id])
    new_timer.start()
    timers[row_id] = new_timer
    print(f"Timer for row {row_id} started/reset.")