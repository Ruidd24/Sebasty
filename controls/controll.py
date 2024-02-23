# Import necessary libraries
from flask import Flask, render_template, request, Response
import RPi.GPIO as GPIO
import cv2
from camera import Camera  # Assuming you have a separate camera.py file for camera functionality
import time

app = Flask(__name__)

# Set up GPIO pins for motor control
# Adjust pin numbers based on your hardware configuration
left_motor_pin1 = 17
left_motor_pin2 = 18
right_motor_pin1 = 22
right_motor_pin2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(left_motor_pin1, GPIO.OUT)
GPIO.setup(left_motor_pin2, GPIO.OUT)
GPIO.setup(right_motor_pin1, GPIO.OUT)
GPIO.setup(right_motor_pin2, GPIO.OUT)

# Initialize the camera
camera = Camera()

# Function to move the robot forward
def move_forward():
    GPIO.output(left_motor_pin1, GPIO.HIGH)
    GPIO.output(left_motor_pin2, GPIO.LOW)
    GPIO.output(right_motor_pin1, GPIO.HIGH)
    GPIO.output(right_motor_pin2, GPIO.LOW)

# Function to move the robot backward
def move_backward():
    GPIO.output(left_motor_pin1, GPIO.LOW)
    GPIO.output(left_motor_pin2, GPIO.HIGH)
    GPIO.output(right_motor_pin1, GPIO.LOW)
    GPIO.output(right_motor_pin2, GPIO.HIGH)

# Function to turn the robot left
def turn_left():
    GPIO.output(left_motor_pin1, GPIO.LOW)
    GPIO.output(left_motor_pin2, GPIO.HIGH)
    GPIO.output(right_motor_pin1, GPIO.HIGH)
    GPIO.output(right_motor_pin2, GPIO.LOW)

# Function to turn the robot right
def turn_right():
    GPIO.output(left_motor_pin1, GPIO.HIGH)
    GPIO.output(left_motor_pin2, GPIO.LOW)
    GPIO.output(right_motor_pin1, GPIO.LOW)
    GPIO.output(right_motor_pin2, GPIO.HIGH)

# Function to stop the robot
def stop_robot():
    GPIO.output(left_motor_pin1, GPIO.LOW)
    GPIO.output(left_motor_pin2, GPIO.LOW)
    GPIO.output(right_motor_pin1, GPIO.LOW)
    GPIO.output(right_motor_pin2, GPIO.LOW)

# Route for the web kiosk interface
@app.route('/')
def index():
    return render_template('index.html')  # Create an HTML template for your web kiosk

# Route to handle robot control form submission
@app.route('/control', methods=['POST'])
def control():
    direction = request.form['direction']

    if direction == 'forward':
        move_forward()
    elif direction == 'backward':
        move_backward()
    elif direction == 'left':
        turn_left()
    elif direction == 'right':
        turn_right()
    elif direction == 'stop':
        stop_robot()

    return render_template('index.html')  # Redirect back to the main page

# Route for streaming video feed
def gen_frames():
    while True:
        frame = camera.get_frame()  # Get a frame from the camera
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Main program
if __name__ == '__main__':
    try:
        # Start the web server
        app.run(host='0.0.0.0', port=5000, debug=True)

    except KeyboardInterrupt:
        # Clean up GPIO on keyboard interrupt
        GPIO.cleanup()
