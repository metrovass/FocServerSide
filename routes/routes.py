from flask import Blueprint, render_template,  request, jsonify
from datetime import datetime
from models import Event, Status, Node, db
from sqlalchemy import text

# Create a Blueprint object named 'main'
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@main_bp.route("/index")
def index():
	return render_template("index.html")

@main_bp.route('/intrusion', methods=['GET'])
def get_all_events():
    """Fetches all events from the database."""
    events = Event.query.all()  # Retrieve all events from the database
    statuses = Status.query.all() # Retrieve all statuses from the database
    events_list = [event.to_dict() for event in events]
    return jsonify(events_list), 200

@main_bp.route('/statustable', methods=['GET'])
def get_all_status():
    """Fetches all events from the database."""
    status = Status.query.first()
    # status_list = [status.to_dict() for status in status]
    # return jsonify(status_list), 200
    return jsonify(status.to_dict())

@main_bp.route('/node', methods=['GET'])
def get_all_nodes():
    """Fetches all events from the database."""
    node = Node.query.all()
    node_list = [node.to_dict() for node in node]
    return jsonify(node_list), 200

@main_bp.route('/api/data')
def get_map_data():

    nodes = Node.query.all()

    # Convert the list of Node objects into a list of dictionaries
    data = [node.to_dict() for node in nodes]
    # Dummy data for coordinates
    # data = [
    #     {"lat": 9.533005815133118, "lon": 6.450099048962754, "name": "Node 2"},
    #     {"lat": 9.534229827853, "lon": 6.4515594912953835, "name": "Node 3"},
    #     {"lat": 9.53541398047955, "lon": 6.451769062011862, "name": "Node 4"},
    #     {"lat": 9.534403984071034, "lon": 6.452680413387654, "name": "Node 5"},
    # ]
    return jsonify(data)

@main_bp.route('/submit-node', methods=['POST'])
def submit_node():
    data = request.json
    location = data.get('location')
    longitude = data.get('longitude')
    latitude = data.get('latitude')

    if not all([location, longitude, latitude]):
        return jsonify({'success': False, 'message': 'All fields are required!'}), 400

    try:
        new_node = Node(location=location, longitude=float(longitude), latitude=float(latitude))
        db.session.add(new_node)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Node added successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
@main_bp.route('/truncate_table')
def clear_table():
    try:
        # Delete all rows from the MyTable model
        num_rows_deleted = db.session.query(Node).delete()
        # Commit the changes to the database
        db.session.commit()
        return f'{num_rows_deleted} rows have been deleted from MyTable.'
    except Exception as e:
        db.session.rollback()
        return f'An error occurred: {e}'
    
@main_bp.route('/api/events', methods=['GET'])
def get_events():
    # events = Event.query.all()
    events = Event.query.order_by(Event.timecreated.desc()).all()
    events_data = [event.to_dict() for event in events]
    return jsonify(events_data)

@main_bp.route('/admin/clear-database', methods=['POST'])
# @login_required # Ensure only logged-in users can access this (improve with role checking if necessary)
def clear_database():
    # Optional: Add extra security checks (e.g., check if user has admin role)
    # if not current_user.is_admin:
    #     abort(403) 

    try:
        # Drop all tables defined in your models
        db.drop_all()
        # Recreate the tables (optional, but useful to start fresh)
        db.create_all()
        
        # flash("All database tables have been dropped and recreated.", "success")
        # return redirect(url_for('main.index')) # Redirect to a safe page
        return "All database tables have been dropped and recreated."
        
    except Exception as e:
        # flash(f"An error occurred: {str(e)}", "danger")
        # return redirect(url_for('main.index'))
        return "An error occured."