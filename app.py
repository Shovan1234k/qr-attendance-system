from flask import Flask, render_template, Response
import cv2
import csv
import os
from datetime import datetime
app = Flask(__name__)
csv_file = "attendance.csv"
image_folder = "static/students"
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Timestamp"])
scanned_ids = set()

def mark_attendance(student_id):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    if student_id not in scanned_ids:
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([student_id, timestamp])
        scanned_ids.add(student_id)
        print(f"✅ Marked {student_id} at {timestamp}")
    else:
        print(f"⚠️ {student_id} already marked")
def generate_frames():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        success, frame = cap.read()
        if not success:
            break

        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            mark_attendance(data)

            # Draw box and ID
            if bbox is not None:
                bbox = bbox.astype(int).reshape(-1, 2)
                for i in range(len(bbox)):
                    cv2.line(frame, tuple(bbox[i]), tuple(bbox[(i+1) % len(bbox)]),
                             (0, 255, 0), 2)
                cv2.putText(frame, data, (bbox[0][0], bbox[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Convert frame to JPEG for web
        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(debug=True)
