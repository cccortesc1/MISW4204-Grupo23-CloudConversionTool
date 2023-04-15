from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource
from flask import request
from datetime import timedelta
from ..model import db, User, UserSchema, Task, TaskSchema, UserSignupSchema, UserLoginSchema
from ..tasks import convert_file
import os

user_schema = UserSchema()
task_schema = TaskSchema()
signup_schema = UserSignupSchema()

upload_folder = './upload'
download_folder = './download'

class SignupView(Resource):
    def post(self):
        try:
            # Obtenemos el request body y lo deserializamos con Marshmallow
            data = signup_schema.load(request.json)
            
            # Verificamos si ya existe un usuario con el mismo username o email
            if User.query.filter_by(username=data['username']).first():
                return {"message": "Username already exists"}, 409
            elif User.query.filter_by(email=data['email']).first():
                return {"message": "Email already exists"}, 409
            
            # Verificamos que las contraseñas coincidan
            if data['password1'] != data['password2']:
                return {"message": "Passwords don't match"}, 400
            
            # Creamos el usuario a partir de los datos obtenidos
            user = User(
                username=data['username'],
                email=data['email'],
                password=data['password1']
            )
            
            # Si todo está bien, creamos el usuario y lo guardamos en la base de datos
            db.session.add(user)
            db.session.commit()
            return {"message": "User created successfully"}, 200
        except ValidationError as e:
            return {"message": e.messages}, 400
        
class LoginView(Resource):
    def post(self):
        try:
            # Obtenemos el request body y lo deserializamos con Marshmallow
            login_data = UserLoginSchema().load(request.json, session=db.session)
            user = User.query.filter_by(username=login_data.username).first()
            
            # Si no se emcuentra el usuario o la contraseña es incorrecta se devuelve un error
            if not user:
                return {"message": "User not found"}, 404
            
            if user.password != login_data.password:
                return {"message": "Incorrect password"}, 401
            
            # Si todo es correcto se crea un token jwt
            access_token = create_access_token(identity=user.username, expires_delta=timedelta(hours=2))
            return {"access_token": access_token}, 200
            
        except ValidationError as e:
            return {"message": e.messages}, 400


class UserListView(Resource):
    @jwt_required()
    def get(self):
        return [user_schema.dump(user) for user in User.query.all()]
    
class TaskView(Resource):
    @jwt_required()
    def get(self, id_task):
        return task_schema.dump(Task.query.get_or_404(id_task))
    
    @jwt_required()
    def delete(self, id_task):
        # Obtener la tarea que se quiere eliminar
        task = Task.query.get_or_404(id_task)

        # Borrarla de la base de datos
        db.session.delete(task)
        db.session.commit()
        
        return '',204

class TaskListView(Resource):
    @jwt_required()
    def get(self):
        # Se obtiene el usuario que está logueado
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username).first()

        # Obtener los parámetros de la solicitud en caso de que sean enviados
        max_results = request.args.get('max', default=None, type=int)
        order_by = request.args.get('order', default=None, type=int)

        # Construir una nueva consulta a partir de la relación 'tasks' del usuario
        tasks_query = db.session.query(Task).filter(Task.user == user.id)
        
        # Ordenar las tareas según el parámetro order_by
        if order_by is not None:
            tasks_query = tasks_query.order_by(Task.id.asc() if order_by == 0 else Task.id.desc())
        
        # Filtrar la cantidad de resultados según el parámetro max_results
        if max_results is not None:
            tasks_query = tasks_query.limit(max_results)
        
        # Ejecutar la consulta y devolver las tareas serializadas
        tasks = tasks_query.all()

        return [task_schema.dump(tasks, many=True)]
    
    @jwt_required()
    def post(self):
        # Se obtiene el usuario que está logueado
        current_username = get_jwt_identity()
        user = User.query.filter_by(username=current_username).first()

        # Se cargan los valores de ka ruta del archivo y la nueva extensión 
        file = request.json["fileName"]
        new_format = request.json["newFormat"]
        
        # A partir de los valores establecidos se crea el path
        file_path = os.path.join(upload_folder, file)

        # Se crea la nueva tarea en base de datos
        new_task = Task(fileName=file, newFormat=new_format)
        new_task.user = user.id
        db.session.add(new_task)
        db.session.commit()

        # Se encola la tarea
        task = convert_file.delay(file_path, new_format)

        return 'Tarea creada exitosamente', 201
    
class FileView(Resource):
    @jwt_required()
    def get(self, filename):
        return 'Coming soon you would have ' + filename, 200