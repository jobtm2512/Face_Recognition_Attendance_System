import cv2
import face_recognition
import numpy as np
import mysql.connector
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
import base64
import io
from PIL import Image
import imageio
from io import BytesIO
import pandas as pd
from io import BytesIO
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

# Connect to the MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jobtmmysql2512",
    database="face_recognition_system"
)
cursor = connection.cursor()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/new-user", methods=["GET", "POST"])
def register_new_user():
    if request.method == "POST":
        # Gather form data
        emp_id = request.form.get("emp_id")
        emp_name = request.form.get("name")
        department = request.form.get("deptname")
        designation = request.form.get("designation")
        joining_date = request.form.get("join_date")
        video_data = request.form.get("video_data")

        embeddings = []

        if video_data:
            try:
                # Decode the base64-encoded video data
                video_bytes = base64.b64decode(video_data.split(',')[1])
                video_io = BytesIO(video_bytes)  # Create an in-memory byte stream

                # Use imageio to read video from memory
                reader = imageio.get_reader(video_io, format='webm')

                embeddings = []
                for frame in reader:
                    if len(embeddings) >= 10:
                        break
                    
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)
                    
                    for face_location in face_locations:
                        face_encoding = face_recognition.face_encodings(rgb_frame, [face_location])[0]
                        embeddings.append(face_encoding.tobytes())

                        # Check if 10 embeddings have been collected
                        if len(embeddings) >= 10:
                            break

            except Exception as e:
                print(f"Error processing video: {e}")
                flash("Error processing video. Please try again.", "error")
                return redirect(url_for('register_new_user'))

        # Insert user data and embeddings into the database
        try:
            # Insert user data
            insert_user_query = """
            INSERT INTO users (emp_name, emp_id, department, designation, joining_date)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_user_query, (emp_name, emp_id, department, designation, joining_date))
            
            # Insert face embeddings
            for embedding_blob in embeddings:
                insert_embedding_query = """
                INSERT INTO face_embeddings (emp_id, embedding)
                VALUES (%s, %s)
                """
                cursor.execute(insert_embedding_query, (emp_id, embedding_blob))
            
            # Commit the transaction
            connection.commit()
            print(f"User {emp_id} and {len(embeddings)} embeddings registered successfully!")
            flash("User registered successfully!", "success")
        except mysql.connector.Error as err:
            print(f"Error inserting user data: {err}")
            flash("Database error occurred. Please try again.", "error")
            connection.rollback()  # Rollback the transaction in case of error
        
        return redirect(url_for('home'))
    
    return render_template("register.html")

@app.route('/select_event', methods=['GET', 'POST'])
def select_event():
    cursor = connection.cursor()
    cursor.execute("SELECT event_id, event_name FROM events")  # Fetch events from the database
    events = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        # Get selected event IDs, event names, and date range
        selected_event_ids = request.form.getlist('event_ids')  # List of selected event IDs
        selected_event_names = request.form.getlist('event_names')  # List of selected event names
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')

        # Initialize the query and parameters
        query = """
            SELECT 
                u.emp_id,
                u.emp_name,
                a.attendance_time,
                e.event_name
            FROM 
                users u
            JOIN 
                attendance a ON u.emp_id = a.emp_id
            JOIN 
                events e ON a.event_id = e.event_id
            WHERE 1=1
        """
        params = []

        # Apply filters based on what the user has selected
        if selected_event_ids:
            query += " AND e.event_id IN ({})".format(','.join(['%s'] * len(selected_event_ids)))
            params.extend(selected_event_ids)

        if selected_event_names:
            query += " AND e.event_name IN ({})".format(','.join(['%s'] * len(selected_event_names)))
            params.extend(selected_event_names)

        if from_date and to_date:
            query += " AND DATE(a.attendance_time) BETWEEN %s AND %s"
            params.extend([from_date, to_date])

        # If no filters are provided, return all data (optional)
        if not selected_event_ids and not selected_event_names and not (from_date and to_date):
            return render_template('view_attendance.html', events=events, data=[])

        cursor = connection.cursor()
        cursor.execute(query, tuple(params))  # Execute the query with the appropriate parameters
        attendance_data = cursor.fetchall()
        cursor.close()

        # Convert fetched data to a DataFrame for download
        df = pd.DataFrame(attendance_data, columns=['Employee ID', 'Employee Name', 'Date and Time', 'Event Name'])

        # Generate Excel File
        if 'download_excel' in request.form:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            return send_file(output, download_name="attendance_data.xlsx", as_attachment=True)

        return render_template('view_attendance.html', events=events, data=attendance_data)

    return render_template('view_attendance.html', events=events)


@app.route('/log_attendance', methods=['GET', 'POST'])
def log_attendance():
    if request.method == 'GET':
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT event_id, event_name FROM events")
            events = cursor.fetchall()  # Fetch all rows
            cursor.close()  # Close the cursor after fetching
            print(f"Fetched events: {events}")
        except mysql.connector.Error as err:
            print(f"Error fetching events: {err}")
            return jsonify({'success': False, 'message': 'Database error while fetching events'})

        return render_template('attendance.html', events=events)

    elif request.method == 'POST':
        try:
            # Process image data and event_id
            data = request.json
            image_data = data.get('image', '').split(',')[1]
            event_id = data.get('event_id')
            if not image_data or not event_id:
                return jsonify({'success': False, 'message': 'Missing data'})

            # Decode image data
            image_data = base64.b64decode(image_data)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Detect face and compute embedding
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return jsonify({'success': False, 'message': 'No face detected'})

            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

            # Reset session to avoid unread result errors
            connection.reset_session()

            # Fetch all registered users
            cursor = connection.cursor()
            cursor.execute("SELECT emp_id, embedding FROM face_embeddings")
            registered_users = cursor.fetchall()  # Fetch all rows
            cursor.close()  # Close the cursor after fetching
            print(f"Fetched {len(registered_users)} registered users")

            if not registered_users:
                return jsonify({'success': False, 'message': 'No registered users'})

            # Compare captured face with registered faces
            matched_emp_id = None
            for emp_id, embedding_blob in registered_users:
                registered_face_encoding = np.frombuffer(embedding_blob, dtype=np.float64)
                if face_recognition.compare_faces([registered_face_encoding], face_encoding, tolerance=0.4)[0]:
                    matched_emp_id = emp_id
                    break

            if not matched_emp_id:
                return jsonify({'success': False, 'message': 'Face not recognized'})

            # Check attendance
            cursor = connection.cursor()
            cursor.execute("""
                SELECT attendance_time FROM attendance 
                WHERE emp_id = %s AND event_id = %s AND attendance_time > %s
            """, (matched_emp_id, event_id, datetime.now() - timedelta(hours=12)))
            attendance_check = cursor.fetchone()
            cursor.close()

            if attendance_check:
                return jsonify({'success': False, 'message': 'Already marked for this event!'})

            # Log attendance
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO attendance (emp_id, attendance_time, event_id)
                VALUES (%s, CURRENT_TIMESTAMP, %s)
            """, (matched_emp_id, event_id))
            connection.commit()
            cursor.close()

            return jsonify({'success': True, 'emp_id': matched_emp_id})

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            return jsonify({'success': False, 'message': f'Database error: {err}'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('cert.pem', 'key.pem'))

