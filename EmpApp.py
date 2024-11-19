from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Simulated employee data (replace with a database in a real app)
employee_data = {}

@app.route('/addemp', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Retrieve employee data from the form
        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        emp_image_file = request.files['emp_image_file']
        
        # Save the employee data (simulated)
        employee_data[emp_id] = {
            'emp_id': emp_id,
            'first_name': first_name,
            'last_name': last_name,
            'pri_skill': pri_skill,
            'location': location,
            'emp_image_file': emp_image_file.filename if emp_image_file else None
        }

        # Save the image (if provided)
        if emp_image_file:
            image_path = os.path.join('static', 'images', emp_image_file.filename)
            emp_image_file.save(image_path)
        
        # Return to the success page with employee name
        name = f"{first_name} {last_name}"
        return render_template('AddEmpOutput.html', name=name)

    return render_template('AddEmp.html')

@app.route('/getemp', methods=['GET'])
def get_employee():
    # For simplicity, let's show all employees. In a real app, you'd retrieve this from a database.
    employee_list = []
    for emp_id, emp_info in employee_data.items():
        employee_list.append({
            'emp_id': emp_info['emp_id'],
            'name': f"{emp_info['first_name']} {emp_info['last_name']}",
            'skills': emp_info['pri_skill'],
            'location': emp_info['location'],
            'image': emp_info['emp_image_file']
        })
    
    # Render employee information in a new page
    return render_template('EmployeeList.html', employee_list=employee_list)

if __name__ == '__main__':
    app.run(debug=True)
