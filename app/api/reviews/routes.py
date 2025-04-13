# app/api/reviews/routes.py
from flask import request, jsonify
from app import db
from app.api.reviews import bp
from app.models.review import Review
from app.models.listing import Listing
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError

@bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    # Check if user is a verified tenant
    claims = get_jwt()
    if claims.get('role') != 'tenant':
        return jsonify({'error': 'Only tenants can post reviews'}), 403
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_verified:
        return jsonify({'error': 'Only verified tenants can post reviews'}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['content', 'rating', 'listing_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate rating range
    rating = data['rating']
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
    
    # Check if listing exists
    listing = Listing.query.get(data['listing_id'])
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if user already reviewed this listing
    existing_review = Review.query.filter_by(
        user_id=current_user_id,
        listing_id=data['listing_id']
    ).first()
    
    if existing_review:
        return jsonify({'error': 'You have already reviewed this listing'}), 400
    
    # Create new review
    review = Review(
        content=data['content'],
        rating=data['rating'],
        user_id=current_user_id,
        listing_id=data['listing_id']
    )
    
    # Save review to database
    try:
        db.session.add(review)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'Review created successfully',
        'review': review.to_dict(include_user=True)
    }), 201

@bp.route('/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Check if the current user is the author of the review
    current_user_id = get_jwt_identity()
    if review.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to update this review'}), 403
    
    data = request.get_json() or {}
    
    # Update review fields
    if 'content' in data:
        review.content = data['content']
    
    if 'rating' in data:
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400
        review.rating = rating
    
    # Save changes to database
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'Review updated successfully',
        'review': review.to_dict(include_user=True)
    }), 200

@bp.route('/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get(review_id)
    
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    
    # Check if the current user is the author of the review
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if review.user_id != current_user_id and user.role != 'admin':
        return jsonify({'error': 'You do not have permission to delete this review'}), 403
    
    # Delete review from database
    try:
        db.session.delete(review)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({'message': 'Review deleted successfully'}), 200

@bp.route('/listing/<listing_id>', methods=['GET'])
def get_listing_reviews(listing_id):
    # Check if listing exists
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Get paginated reviews for the listing
    pagination = Review.query.filter_by(listing_id=listing_id).order_by(
        Review.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [item.to_dict(include_user=True) for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200