# app/api/search/routes.py
from flask import request, jsonify
from app import db
from app.api.search import bp
from app.models.listing import Listing, Amenity
from sqlalchemy import or_

@bp.route('/', methods=['GET'])
def search_listings():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Initialize the base query
    listing_query = Listing.query.filter_by(is_published=True)
    
    # Apply text search filter if provided
    if query:
        search_filter = or_(
            Listing.title.ilike(f'%{query}%'),
            Listing.description.ilike(f'%{query}%'),
            Listing.address.ilike(f'%{query}%'),
            Listing.city.ilike(f'%{query}%'),
            Listing.state.ilike(f'%{query}%'),
            Listing.zip_code.ilike(f'%{query}%')
        )
        listing_query = listing_query.filter(search_filter)
    
    # Apply location filters if provided
    city = request.args.get('city')
    if city:
        listing_query = listing_query.filter(Listing.city.ilike(f'%{city}%'))
    
    state = request.args.get('state')
    if state:
        listing_query = listing_query.filter(Listing.state.ilike(f'%{state}%'))
    
    zip_code = request.args.get('zip_code')
    if zip_code:
        listing_query = listing_query.filter(Listing.zip_code.ilike(f'%{zip_code}%'))
    
    # Apply price range filters if provided
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        listing_query = listing_query.filter(Listing.price >= min_price)
    
    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        listing_query = listing_query.filter(Listing.price <= max_price)
    
    # Apply bedroom and bathroom filters if provided
    min_bedrooms = request.args.get('min_bedrooms', type=int)
    if min_bedrooms is not None:
        listing_query = listing_query.filter(Listing.bedrooms >= min_bedrooms)
    
    max_bedrooms = request.args.get('max_bedrooms', type=int)
    if max_bedrooms is not None:
        listing_query = listing_query.filter(Listing.bedrooms <= max_bedrooms)
    
    min_bathrooms = request.args.get('min_bathrooms', type=float)
    if min_bathrooms is not None:
        listing_query = listing_query.filter(Listing.bathrooms >= min_bathrooms)
    
    max_bathrooms = request.args.get('max_bathrooms', type=float)
    if max_bathrooms is not None:
        listing_query = listing_query.filter(Listing.bathrooms <= max_bathrooms)
    
    # Apply amenity filter if provided
    amenity_ids = request.args.getlist('amenity_id', type=int)
    if amenity_ids:
        for amenity_id in amenity_ids:
            listing_query = listing_query.filter(Listing.amenities.any(Amenity.id == amenity_id))
    
    # Get paginated results
    pagination = listing_query.order_by(Listing.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    }), 200