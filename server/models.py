from server.extensions import db, bcrypt,ma  # Use db from extensions.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from sqlalchemy.orm import validates, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from flask_marshmallow import Marshmallow
from datetime import date
import re


class Landlord(db.Model):

    __tablename__ = 'landlords'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
 
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    tenants = db.relationship('Tenant', back_populates='landlord',  cascade='all, delete-orphan')
    
    rental_buildings = db.relationship('RentalBuilding', back_populates='landlord',  cascade='all, delete-orphan')

    property_types = db.relationship('PropertyType', secondary='landlord_property_type', back_populates='landlords')
    
    @validates('username')
    def validate_username(self, key, username):
        if not username or not isinstance(username, str):
            raise ValueError('username is required and must be a string')
        if len(username) < 3 or len(username) > 50:
            raise ValueError('username must be between 3 and 50 characters')
        return username
    @property
    def password(self):
        raise AttributeError('password is read only')
    @password.setter
    def password(self, password):
        pattern = re.compile(r'^(?=.*\w)(?=.*[!@#$%^&*]).{6,}$')
        if not password or not isinstance(password, str):
            raise ValueError('password is required and must be a string')
        if not pattern.match(password):
            raise ValueError('Password must contain at least one uppercase or lowercase letter, number, or underscore. It must contain at least one symbol (!@#$%^&*), and be between 6 and 100 characters in length.')
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        result = bcrypt.check_password_hash(self.password_hash, password)
        return result

class Tenant(db.Model):

    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
 
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(12), nullable=False)
    occupation = db.Column(db.String(50), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'))

    landlord = db.relationship('Landlord', back_populates='tenants')
    rental_buildings = db.relationship('RentalBuilding', back_populates='tenant' )

    @validates('first_name')
    def validate_first_name(self, key, first_name):
        if not first_name or not isinstance(first_name, str):
            raise ValueError('first_name is required and must be a string')
        if len(first_name) < 3 or len(first_name) > 50:
            raise ValueError('first_name must be between 3 and 50 characters')
        return first_name
    @validates('last_name')
    def validate_last_name(self, key, last_name):
        if not last_name or not isinstance(last_name, str):
            raise ValueError('last_name is required and must be a string')
        if len(last_name) < 3 or len(last_name) > 50:
            raise ValueError('last_name must be between 3 and 50 characters')
        return last_name
    @validates('occupation')
    def validate_occupation(self, key, occupation):
        if not occupation or not isinstance(occupation, str):
            raise ValueError('foccupation is required and must be a string')
        if len(occupation) < 3 or len(occupation) > 50:
            raise ValueError('occupation must be between 3 and 50 characters')
        return occupation
    @validates('telephone')
    def validate_telephone(self, key, telephone):
        pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
        if not telephone or not isinstance(telephone, str):
            raise ValueError('telephone is required and must be a string')
        if not pattern.match(telephone):
            raise ValueError('telephone must match xxx-xxx-xxxx format')
        return telephone

class RentalBuilding(db.Model):

    __tablename__ = 'rental_buildings'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
 
    address = db.Column(db.String(200), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    starting_date = db.Column(db.Date, nullable=False)
    ending_date = db.Column(db.Date, nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    property_type_id = db.Column(db.Integer, db.ForeignKey('property_types.id'))

    landlord = db.relationship('Landlord', back_populates='rental_buildings')
    tenant = db.relationship('Tenant', back_populates='rental_buildings' )
    property_type = db.relationship('PropertyType', back_populates='rental_buildings')

    @validates('address')
    def validate_address(self, key, address):
        if not address or not isinstance(address, str):
            raise ValueError('address is required and must be a string')
        if len(address) < 3 or len(address) > 200:
            raise ValueError('address must be between 3 and 200 characters')
        return address
    @validates('price')
    def validate_price(self, key, price):
        if not price or not isinstance(price, int):
            raise ValueError('price is required and must be a number')
        if price < 100:
            raise ValueError('price must be greater than 100')
        return price
    @validates('starting_date')
    def validate_starting_date(self, key, starting_date):
        if not starting_date or not isinstance(starting_date, date):
            raise ValueError('starting_date is required and must be a date')
        return starting_date
    @validates('ending_date')
    def validate_ending_date(self, key, ending_date):
        if not ending_date or not isinstance(ending_date, date):
            raise ValueError('ending_date is required and must be a date')
        if self.starting_date and ending_date <= self.starting_date:
            raise ValueError('ending date must be after starting date')
        return ending_date

class PropertyType(db.Model):

    __tablename__ = 'property_types'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    property_type_name = db.Column(db.String(50), nullable=False)
    
    rental_buildings = db.relationship('RentalBuilding', back_populates='property_type')

    landlords = db.relationship('Landlord', secondary='landlord_property_type', back_populates='property_types')

    @validates('property_type_name')
    def validate_property_type_name(self, key, property_type_name):
        if not property_type_name or not isinstance(property_type_name, str):
            raise ValueError('property_type_name is required and must be a string')
        if len(property_type_name) < 3 or len(property_type_name) > 50:
            raise ValueError('property_type_name must be between 3 and 50 characters')
        return property_type_name

landlord_property_type = db.Table(
    'landlord_property_type', 
    db.Column('landlord_id',db.Integer, db.ForeignKey('landlords.id'), primary_key=True),
    db.Column('property_type_id', db.Integer, db.ForeignKey('property_types.id'), primary_key=True)
)





