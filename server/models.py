from server.extensions import db, bcrypt,ma  # Use db from extensions.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from sqlalchemy.orm import validates, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import fields
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
    
    def property_by_name(self, type_name):
        return [b for b in self.rental_buildings if b.property_type.property_type_name == type_name]
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
        pattern = re.compile(r'^(?=.*[A-Z])(?=.*[!@#$%^&*]).{6,}$')
        if not password or not isinstance(password, str):
            raise ValueError('password is required and must be a string')
        if not pattern.match(password):
            raise ValueError('password must be at least 6 characters and include at least an upper case and a symbol(!@#$%^&*)')
        
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
            raise ValueError('occupation is required and must be a string')
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
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    monthly_price = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.Boolean, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    payment_period = db.Column(db.String(7), nullable=False)
    rental_building_id = db.Column(db.Integer, db.ForeignKey('rental_buildings.id'))

    rental_building = db.relationship('RentalBuilding', back_populates='payments')

    @validates('price')
    def validate_price(self, key, price):
        if not price or not isinstance(price, int):
            raise ValueError('price is required and must be a number')
        if price < 100:
            raise ValueError('price must be greater than 100')
        return price
    @validates('payment_status')
    def validate_payment_status(self, key, payment_status):
        if payment_status is None or not isinstance(payment_status, bool):
            raise ValueError('payment_status is required and must be a status')
        return payment_status
    


class RentalBuilding(db.Model):

    __tablename__ = 'rental_buildings'
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
 
    address = db.Column(db.String(200), nullable=False, unique=True)
    # price = db.Column(db.Integer, nullable=False)
    starting_date = db.Column(db.Date, nullable=False)
    ending_date = db.Column(db.Date, nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlords.id'))
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'))
    property_type_id = db.Column(db.Integer, db.ForeignKey('property_types.id'))

    landlord = db.relationship('Landlord', back_populates='rental_buildings')
    tenant = db.relationship('Tenant', back_populates='rental_buildings' )
    property_type = db.relationship('PropertyType', back_populates='rental_buildings')

    payments = db.relationship('Payment', back_populates='rental_building', cascade=('all, delete-orphan'))

    @validates('address')
    def validate_address(self, key, address):
        if not address or not isinstance(address, str):
            raise ValueError('address is required and must be a string')
        if len(address) < 3 or len(address) > 200:
            raise ValueError('address must be between 3 and 200 characters')
        return address
    
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

class LandlordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Landlord
        load_instance = True
        include_relationship = True
        exclude = ('password_hash',)

    id = ma.auto_field()
    username = ma.auto_field()
    password = fields.String(load_only=True)

    tenants = ma.Nested('TenantSchema', many=True, only=('id', 'first_name', 'last_name', 'telephone', 'occupation', 'landlord_id'))
    rental_buildings = ma.Nested('RentalBuildingSchema', many=True, only=('id', 'address', 'starting_date', 'ending_date', 'landlord_id', 'tenant_id', 'property_type_id', 'payments'))
    property_types = ma.Nested('PropertyTypeSchema', many=True, only=('id', 'property_type_name'))


class TenantSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tenant
        include_relationship = True
        load_instance = True

    id = ma.auto_field()
    first_name = ma.auto_field()
    last_name = ma.auto_field()
    occupation = ma.auto_field()
    landlord_id = ma.auto_field()

    # landlord = ma.Nested('LandlordSchema', exclude=('tenants', 'rental_buildings'))
    landlord = ma.Nested('LandlordSchema', only=('id','username'))
    # rental_buildings = ma.Nested('RentalBuildingSchema', many=True, exclude=('tenant', 'landlord'))
    rental_buildings = ma.Nested('RentalBuildingSchema', many=True, only=('id', 'address', 'starting_date', 'ending_date', 'landlord_id', 'tenant_id', 'property_type_id', 'tenant'))


class RentalBuildingSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RentalBuilding
        include_relationship = True
        load_instance = True

    id = ma.auto_field()
    address = ma.auto_field()
    starting_date = ma.Date(format='%Y-%m-%d')
    ending_date = ma.Date(format='%Y-%m-%d')
    landlord_id = ma.auto_field()
    tenant_id = ma.auto_field()
    property_type_id = ma.auto_field()

    # landlord = ma.Nested('LandlordSchema', exclude=('rental_buildings',))
    landlord = ma.Nested('LandlordSchema', only=('id', 'username'))
    # tenant = ma.Nested('TenantSchema', exclude=('rental_buildings',))
    tenant = ma.Nested('TenantSchema', only=('id', 'first_name', 'last_name', 'telephone', 'occupation', 'landlord_id'))
    # property_type = ma.Nested('PropertyTypeSchema', exclude=('rental_buildings',))
    property_type = ma.Nested('PropertyTypeSchema', only=('id','property_type_name'))
    # payments = ma.Nested('PaymentSchema', many=True, only=('id', 'monthly_price', 'price', 'payment_status', 'payment_date', 'due_date', 'payment_period', 'rental_building_id'))
    payments = ma.Nested('PaymentSchema', many=True)

class PropertyTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PropertyType
        load_instance = True
        include_relationship = True

    id = ma.auto_field()
    property_type_name = ma.auto_field()

    # rental_buildings = ma.Nested('RentalBuildingSchema', many=True, exclude=('property_type',))
    # landlords = ma.Nested('LandlordSchema', many=True, exclude=('property_types',))
    rental_buildings = ma.Nested('RentalBuildingSchema', many=True, only=('id', 'address', 'starting_date', 'ending_date', 'landlord_id', 'tenant_id', 'property_type_id'))
    landlords = ma.Nested('LandlordSchema', many=True, only=('id', 'username'))

# class LandlordSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Landlord
#         load_instance = True
#         include_relationship = True
#         exclude = ('password_hash',)

#     id = ma.auto_field()
#     username = ma.auto_field()
#     password = fields.String(load_only=True)

#     tenants = ma.Nested('TenantSchema', many=True, only=('id', 'first_name', 'last_name', 'telephone', 'occupation', 'landlord_id'))
#     rental_buildings = ma.Nested('RentalBuildingSchema', many=True, only=('id', 'address', 'starting_date', 'ending_date', 'landlord_id', 'tenant_id', 'property_type_id'))
#     property_types = ma.Nested('PropertyTypeSchema', many=True, only=('id', 'property_type_name'))

class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment
        load_instance = True
        include_relationship = True

    id = ma.auto_field()
    monthly_price = ma.auto_field()
    price = ma.auto_field()
    payment_status = ma.auto_field()
    payment_date = ma.Date(format='%Y-%m-%d')
    due_date = ma.Date(format='%Y-%m-%d')
    payment_period = ma.auto_field()
    rental_building_id = ma.auto_field()

    # rental_building = ma.Nested('RentalBuildingSchema', only=('id', 'address', 'starting_date', 'ending_date', 'landlord_id', 'tenant_id', 'property_type_id'))
