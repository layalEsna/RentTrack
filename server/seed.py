import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.app import app
from server.models import db, Landlord, Tenant, RentalBuilding, PropertyType

if __name__ == '__main__':
    with app.app_context():
        print("🏢 Starting seed...")

        # Reset the database
        db.drop_all()
        db.create_all()

        # Create Property Types
        property_types = [
            PropertyType(property_type_name='Apartment'),
            PropertyType(property_type_name='House'),
            PropertyType(property_type_name='Condo'),
        ]
        db.session.add_all(property_types)
        db.session.commit()

        print("Created property types")

        # Create Landlords
        landlord1 = Landlord(username='JohnDoe', password='Password123!')
        landlord2 = Landlord(username='JaneSmith', password='Password456!')
        db.session.add_all([landlord1, landlord2])
        db.session.commit()

        print("Created landlords")

        # Associate property types with landlords
        landlord1.property_types = [property_types[0], property_types[1]]
        landlord2.property_types = [property_types[2]]
        db.session.commit()

        print("Associated property types with landlords")

        # Create Tenants
        tenant1 = Tenant(first_name='Alice', last_name='Johnson', telephone='123-456-7890', occupation='Teacher', landlord_id=landlord1.id)
        tenant2 = Tenant(first_name='Bob', last_name='Brown', telephone='234-567-8901', occupation='Engineer', landlord_id=landlord2.id)
        db.session.add_all([tenant1, tenant2])
        db.session.commit()

        print("Created tenants")

        # Create Rental Buildings
        rental_building1 = RentalBuilding(
            address='123 Main St, Apartment 101', 
            price=1500, 
            starting_date=datetime(2023, 5, 1).date(), 
            ending_date=datetime(2024, 5, 1).date(),
            landlord_id=landlord1.id,
            tenant_id=tenant1.id,
            property_type_id=property_types[0].id
        )
        rental_building2 = RentalBuilding(
            address='456 Oak St, House 202', 
            price=2500, 
            starting_date=datetime(2023, 6, 1).date(), 
            ending_date=datetime(2024, 6, 1).date(),
            landlord_id=landlord2.id,
            tenant_id=tenant2.id,
            property_type_id=property_types[1].id
        )
        db.session.add_all([rental_building1, rental_building2])
        db.session.commit()

        print("Created rental buildings")

        print("🏢 Seeding complete! Landlords, tenants, rental buildings, and property types created.")
