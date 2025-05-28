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
from server.models import Landlord, Tenant, RentalBuilding, PropertyType, Payment

# from server.models import Landlord, Tenant, RentalBuilding, PropertyType  # or whatever your models are

# from flask import send_from_directory


load_dotenv()
import os

# Initialize Flask app
app = Flask(__name__)
# app = Flask(__name__, static_folder='../client/build', static_url_path='/')


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



if __name__ == '__main__':
    print("🔥 Running from the correct app file 🔥")
    app.run(port=5555, debug=True)

       
   #python -m server.app    
   # http://localhost:5555/check_session