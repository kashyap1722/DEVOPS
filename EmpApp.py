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

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    empid = request.form['empid']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    priskill = request.form['priskill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    # Ensure the employee image is uploaded
    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        insert_sql = "INSERT INTO employee (empid, firstname, lastname, priskill, location) VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (empid, firstname, lastname, priskill, location))
        db_conn.commit()

        emp_name = f"{firstname} {lastname}"

        # Upload image file to S3
        emp_image_file_name_in_s3 = f"emp-id-{empid}_image_file"
        s3 = boto3.resource('s3')
        print("Data inserted in MySQL RDS... uploading image to S3...")

        # Upload the image to the S3 bucket
        s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
        
        # Get the S3 bucket location
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        s3_location = bucket_location['LocationConstraint'] or ''
        object_url = f"https://s3{s3_location}.amazonaws.com/{custombucket}/{emp_image_file_name_in_s3}"

        # Update the employee record with the image URL
        update_sql = "UPDATE employee SET emp_image_url = %s WHERE empid = %s"
        cursor.execute(update_sql, (object_url, empid))
        db_conn.commit()

        print("All modifications done...")

    except Exception as e:
        return str(e)  # Handle exceptions by returning the error message

    finally:
        cursor.close()

    return render_template('AddEmpOutput.html', name=emp_name, object_url=object_url)



