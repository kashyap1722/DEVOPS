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

@app.route("/updateemp/<empid>", methods=['POST'])
def UpdateEmp(empid):
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    cursor = db_conn.cursor()
    update_sql = """
        UPDATE employee 
        SET first_name = %s, last_name = %s, pri_skill = %s, location = %s
        WHERE empid = %s
    """
    try:
        cursor.execute(update_sql, (first_name, last_name, pri_skill, location, empid))
        db_conn.commit()
        return f"Employee {empid} information updated successfully."
    except Exception as e:
        return f"Error updating employee information: {str(e)}"
    finally:
        cursor.close()

   @app.route("/deleteemp", methods=['POST'])
def DeleteEmp():
    empid = request.form['empid']  # Get the employee ID to delete
    cursor = db_conn.cursor()

    delete_sql = "DELETE FROM employee WHERE empid = %s"
    try:
        cursor.execute(delete_sql, (empid,))
        db_conn.commit()
        return f"Employee with ID {empid} deleted successfully."
    except Exception as e:
        return f"Error deleting employee: {str(e)}"
    finally:
        cursor.close()
<!-- UpdateEmpForm.html -->
<form method="POST" action="{{ url_for('process_update_emp', empid=data[0]) }}">
    <label for="empid">Employee ID</label>
    <input type="text" id="empid" name="empid" value="{{ data[0] }}" readonly>

    <label for="first_name">First Name</label>
    <input type="text" id="first_name" name="first_name" value="{{ data[1] }}">

    <label for="last_name">Last Name</label>
    <input type="text" id="last_name" name="last_name" value="{{ data[2] }}">

    <label for="pri_skill">Primary Skill</label>
    <input type="text" id="pri_skill" name="pri_skill" value="{{ data[3] }}">

    <label for="location">Location</label>
    <input type="text" id="location" name="location" value="{{ data[4] }}">

    <input type="submit" value="Update Information">
</form>



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
