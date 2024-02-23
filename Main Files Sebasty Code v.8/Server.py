from flask import Flask, render_template, request, redirect, url_for, Response, flash, jsonify
from neuralintents import BasicAssistant
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
# import RPi.GPIO as GPIO
import cv2

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///survey1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'survey_secret'

db = SQLAlchemy(app)

class Survey1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225))
    There_Department = db.Column(db.String(50))
    There_TDepartment = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    suggestion = db.Column(db.Text)
    srating = db.Column(db.Integer)

camera = cv2.VideoCapture(0)

assistant = BasicAssistant('answer.json')

assistant.fit_model(epochs=50)
assistant.save_model()

# # Comment this part

# left_motor_pin1 = 17
# left_motor_pin2 = 18
# right_motor_pin1 = 22
# right_motor_pin2 = 23

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(left_motor_pin1, GPIO.OUT)
# GPIO.setup(left_motor_pin2, GPIO.OUT)
# GPIO.setup(right_motor_pin1, GPIO.OUT)
# GPIO.setup(right_motor_pin2, GPIO.OUT)

# # Function to move the robot forward
# def move_forward():
#     GPIO.output(left_motor_pin1, GPIO.HIGH)
#     GPIO.output(left_motor_pin2, GPIO.LOW)
#     GPIO.output(right_motor_pin1, GPIO.HIGH)
#     GPIO.output(right_motor_pin2, GPIO.LOW)

# # Function to move the robot backward
# def move_backward():
#     GPIO.output(left_motor_pin1, GPIO.LOW)
#     GPIO.output(left_motor_pin2, GPIO.HIGH)
#     GPIO.output(right_motor_pin1, GPIO.LOW)
#     GPIO.output(right_motor_pin2, GPIO.HIGH)

# # Function to turn the robot left
# def turn_left():
#     GPIO.output(left_motor_pin1, GPIO.LOW)
#     GPIO.output(left_motor_pin2, GPIO.HIGH)
#     GPIO.output(right_motor_pin1, GPIO.HIGH)
#     GPIO.output(right_motor_pin2, GPIO.LOW)

# # Function to turn the robot right
# def turn_right():
#     GPIO.output(left_motor_pin1, GPIO.HIGH)
#     GPIO.output(left_motor_pin2, GPIO.LOW)
#     GPIO.output(right_motor_pin1, GPIO.LOW)
#     GPIO.output(right_motor_pin2, GPIO.HIGH)

# # Function to stop the robot
# def stop_robot():
#     GPIO.output(left_motor_pin1, GPIO.LOW)
#     GPIO.output(left_motor_pin2, GPIO.LOW)
#     GPIO.output(right_motor_pin1, GPIO.LOW)
#     GPIO.output(right_motor_pin2, GPIO.LOW)
# # hanggang dto


@app.route('/')
def index():
    return render_template('Login.html')

def calculate_total_average_rate():
    with app.app_context():
        total_average_rate = db.session.query(func.avg(Survey1.rating)).scalar()
    return total_average_rate

def Admin_index():
    # Calculate total rate per target department
    total_department_rates = db.session.query(Survey1.There_TDepartment, func.avg(Survey1.rating)).group_by(Survey1.There_TDepartment).all()
    
    # Calculate total rate of school
    total_school_rate = db.session.query(func.avg(Survey1.srating)).scalar()

    # Calculate total average rate
    total_average_rate = calculate_total_average_rate()
    
    # Fetch all surveys for the separate table
    survey_results = Survey1.query.all()
    
    return render_template('Admin.html', total_department_rates=total_department_rates, total_school_rate=total_school_rate, total_average_rate=total_average_rate, survey_results=survey_results)

@app.route("/send_message", methods=["POST"])
def send_message():
    # Get the message from the request data
    message = request.form["message"]
    
    # Process the message using the assistant
    response = assistant.process_input(message)
    
    # Return the response
    return jsonify({"response": response})

# Camera settings
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/survey', methods=['GET', 'POST'])
def formsurvey():
    if request.method == 'POST':
        name = request.form['name']
        There_Department = request.form['There_Department']
        There_TDepartment = request.form['There_TDepartment']
        rating = request.form['department_rating']
        suggestion = request.form['suggestion']
        srating = request.form['schoolrating']
        
        with app.app_context():
            new_survey = Survey1(name=name,There_Department=There_Department,There_TDepartment=There_TDepartment,rating=rating,suggestion=suggestion,srating=srating)
            db.session.add(new_survey)
            db.session.commit()
        
        flash('Survey submitted successfully', 'success')
        return render_template('Sebastyui.html')
    return render_template('Sebastyui.html')

@app.route('/admin')
def admin():
    sort_by = request.args.get('sort_by', 'id')
    if sort_by not in ['id', 'name', 'There_Department', 'There_TDepartment', 'rating', 'suggestion','srating']:
        sort_by = 'id'
    surveys = Survey1.query.order_by(sort_by).all()
    return render_template('Admin.html', surveys=surveys)

@app.route('/delete/<int:id>')
def delete(id):
    survey = Survey1.query.get_or_404(id)
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_all', methods=['POST'])
def delete_all():
    Survey1.query.delete()
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'Sebasty' and password == '12345':
        return redirect(url_for('admin'))
    elif username == 'Sebastyui' and password == '1233':
       return redirect(url_for('SEBASTYINDEX'))
    elif username == 'ControlsSebastyUI' and password == '123':
       return redirect(url_for('ControlsSebastyUI'))
    else:
        return render_template('Login.html', message='Invalid username or password. Please try again.')


@app.route('/SEBASTYINDEX')
def SEBASTYINDEX():
    return render_template('SEBASTYINDEX.html')

@app.route('/SebastyUI')
def SebastyUI():
    return render_template('Sebastyui.html')
  
@app.route('/ControlsSebastyUI')
def ControlsSebastyUI():
    return render_template('Controls.html')

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
