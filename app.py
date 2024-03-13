import hashlib
import logging
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import relationship
from flask import Flask,  render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class user(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password

class client(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    number = db.Column(db.String(100))
    deleted = db.Column(db.Boolean, default=False, index=True)
    total_price = db.Column(db.String(1000), default="0.00")
    tasks = relationship("project", back_populates="client")
    
    def __init__(self, name, email, number):
        self.name = name
        self.email = email
        self.number = number
        





class Employee(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(100))
    projects = relationship("project", secondary='project_employee', back_populates="employees")

    def __init__(self, name, role):
        self.name = name
        self.role = role

# Define association table for many-to-many relationship between projects and employees
project_employee = db.Table('project_employee',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True)
)
        

class project(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(500))
    description = db.Column(db.String(500), nullable=True)
    created_on = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, default=0.00) 
    status = db.Column(db.Boolean, default=False, index=True)
    price_paid = db.Column(db.Float, default=0.00)  # Convert to Float
    advance_paid = db.Column(db.Float, default=0.00)
    deleted = db.Column(db.Boolean, default=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    client = relationship("client", back_populates="tasks")
    subtasks = relationship("subtask", back_populates="task")
    employees = relationship("Employee", secondary='project_employee', back_populates="projects")

    

    def __init__(self,  title, description, price, created_on,  client_id):
        self.title = title
        self.description = description
        self.price = price
        self.client_id = client_id
        self.created_on = created_on

class subtask(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    description = db.Column(db.String(500), nullable=True)
    created_on = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    task = relationship("project", back_populates="subtasks")

    def __init__(self, created_on, title, description, task_id):
        self.title = title
        self.created_on = created_on
        self.description = description
        self.task_id =  task_id

class passwordManager(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    app = db.Column(db.String(500))
    extradetail = db.Column(db.String(500))
    password = db.Column(db.String(500))
    deleted = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500), nullable=True)

    def __init__(self, app, password):
        self.app = app
        self.password = password
        
class license (db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    app = db.Column(db.String(500))
    extradetail = db.Column(db.String(500))
    license = db.Column(db.String(500))
    deleted = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(500), nullable=True)

    def __init__(self, app, license):
        self.app = app
        self.license = license

with app.app_context():
    db.create_all()

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='app.log', level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)









# routes



# clients
@app.route('/client_list')
def client_list():
    
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    clients = client.query.filter_by(deleted = False).all()
    task_counts = {}
    total_price_pending_per_client = {}
    total_price_earned_per_client = {}

    for client_item in clients:
        pending_tasks_count = project.query.filter_by(client_id=client_item._id, status=False).count()
        completed_tasks_count = project.query.filter_by(client_id=client_item._id, status=True).count()
        total_tasks_count = project.query.filter_by(client_id=client_item._id).count()
        
        task_counts[client_item._id] = (pending_tasks_count, completed_tasks_count)
        
        client_tasks = project.query.filter_by(client_id=client_item._id).all()
        total_pending_price = sum(float(task_item.price) - (float(task_item.advance_paid) + float(task_item.price_paid)) for task_item in client_tasks)
        
        total_price_pending_per_client[client_item._id] = total_pending_price
        
        # Calculate total price earned for each client
        total_price_earned = sum(float(task_item.advance_paid) + float(task_item.price_paid) for task_item in client_tasks)
        total_price_earned_per_client[client_item._id] = total_price_earned


    return render_template('client_list.html', clients=clients, task_counts=task_counts,total_tasks_count = total_tasks_count, total_price_pending_per_client =  total_price_pending_per_client, total_price_earned_per_client = total_price_earned_per_client)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        new_client = client(name=name, email=email, number=number)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('client_list'))
    return render_template('add_client.html')

@app.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    search_client = client.query.get_or_404(int(client_id))
    if request.method == 'POST':
        search_client.name = request.form['name']
        search_client.email = request.form['email']
        search_client.number = request.form['number']
        db.session.commit()
        return redirect(url_for('client_list'))
    return render_template('edit_client.html', client=search_client)

@app.route('/add_task/<int:client_id>', methods=['GET', 'POST'])
def add_task(client_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        new_task = project(title=title, description=description, price=price, client_id=client_id, created_on=datetime.datetime.now())
        db.session.add(new_task)
        
        client_search = client.query.get_or_404(client_id)
        client_search.total_price=float(client_search.total_price) + float(price)
        db.session.commit()

        return redirect(url_for('client_list'))
    return render_template('add_task.html', client_id=client_id)

@app.route('/task_list')
def task_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    tasks_list = project.query.filter_by(deleted=False).order_by(project.client_id).all()
    leftPerTask = {}
    for tasks in tasks_list:
        leftPerTask[tasks._id] = float(tasks.price) - (float(tasks.advance_paid)+float(tasks.price_paid))
    return render_template('task_list.html', tasks=tasks_list, leftPerTask = leftPerTask)

@app.route('/client_tasks/<int:client_id>')
def client_tasks(client_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    client_item = client.query.get_or_404(client_id)
    leftPerTask = {}
    client_tasks = [task for task in client_item.tasks if not task.deleted]  # Filter out deleted tasks

    for task in client_tasks:
        leftPerTask[task._id] = float(task.price) - (float(task.advance_paid) + float(task.price_paid))

    return render_template('client_tasks.html', client=client_item, tasks=client_tasks, leftPerTask=leftPerTask)


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    edit_task = project.query.get_or_404(task_id)
    clients = client.query.all()
    
    if request.method == 'POST':
        original_price = float(edit_task.price)
        
        edit_task.title = request.form['title']
        edit_task.description = request.form['description']
        edit_task.price = request.form['price']
        edit_task.advance_paid = request.form['advance_paid']
        edit_task.price_paid = request.form['price_paid']
        
        edit_task.status = True if 'status' in request.form else False
        
        price_difference = float(edit_task.price) - original_price
        
        associated_client = client.query.get_or_404(int(edit_task.client_id))
        if associated_client:
            associated_client.total_price = float(associated_client.total_price) + price_difference
        
        db.session.commit()
        
        return render_template('edit_task.html', task=edit_task, clients=clients)
        
    return render_template('edit_task.html', task=edit_task, clients=clients)


@app.route('/completed_projects')
def completed_projects():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    completed_projects = project.query.filter_by(status=True, deleted=False).all()
    leftPerTask = {}
    for tasks in completed_projects:
        leftPerTask[tasks._id] = float(tasks.price) - (float(tasks.advance_paid)+float(tasks.price_paid))
    
    
    return render_template('completed_projects.html', completed_projects=completed_projects, leftPerTask=leftPerTask)

@app.route('/pending_projects')
def pending_projects():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    pending_projects_list = project.query.filter_by(status=False, deleted=False).all()
    leftPerTask = {}
    for task in pending_projects_list:
        leftPerTask[task._id] = float(task.price) - (float(task.advance_paid)+float(task.price_paid))
    
    return render_template('pending_projects.html', pending_projects=pending_projects_list, leftPerTask=leftPerTask)


@app.route('/deleted_projects')
def deleted_projects():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    deleted_projects_list = project.query.filter_by( deleted=True).all()
    leftPerTask = {}
    for task in deleted_projects_list:
        leftPerTask[task._id] = float(task.price) - (float(task.advance_paid)+float(task.price_paid))
    
    return render_template('deleted_projects.html', deleted_projects=deleted_projects_list, leftPerTask=leftPerTask)




@app.route('/delete_project/<int:task_id>', methods=['POST'])
def delete_project(task_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    project_to_delete = project.query.get_or_404(task_id)
    project_to_delete.deleted = True
    db.session.commit()
    return redirect(url_for('task_list'))

@app.route('/restore_project/<int:task_id>', methods=['POST'])
def restore_project(task_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    project_to_delete = project.query.get_or_404(task_id)
    project_to_delete.deleted = False
    db.session.commit()
    return redirect(url_for('task_list'))



@app.route('/subtask/<int:task_id>/subtasks')
def view_subtasks(task_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    tasks = project.query.get_or_404(task_id)
    subtasks = subtask.query.filter_by(task_id=task_id).all()
    return render_template('view_subtasks.html', task=tasks, subtasks=subtasks)

@app.route('/add_subtask/<int:task_id>', methods=['GET', 'POST'])
def add_subtask(task_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_subtask = subtask(title=title, description=description, task_id=task_id, created_on = datetime.datetime.now())
        db.session.add(new_subtask)
        db.session.commit()
        return redirect(url_for('task_list'))
    return render_template('add_subtask.html', task_id=task_id)

@app.route('/delete_subtask/<int:subtask_id>', methods=['POST'])
def delete_subtask(subtask_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    subtask_to_delete = subtask.query.get_or_404(subtask_id)
    subtask_to_delete.deleted = True
    db.session.commit()
    return redirect(url_for('task_list'))

@app.route('/edit_subtask/<int:subtask_id>', methods=['GET', 'POST'])
def edit_subtask(subtask_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    edit_subtask = subtask.query.get_or_404(subtask_id)
    if request.method == 'POST':
        edit_subtask.title = request.form['title']
        edit_subtask.description = request.form['description']
        db.session.commit()
        return redirect(url_for('task_list'))
    return render_template('edit_subtask.html', subtask=edit_subtask)

@app.route('/passwords')
def password_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    passwords = passwordManager.query.filter_by( deleted=False).all()
    return render_template('password_list.html', passwords=passwords)

@app.route('/add_password', methods=['GET', 'POST'])
def add_password():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        app_name = request.form['app']
        password = request.form['password']
        # encoded_pass = hashlib.sha256(password.encode()).hexdigest()
        new_password = passwordManager(app=app_name, password=password)
        db.session.add(new_password)
        db.session.commit()
        return redirect(url_for('password_list'))
    return render_template('add_password.html')

@app.route('/edit_password/<int:password_id>', methods=['GET', 'POST'])
def edit_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    edit_password = passwordManager.query.get_or_404(password_id)
    if request.method == 'POST':
        edit_password.app = request.form['app']
        edit_password.password = request.form['password']
        db.session.commit()
        return render_template('edit_password.html', password=edit_password)
    return render_template('edit_password.html', password=edit_password)

@app.route('/delete_password/<int:password_id>', methods=['POST'])
def delete_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    password_to_delete = passwordManager.query.get_or_404(password_id)
    password_to_delete.deleted = True
    db.session.commit()
    return redirect(url_for('password_list'))

@app.route('/restore_password/<int:password_id>', methods=['POST'])
def restore_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    password_to_delete = passwordManager.query.get_or_404(password_id)
    password_to_delete.deleted = False
    db.session.commit()
    return redirect(url_for('deleted_password_list'))


@app.route('/deleted_password_list')
def deleted_password_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    passwords = passwordManager.query.filter_by( deleted=True).all()
    return render_template('deleted_password_list.html', passwords=passwords)



@app.route('/license')
def license_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    licenses = license.query.filter_by( deleted=False).all()
    return render_template('license_list.html', licenses=licenses)

@app.route('/add_license', methods=['GET', 'POST'])
def add_license():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        app_name = request.form['app']
        password = request.form['license']
        new_license = license(app=app_name, license=password)
        print(new_license)
        db.session.add(new_license)
        db.session.commit()
        return redirect(url_for('license_list'))
    return render_template('add_license.html')

@app.route('/edit_license/<int:license_id>', methods=['GET', 'POST'])
def edit_license(license_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    edit_license = license.query.get_or_404(license_id)
    if request.method == 'POST':
        edit_license.app = request.form['app']
        edit_license.license = request.form['license']
        db.session.commit()
        return render_template('edit_license.html', license=edit_license)
    return render_template('edit_license.html', license=edit_license)

@app.route('/delete_license/<int:license_id>', methods=['POST'])
def delete_license(license_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    license_to_delete = license.query.get_or_404(license_id)
    license_to_delete.deleted = True
    db.session.commit()
    return redirect(url_for('license_list'))


@app.route('/restore_license/<int:license_id>', methods=['POST'])
def restore_license(license_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    password_to_delete = license.query.get_or_404(license_id)
    password_to_delete.deleted = False
    db.session.commit()
    return redirect(url_for('deleted_license_list'))


@app.route('/deleted_license_list')
def deleted_license_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    passwords = license.query.filter_by( deleted=True).all()
    return render_template('deleted_license_list.html', licenses=passwords)




#                   Employee




@app.route('/employee_list')
def employee_list():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    employees = Employee.query.all()
    projects_per_employee = {}
    
    # Calculate the number of projects for each employee
    for employee in employees:
        projects_per_employee[employee._id] = len(employee.projects)
    return render_template('employee_list.html', employees=employees, projects_per_employee=projects_per_employee)


@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        new_employee = Employee(name=name, role=role)
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('employee_list'))
    return render_template('add_employee.html')

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    edit_employee = Employee.query.get_or_404(employee_id)
    if request.method == 'POST':
        edit_employee.name = request.form['name']
        edit_employee.role = request.form['role']
        db.session.commit()
        return redirect(url_for('employee_list'))
    return render_template('edit_employee.html', employee=edit_employee)

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    employee_to_delete = Employee.query.get_or_404(employee_id)
    db.session.delete(employee_to_delete)
    db.session.commit()
    return redirect(url_for('employee_list'))

@app.route('/assign_project/<int:project_id>', methods=['GET', 'POST'])
def assign_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        proj = project.query.get_or_404(project_id)
        # Get the list of employee IDs sent from the form
        selected_employee_ids = [int(emp_id) for emp_id in request.form.getlist('employees') if emp_id]
        # Remove employees not selected from the project
        for employee in proj.employees:
            if employee._id not in selected_employee_ids:
                proj.employees.remove(employee)
        # Add new employees selected from the form to the project
        for employee_id in selected_employee_ids:
            employee = Employee.query.get_or_404(employee_id)
            if employee not in proj.employees:
                proj.employees.append(employee)
        db.session.commit()
        return redirect(url_for('task_list'))
    else:
        proj = project.query.get_or_404(project_id)
        employees = Employee.query.all()
        return render_template('assign_project.html', project=proj, employees=employees)





@app.route('/remove_employee/<int:project_id>/<int:employee_id>', methods=['POST'])
def remove_employee(project_id, employee_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    project = Project.query.get_or_404(project_id)
    employee = Employee.query.get_or_404(employee_id)
    project.employees.remove(employee)
    db.session.commit()
    return redirect(url_for('edit_project', project_id=project_id))


@app.route('/employees_dashboard/<int:employee_id>')
def employees_dashboard(employee_id):
    if 'user_id' not in session:
        return redirect(url_for('show_login'))

    # Query the database to get the employee's information
    employee = Employee.query.get_or_404(employee_id)

    # Get the employee's associated projects
    projects = employee.projects

    # Calculate the required statistics
    total_price_earned = sum(project.price_paid + project.advance_paid for project in projects)
    total_num_projects = len(projects)
    num_completed_projects = sum(1 for project in projects if project.status)
    num_pending_projects = total_num_projects - num_completed_projects

    # Pass the statistics to the template
    return render_template('employees_dashboard.html',
                           employee=employee,
                           total_price_earned=total_price_earned,
                           total_num_projects=total_num_projects,
                           num_completed_projects=num_completed_projects,
                           num_pending_projects=num_pending_projects)
    
    
    
    













# user 

# Dashboard

@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    num_clients = client.query.filter_by(deleted=False).count()
    num_projects = project.query.filter_by(deleted=False).count()
    
    # Total money earned (sum of total_price in client table)
    total_money_earned = (
        db.session.query(func.sum(project.price_paid + project.advance_paid))  # Assuming deleted is a boolean column
        .scalar()
    )
    pending_money = (
        db.session.query(func.sum(project.price - (project.price_paid + project.advance_paid)))  # Assuming deleted is a boolean column
        .scalar()
    )


    return render_template('dashboard.html',
        num_clients=num_clients,
        num_projects=num_projects,
        total_money_earned=total_money_earned,
        pending_money=pending_money)










# Login Signup

@app.route('/registerUser', methods=['GET', 'POST'])
def registerUser():
    if 'user_id' not in session:
        return redirect(url_for('show_login'))
    if request.method == 'POST':
        
        # Get data from form
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check whether username already exists or not
        users = user.query.filter_by(username=username).first()
        if users:
            flash("Username already exists.", "error")
            return redirect(url_for('registerUser'))

        # Create a new admin user
        new_user = user(
            name=name,
            username=username,
            password=hashlib.sha256(password.encode()).hexdigest(),
            email=email
        )

        db.session.add(new_user)
        db.session.commit()


        return redirect(url_for('show_login'))
    else:
        return render_template('registerUser.html')






# Route for displaying the login form
@app.route('/adminLogin', methods=['GET'])
def show_login():
    return render_template('AdminLogin.html')


# Login
@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        users = user.query.filter_by(
            username=username,
            password=hashlib.sha256(password.encode()).hexdigest()
        ).first()

        if users:
            session.clear()
            session['user_id'] = users._id
            session['username'] = users.username

            if remember_me:
                session.permanent = True
            else:
                session.permanent = False

            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please try again.")
            return redirect(url_for('show_login'))
    else:
        return render_template('adminLogin.html')












# logout

@app.route('/logout')
def logout():
    session.clear()
    return render_template('adminLogin.html')

if __name__ =="__main__":
    app.run()
