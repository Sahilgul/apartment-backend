# app/api/listings/routes.py
from flask import request, jsonify
from app import db
from app.api.listings import bp
from app.models.listing import Listing, ListingImage, Amenity
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import SQLAlchemyError

def check_landlord_role():
    claims = get_jwt()
    if claims.get('role') != 'landlord':
        return jsonify({'error': 'Only landlords can perform this action'}), 403
    return None

# @bp.route('/', methods=['GET', 'OPTIONS'])
# def get_listings():

@bp.route('/', methods=['GET', 'OPTIONS'])
def get_listings():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight check successful'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response, 200
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    query = Listing.query.filter_by(is_published=True)
    
    # Apply filters if provided
    city = request.args.get('city')
    if city:
        query = query.filter(Listing.city.ilike(f'%{city}%'))
        
    state = request.args.get('state')
    if state:
        query = query.filter(Listing.state.ilike(f'%{state}%'))
        
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
        
    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
        
    bedrooms = request.args.get('bedrooms', type=int)
    if bedrooms is not None:
        query = query.filter(Listing.bedrooms >= bedrooms)
        
    bathrooms = request.args.get('bathrooms', type=float)
    if bathrooms is not None:
        query = query.filter(Listing.bathrooms >= bathrooms)
    
    # Get paginated results
    pagination = query.order_by(Listing.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/<listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    if not listing.is_published:
        # Check if user is the owner
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        if not current_user_id or current_user_id != listing.user_id:
            return jsonify({'error': 'Listing not found'}), 404
    
    return jsonify(listing.to_dict(include_reviews=True)), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_listing():
    # Check if user is a landlord
    error_response = check_landlord_role()
    if error_response:
        return error_response
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['title', 'description', 'price', 'bedrooms', 'bathrooms', 
                       'address', 'city', 'state', 'zip_code']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    current_user_id = get_jwt_identity()
    
    # Create new listing
    listing = Listing(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        bedrooms=data['bedrooms'],
        bathrooms=data['bathrooms'],
        square_feet=data.get('square_feet'),
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zip_code'],
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        is_published=data.get('is_published', True),
        user_id=current_user_id
    )
    
    # Add amenities if provided
    if 'amenity_ids' in data and isinstance(data['amenity_ids'], list):
        amenities = Amenity.query.filter(Amenity.id.in_(data['amenity_ids'])).all()
        listing.amenities = amenities
    
    # Add images if provided
    if 'images' in data and isinstance(data['images'], list):
        for img_data in data['images']:
            if 'url' in img_data:
                image = ListingImage(
                    url=img_data['url'],
                    caption=img_data.get('caption'),
                    is_primary=img_data.get('is_primary', False),
                    listing=listing
                )
                db.session.add(image)
    
    # Save listing to database
    try:
        db.session.add(listing)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'Listing created successfully',
        'listing': listing.to_dict()
    }), 201

@bp.route('/<listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    # Check if user is a landlord
    error_response = check_landlord_role()
    if error_response:
        return error_response
    
    listing = Listing.query.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if the current user is the owner of the listing
    current_user_id = get_jwt_identity()
    if listing.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to update this listing'}), 403
    
    data = request.get_json() or {}
    
    # Update listing fields
    for field in ['title', 'description', 'price', 'bedrooms', 'bathrooms', 
                 'square_feet', 'address', 'city', 'state', 'zip_code', 
                 'latitude', 'longitude', 'is_published']:
        if field in data:
            setattr(listing, field, data[field])
    
    # Update amenities if provided
    if 'amenity_ids' in data and isinstance(data['amenity_ids'], list):
        amenities = Amenity.query.filter(Amenity.id.in_(data['amenity_ids'])).all()
        listing.amenities = amenities
    
    # Update images if provided
    if 'images' in data and isinstance(data['images'], list):
        # Remove existing images
        for image in listing.images.all():
            db.session.delete(image)
        
        # Add new images
        for img_data in data['images']:
            if 'url' in img_data:
                image = ListingImage(
                    url=img_data['url'],
                    caption=img_data.get('caption'),
                    is_primary=img_data.get('is_primary', False),
                    listing=listing
                )
                db.session.add(image)
    
    # Save changes to database
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'Listing updated successfully',
        'listing': listing.to_dict()
    }), 200

@bp.route('/<listing_id>', methods=['DELETE'])
@jwt_required()
def delete_listing(listing_id):
    # Check if user is a landlord
    error_response = check_landlord_role()
    if error_response:
        return error_response
    
    listing = Listing.query.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    # Check if the current user is the owner of the listing
    current_user_id = get_jwt_identity()
    if listing.user_id != current_user_id:
        return jsonify({'error': 'You do not have permission to delete this listing'}), 403
    
    # Delete listing from database
    try:
        db.session.delete(listing)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({'message': 'Listing deleted successfully'}), 200

@bp.route('/amenities', methods=['GET'])
def get_amenities():
    amenities = Amenity.query.all()
    return jsonify([amenity.to_dict() for amenity in amenities]), 200

@bp.route('/amenities', methods=['POST'])
@jwt_required()
def create_amenity():
    # Only admins should be able to create amenities in a real app
    # For simplicity, we're allowing any authenticated user
    
    data = request.get_json() or {}
    
    if not data.get('name'):
        return jsonify({'error': 'Amenity name is required'}), 400
    
    # Check if amenity already exists
    if Amenity.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Amenity already exists'}), 400
    
    # Create new amenity
    amenity = Amenity(
        name=data['name'],
        icon=data.get('icon')
    )
    
    # Save amenity to database
    try:
        db.session.add(amenity)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'details': str(e)}), 500
    
    return jsonify({
        'message': 'Amenity created successfully',
        'amenity': amenity.to_dict()
    }), 201