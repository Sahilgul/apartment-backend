# app/models/review.py
from app import db
from datetime import datetime
import uuid

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.String(36), db.ForeignKey('listings.id'), nullable=False)
    
    def to_dict(self, include_user=False):
        data = {
            'id': self.id,
            'content': self.content,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() + 'Z',
            'updated_at': self.updated_at.isoformat() + 'Z',
            'user_id': self.user_id,
            'listing_id': self.listing_id
        }
        
        if include_user:
            data['user'] = self.author.to_dict()
            
        return data