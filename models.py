from extensions import db, socketio
from datetime import datetime
from sqlalchemy import event
# from timers import reset_or_create_timer

# Define the Events table model
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    eventtype = db.Column(db.String(80), nullable=False)
    timecreated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    timeupdated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """returns a dictionary representation of the event object"""
        return{
            'id': self.id,
            'eventtype': self.eventtype,
            'timecreated': self.timecreated.isoformat() if self.timecreated else None,
            'timeupdated': self.timeupdated.isoformat() if self.timeupdated else None,
        }
    
    def __repr__(self):
        return f"<Event {self.eventtype}>"

# Define the Status table model
class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(80), nullable=False)
    timecreated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    timeupdated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """returns a dictionary representation of the event object"""
        return{
            'id': self.id,
            'status': self.status,
            'timecreated': self.timecreated,
            'timeupdated': self.timeupdated,
        }
    def __repr__(self):
        return f"<Status {self.status}>"

# define the node model
class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """returns a dictionary representation of the event object"""
        return{
            # 'name': self.id,
            'name': self.location,
            'lon': self.longitude,
            'lat': self.latitude,
        }

    def __repr__(self):
        return f'<Node {self.location}>'
    
    
    

# Register a listener for new records
@event.listens_for(Event, 'after_insert')
def receive_after_insert(mapper, connection, target):
    # This event is triggered on a background thread.
    # Use the `socketio.emit()` from this context.
    socketio.emit('new_record', target.to_dict(), namespace='/')

# @event.listens_for(Status, 'after_insert')
# @event.listens_for(Status, 'after_update')
# def status_after_update(mapper, connection, target):
#     if target.id == 1:
#         print("Model listener triggered for Status ID 1.")
#         reset_or_create_timer(target.id)
#         socketio.emit('row_updated', target.to_dict(), namespace='/')