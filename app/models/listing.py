# app/models/listing.py
from app import db
from datetime import datetime
import uuid

# Association table for many-to-many relationship
listing_amenities = db.Table('listing_amenities',
    db.Column('listing_id', db.String(36), db.ForeignKey('listings.id'), primary_key=True),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenities.id'), primary_key=True)
)

class Listing(db.Model):
    __tablename__ = 'listings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    square_feet = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    reviews = db.relationship('Review', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary=listing_amenities, lazy='subquery',
                                backref=db.backref('listings', lazy=True))
    images = db.relationship('ListingImage', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_reviews=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'square_feet': self.square_feet,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'user_id': self.user_id,
            'amenities': [amenity.to_dict() for amenity in self.amenities],
            'images': [image.to_dict() for image in self.images]
        }
        
        if include_reviews:
            data['reviews'] = [review.to_dict() for review in self.reviews]
            
        return data

class ListingImage(db.Model):
    __tablename__ = 'listing_images'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256), nullable=False)
    caption = db.Column(db.String(256), nullable=True)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    listing_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'caption': self.caption,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat() + 'Z',
            'listing_id': self.listing_id
        }

class Amenity(db.Model):
    __tablename__ = 'amenities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    icon = db.Column(db.String(64), nullable=True)  # Font awesome icon name or similar
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }
