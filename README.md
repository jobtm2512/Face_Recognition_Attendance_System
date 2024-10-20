# Face Recognition Attendance System

This project is a web-based face recognition attendance system built using Flask, OpenCV, and MySQL. It allows users to register new employees, log attendance through face recognition, and generate attendance reports for specific events.

## Features

- **Employee Registration**: Capture employee details along with a short video for face embedding extraction.
- **Face Recognition**: Use face embeddings to recognize employees and log attendance.
- **Event-Based Attendance**: Log attendance for specific events and generate reports for event participation.
- **Date Filtering**: Filter attendance records by date range for better analysis.
- **Attendance Export**: Download attendance data as an Excel sheet.
- **Real-Time Attendance Logging**: Automatically log attendance when a face is detected and matched with a registered user.
- **Secure Connection**: The app runs on HTTPS with SSL encryption.

## Technologies Used

- **Flask**: Backend framework for web routing and API endpoints.
- **OpenCV**: For processing video and capturing frames.
- **face_recognition**: Library used for face detection and recognition.
- **MySQL**: Database to store user details, face embeddings, and attendance records.
- **Pandas**: Used to handle data and export attendance records to Excel.
- **imageio**: For reading video files in memory.
- **FPDF**: For generating PDF reports (optional).
- **HTML/CSS**: Frontend interface for user interaction.

## Installation and Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/face-recognition-attendance.git
    cd face-recognition-attendance
    ```

2. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up MySQL Database:
    - Create a new MySQL database named `face_recognition_system`.
    - Create the necessary tables:

    ```sql
    CREATE TABLE users (
        emp_id VARCHAR(255) PRIMARY KEY,
        emp_name VARCHAR(255),
        department VARCHAR(255),
        designation VARCHAR(255),
        joining_date DATE
    );

    CREATE TABLE face_embeddings (
        emp_id VARCHAR(255),
        embedding BLOB,
        FOREIGN KEY (emp_id) REFERENCES users(emp_id)
    );

    CREATE TABLE attendance (
        attendance_id INT AUTO_INCREMENT PRIMARY KEY,
        emp_id VARCHAR(255),
        attendance_time TIMESTAMP,
        event_id INT,
        FOREIGN KEY (emp_id) REFERENCES users(emp_id)
    );

    CREATE TABLE events (
        event_id INT AUTO_INCREMENT PRIMARY KEY,
        event_name VARCHAR(255)
    );
    ```

4. Update the MySQL credentials in `app.py`:

    ```python
    connection = mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="face_recognition_system"
    )
    ```

5. Run the application:

    ```bash
    python app.py
    ```

6. Access the application in your browser:

    ```
    https://localhost:5000
    ```

## Usage

1. **Register New Users**:
   - Go to `/new-user` and fill in the employee details along with a short video of the employee turning their head from side to side. The system will extract face embeddings from the video and store them in the database.

2. **Log Attendance**:
   - Go to `/log_attendance` and select an event. The system will capture a face image using the webcam and log the attendance if the face is recognized.

3. **View Attendance**:
   - Go to `/select_event` to view or download attendance records filtered by event and date range.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) library by Adam Geitgey.
- [OpenCV](https://opencv.org/) library for computer vision tasks.
- Flask community for providing such a lightweight and powerful web framework.

