from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    empid = request.form.get('empid')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    pri_skill = request.form.get('pri_skill')
    location = request.form.get('location')
    emp_image_file = request.files.get('emp_image_file')

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if not emp_image_file or emp_image_file.filename == "":
        return "Please select a file"

    try:
        cursor.execute(insert_sql, (empid, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"

        # Upload image file to S3
        emp_image_file_name_in_s3 = f"emp-id-{empid}_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = bucket_location['LocationConstraint']

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = f"-{s3_location}"

            object_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{emp_image_file_name_in_s3}"

        except Exception as e:
            return f"Error uploading to S3: {str(e)}"

    except Exception as db_error:
        return f"Database Error: {str(db_error)}"

    finally:
        cursor.close()

    print("All modifications done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    if request.method == 'POST':  # When someone submits the form
        empid = request.form['empid']  # Get the employee ID from the form
        cursor = db_conn.cursor()  # Start a connection to the database

        # SQL query to find the employee
        query = "SELECT * FROM employee WHERE empid = %s"
        try:
            cursor.execute(query, (empid,))  # Execute the query with the given empid
            record = cursor.fetchone()  # Get the first result (if any)

            if record:  # If we find an employee
                emp_data = {
                    "Employee ID": record[0],
                    "First Name": record[1],
                    "Last Name": record[2],
                    "Primary Skill": record[3],
                    "Location": record[4],
                }
                return render_template('GetEmpOutput.html', data=emp_data)  # Show details
            else:  # If no employee is found
                return "Employee not found."
        except Exception as e:  # Catch any errors
            return f"Error: {str(e)}"
        finally:
            cursor.close()  # Close the database connection
    else:  # If someone just opens the page without submitting
        return render_template('GetEmp.html')  # Show the form to enter an employee ID

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
