from flask import Flask, request, make_response, jsonify, session, redirect, url_for, send_from_directory
from flask_restful import Api, Resource
from flask_cors import CORS
from server.config import Config
# from server.config import Config
from server.extensions import db, ma  # Import extensions from extensions.py
# from server.extensions import db, ma  # Import extensions from extensions.py
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from flask_migrate import Migrate
from marshmallow import ValidationError
from collections import defaultdict
from server.models import Landlord, Tenant, RentalBuilding, PropertyType, Payment, LandlordSchema, PropertyTypeSchema, RentalBuildingSchema
import re
# from server.models import Landlord, Tenant, RentalBuilding, PropertyType  # or whatever your models are

# from flask import send_from_directory andlordSchema


load_dotenv()
import os

# Initialize Flask app
app = Flask(__name__)
# app = Flask(__name__, static_folder='../client/build', static_url_path='/')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# Set app configurations
app.config.from_object(Config)
app.config['FLASK_DEBUG'] = 1

# Initialize extensions
db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)


# from server.models import User, Plant, Category, CareNote, UserSchema, CategorySchema, PlantSchema, CareNoteSchema

# Initialize API
api = Api(app)
CORS(app, supports_credentials=True)




@app.route('/')
def index():
    return '<h1>Project Server</h1>'

class CheckSession(Resource):
    def get(self):
        landlord_id = session.get('landlord_id')
        if not landlord_id:
            return {'error': 'unauthorized'}, 401
        landlord = Landlord.query.filter(Landlord.id == landlord_id).first()
        if not landlord:
            return {'error': 'landlord not found'}, 404
        landlord_schema = LandlordSchema()
        landlord_data = landlord_schema.dump(landlord)
        return landlord_data, 200
        
        
class Login(Resource):
    def post(self):
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            return {'error': 'all the fiels are required'}, 400
        
        landlord = Landlord.query.filter(Landlord.username == username).first()
        if not landlord or not landlord.check_password(password):
            return {'error': "username or password doesn't match"}, 400
        
        session['landlord_id'] = landlord.id
        session.permanent = True

        landlord_schema = LandlordSchema()
        landlord_data = landlord_schema.dump(landlord)
        return landlord_data, 200

class Signup(Resource):
    def post(self):

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        confirmed_password = data.get('confirmed_password')

        existing_landlord = Landlord.query.filter(Landlord.username == username).first()

        pattern = re.compile(r'^(?=.*[A-Z])(?=.*[!@#$%^&*]).{6,}$')

        if not username or not isinstance(username, str):
            return {'error': 'username is required and must be a string'}, 400
        if len(username) < 3 or len(username) > 50:
            return {'error': 'username must be between 3 and 50 characters'}, 400
        if existing_landlord:
            return {'error': 'username already exists'}, 400
        
        if not password or not isinstance(password, str):
            return {'error': 'password is required and must be a string'}, 400
        if len(password) < 6 or len(password) > 100:
            return {'error': 'password must be between 6 and 100 characters'}, 400
        if not pattern.match(password):
            return {'error': 'password must be at least 6 characters and include at least an upper case and a symbol(!@#$%^&*)'}
        
        if not confirmed_password or not isinstance(confirmed_password, str):
            return {'error': 'confirmed_password is required and must be a string'}, 400
        if password != confirmed_password:
            return {'error': "password doesn't match"}, 400
        
        # new_landlord = Landlord()
        # new_landlord.username = username
        # new_landlord.password = password
        new_landlord = Landlord(username=username, password=password)
        

        db.session.add(new_landlord)
        db.session.commit()

        session['landlord_id'] = new_landlord.id
        session.permanent = True

        landlord_schema = LandlordSchema()
        

        return landlord_schema.dump(new_landlord), 201


class NewRentalBuilding(Resource):
    def post(self):

        landlord_id = session.get('landlord_id')
        if not landlord_id:
            return {'error': 'unauthorized'}, 401
        landlord = Landlord.query.filter(Landlord.id == landlord_id).first()
        if not landlord:
            return {'error': 'landlord not found'}, 404
        data = request.get_json()
        address = data.get('address')
        starting_date = data.get('starting_date')
        ending_date = data.get('ending_date')
        # landlord_id = data.get('landlord_id')
        tenant_id = data.get('tenant_id')
        property_type_id = data.get('property_type_id')

        if not address or not isinstance(address, str):
            return {'error': 'address is required and must be a string'}, 400
        if len(address) < 3 or len(address) > 200:
            return {'error':'address must be between 3 and 200 characters'}, 400
        
        try:
            starting_date = datetime.strptime(starting_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return {'error': 'starting_date must be a valid date in YYYY-MM-DD format.'}, 400
        try:
            ending_date = datetime.strptime(ending_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return {'error': 'ending_date must be a valid date in YYYY-MM-DD format.'}, 400
        
        existing_building = RentalBuilding.query.filter(RentalBuilding.address == address).first()
        if existing_building:
            return {'error': 'A rental building with this address already exists'}, 400


        new_rental_building = RentalBuilding(
            address = address,
            starting_date = starting_date,
            ending_date = ending_date,
            landlord_id = landlord_id,
            tenant_id = tenant_id,
            property_type_id = property_type_id
        )

        db.session.add(new_rental_building)
        db.session.commit()

        return RentalBuildingSchema().dump(new_rental_building), 201

        
                
api.add_resource(CheckSession, '/check_session')    
api.add_resource(Login, '/login')    
api.add_resource(Signup, '/signup')
api.add_resource(NewRentalBuilding, '/rental_buildings/new')    


if __name__ == '__main__':
    print("🔥 Running from the correct app file 🔥")
    app.run(port=5555, debug=True)

       
   #python -m server.app    
   # http://localhost:5555/check_session