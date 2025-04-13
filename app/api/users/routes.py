# app/api/users/routes.py
from flask import request, jsonify
from app import db
from app.api.users import bp
from app.models.user import User
from app.models.listing import Listing
from app.models.review import Review
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json() or {}
    
    # Prevent changing username if it already exists
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
    
    # Prevent changing email if it already exists
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
    
    # Update user fields
    for field in ['username', 'email']:
        if field in data:
            setattr(user, field, data[field])
    
    # Handle password change separately
    if 'password' in data:
        user.set_password(data['password'])
    
    # Save changes to database
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@bp.route('/me/listings', methods=['GET'])
@jwt_required()
def get_user_listings():
    # Check if user is a landlord
    claims = get_jwt()
    if claims.get('role') != 'landlord':
        return jsonify({'error': 'Only landlords can access listings'}), 403
    
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Get paginated listings for the user
    pagination = Listing.query.filter_by(user_id=current_user_id).order_by(
        Listing.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/me/reviews', methods=['GET'])
@jwt_required()
def get_user_reviews():
    current_user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Get paginated reviews for the user
    pagination = Review.query.filter_by(user_id=current_user_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200