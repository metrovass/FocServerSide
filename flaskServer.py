# # from FocServerside import create_app
# from flask import Flask, request, jsonify, render_template
# import pandas as pd
# from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
# from river.anomaly import OneClassSVM
# from river import compose, linear_model, preprocessing, stream
# from river.anomaly import OneClassSVM
# from threading import Lock
# import io
# from routes.routes import main_bp  # Import the blueprint
# from extensions import db, socketio  # Import the db object from the new extensions file
# from models import Event, Status
# from config import Config
# from timers import reset_or_create_timer


# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Initialize extensions with the application
#     db.init_app(app)
#     socketio.init_app(app)

#     # Configure for a SQLite database named 'site.db'
#     # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#     # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

#     # Register the blueprint
#     app.register_blueprint(main_bp)


#     # Initialize the online model
#     # We use a pipeline to handle both scaling and the classifier
#     #online_model = preprocessing.StandardScaler() | linear_model.PAClassifier(C=0.1)
#     online_model = compose.Pipeline(
#         preprocessing.StandardScaler(),
#         linear_model.PAClassifier(C=0.1)
#     )

#     # A lock to prevent race conditions during model updates
#     model_lock = Lock()

    

#     def warm_up_model(csv_file):
#         """
#         Trains the online model on the entire historical CSV dataset.
#         This runs only once when the server starts.
#         """
#         try:
#             print(f"Loading and training online model with {csv_file}...")

#             # Define the converters for your specific column types
#             converters = {
#                 'timestamp': str, # river will handle this as a string, but it's often ignored for ML
#                 'temperature': int,
#                 'humidity': int,
#                 'vibration_amplitude': float,
#                 'vibration_frequency': float,
#                 'sound_amplitude': float,
#                 'sound_frequency': float,
#                 'event_type': int # Assuming 0 for normal, 1 for anomaly
#             }

#             # Read the CSV using pandas to handle string-to-int mapping
#             df = pd.read_csv(csv_file)
            
#             # Map 'intrusion' to 1 and 'normal' to 0
#             label_mapping = {'normal': 0, 'intrusion': 1}
#             df['event_type'] = df['event_type'].map(label_mapping)

#             # Use river's stream.iter_pandas to stream the data from the DataFrame
#             dataset = stream.iter_pandas(
#                 df,
#                 target_name='event_type'
#             )


#             with model_lock:
#                 for x, y in dataset:
#                     # 'x' will be a dictionary of features, 'y' will be the label
#                     # Exclude the timestamp from the features used for training
#                     x.pop('timestamp', None)
#                     online_model.learn_one(x, y)
            
#             print("Online model warmed up successfully.")
#         except FileNotFoundError:
#             print(f"Error: CSV file '{csv_file}' not found. The model will start untrained.")
#         except Exception as e:
#             print(f"Error during model warm-up: {e}")

#     @app.route('/predict', methods=['POST'])
#     def predict():
#         if not request.is_json:
#             return jsonify({"status": "Error", "message": "Request must be JSON"}), 400
#             #return request.get_data
        
#         raw_data = request.get_json()

#         # Create a new dictionary to hold the cleaned numeric data
#         data = {}
        
#         for key, value in raw_data.items():
#             try:
#                 # Attempt to convert the value to a float
#                 data[key] = float(value)
#             except (ValueError, TypeError):
#                 # Handle cases where conversion fails, such as with
#                 # missing or non-numeric data.
#                 # You can decide to:
#                 # 1. Provide a default value
#                 # cleaned_x_dict[key] = 0.0
#                 # 2. Skip the problematic feature
#                 print(f"Warning: Could not convert '{value}' for feature '{key}'. Skipping.")
#                 continue # Continue to the next item


#         # Ensure the received data has the correct format and features
#         # Adjust this check to match your actual sensor data
#         required_features = ['temperature', 'humidity', 'vibration_amplitude', 'vibration_frequency', 'sound_amplitude', 'sound_frequency']
#         if not all(feature in data for feature in required_features):
#             return jsonify({"status": "Error", "message": "Missing required features in JSON"}), 400
#             #return data

#         # Convert data to River's format (dictionary)
#         x_dict = {key: value for key, value in data.items() if key in required_features}

#         # Perform prediction with the current state of the online model
#         with model_lock:
#             prediction_value = online_model.predict_one(x_dict)
        
#         # In this online learning scenario, the model learns from every new piece of data.
#         # A true online training would need a ground truth label, but we can assume
#         # the online model's prediction is used as a pseudo-label for continued adaptation.
#         # NOTE: This is a simplified approach. In production, a more robust labeling strategy
#         # or a semi-supervised algorithm might be needed.
        
#         # For demonstration, we'll train the model on the new data point
#         # using the online model's own prediction as a pseudo-label.
#         # This keeps the model adapting, though it's susceptible to confirmation bias.
#         with model_lock:
#             online_model.learn_one(x_dict, prediction_value)

#         online_result = "Anomaly" if prediction_value == 1 else "Normal"
        
#         if online_result == "Anomaly":
#             # Create new Event instance
#             response_message = "Online model detected a potential intrusion!"
        
            
#             try:
#                 new_event = Event(eventtype='intrusion')

#                 # Add both instances to the session
#                 db.session.add(new_event)

#                 # Commit the transaction to save the records to the database
#                 db.session.commit()

#                 # Return a success response
#                 return jsonify({"status": online_result, "message": response_message,
#                                 'event_id': new_event.id,}), 201
            
            
#             except Exception as e:
#                 db.session.rollback()  # Roll back the session in case of an error
#                 return jsonify({'error': f'An error occurred: {str(e)}'}), 500
        
#         else:
#             response_message = "Online model detected normal activity."
        
#         print(f"Received data: {data}. Online prediction: {online_result}. Online model trained.")
        
#         return jsonify({"status": online_result, "message": response_message}), 200

#     @app.route("/")
#     @app.route("/index")
#     def index():
#         # return render_template("index.html", access_token=MAPBOX_ACCESS_TOKEN)
#         return render_template("index.html")

#     # Route to handle POST requests for sending offline intrusion alert
#     @app.route('/alert', methods=['POST'])
#     def create_entry():
#         data = request.get_json()  # Get JSON data from the request body

#         # Extract data for the event
#         event_type = data.get('eventtype')

#         # Basic validation
#         if not event_type:
#             return jsonify({'error': 'Missing data in request'}), 400

#         try:
#             # Create new Event instance
#             new_event = Event(eventtype=event_type)

#             # Add both instances to the session
#             db.session.add(new_event)

#             # Commit the transaction to save the records to the database
#             db.session.commit()

#             # Return a success response
#             return jsonify({'message': 'New Event created successfully!',
#                             'event_id': new_event.id,}), 201
#         except Exception as e:
#             db.session.rollback()  # Roll back the session in case of an error
#             return jsonify({'error': f'An error occurred: {str(e)}'}), 500


#     # @app.route('/status/<int:status_id>', methods=['PUT'])
#     # def update_status(status_id):
#     #     """Updates an existing status record."""
#     #     data = request.get_json()
#     #     status_id = data.get('id')
#     #     new_status_text = data.get('status')
        
#     #     if not status_id or not new_status_text:
#     #         return jsonify({'error': 'Missing id or status in request'}), 400
        
#     #     try:
#     #         # Check if the record already exists
#     #         status = Event.query.get(status_id)
            
#     #         if status:
#     #             # Record exists, so update it
#     #             status.status = new_status_text
#     #             db.session.commit()
#     #             message = f"Status with id {status_id} updated successfully."
#     #             status_code = 200
#     #         else:
#     #             # Record does not exist, so insert a new one
#     #             new_status = Status(id=status_id, status=new_status_text)
#     #             db.session.add(new_status)
#     #             db.session.commit()
#     #             message = f"New event with id {status_id} created successfully."
#     #             status_code = 201
                
#     #         return jsonify({'message': message, 'data': status.to_dict() if status else new_status.to_dict()}), status_code
            
#     #     except Exception as e:
#     #         db.session.rollback()
#     #         return jsonify({'error': str(e)}), 500

#     @app.route('/status', methods=['POST'])
#     def update_status():
#         if not request.is_json:
#             return jsonify({"error": "Request must be JSON"}), 415 # Unsupported Media Type

#         data = request.get_json()
#         new_status = data.get('status')

#         if new_status is None:
#             return jsonify({"error": "Missing 'status' in JSON data"}), 400

#         # Find the record with the first ID (primary key 1)
#         status_record = Status.query.get(1)
#         reset_or_create_timer(status_record.id)

#         # If the record doesn't exist, create it
#         if not status_record:
#             status_record = Status(status=new_status)
#             db.session.add(status_record)
#             db.session.commit()
#             socketio.emit('row_updated', status_record.to_dict(), namespace='/')
#             return jsonify({"message": "Created new status record", "record": status_record.to_dict()}), 201


#         # Check if the new status is different from the current status
#         if status_record.status != new_status:
#             # Update the existing record if the status is different
#             status_record.status = new_status
#             db.session.commit()
#             socketio.emit('row_updated', status_record.to_dict(), namespace='/')
#             return jsonify({"message": "Updated existing status record", "record": status_record.to_dict()}), 200
#         else:
#             # Do nothing if the status is the same
#             return jsonify({"message": "Status has not changed, no update needed", "record": status_record.to_dict()}), 200
        
        


#     # This block is used to create the database and tables
#     # It must be run within an application context
#     def create_database():
#         with app.app_context():
#             # from . import models
#             db.create_all()
#             print("Database and tables created successfully!")

#     # Initial model training with the exported_FOC_data CSV
#     warm_up_model('exported_FOC_data.csv')
#     #create the database
#     create_database()
            
#     return app

# app = create_app()

# if __name__ == '__main__':
#     # Initial model training with the exported_FOC_data CSV
#     # warm_up_model('exported_FOC_data.csv')
#     #create the database
#     # create_database()
#     socketio.run(app, host='192.168.171.48', port=5000, debug=True)