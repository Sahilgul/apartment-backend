# 🏠 Apartment Listing App – Backend (Flask)

This is the backend for a university-level apartment listing platform built with Flask using the FlaskMVC structure. It enables landlords to post listings, tenants to leave reviews, and public users to search available apartments.

---

## 📁 Project Structure

```
apartment-listing-app/
│
├── app/
│   ├── __init__.py              # Application factory and extensions setup
│   │
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── listing.py           # Listing, ListingImage, and Amenity models
│   │   └── review.py            # Review model
│   │
│   └── api/
│       ├── auth/                # Authentication routes
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── listings/            # Listing CRUD and amenities
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── reviews/             # Review CRUD
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── users/               # User profile routes
│       │   ├── __init__.py
│       │   └── routes.py
│       └── search/              # Search and filter
│           ├── __init__.py
│           └── routes.py
│
├── config.py                    # App configuration
├── run.py                       # App entry point
├── .flaskenv                    # Environment variables
└── requirements.txt             # Python dependencies
```

---

## 🎯 Project Summary

A platform where:
- **Landlords** can create, update, and delete apartment listings with amenities
- **Verified tenants** can post reviews on listings
- **Public users** can browse/search listings by location and amenities

### Tech Stack:
- **Framework**: Flask (FlaskMVC pattern)
- **Database**: SQLAlchemy
- **Authentication**: Custom JWT-based (no third-party services)

---

## 🚀 How to Run

1. **Clone the repository**
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up environment**:
   ```bash
   FLASK_APP=run.py
   FLASK_ENV=development
   ```
5. **Run the app**:
   ```bash
   flask run
   ```

---

## 🔐 Authentication Endpoints

1. **Register** – `POST /api/auth/register`
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "role": "tenant"
}
```

2. **Login** – `POST /api/auth/login`
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

3. **Refresh Token** – `POST /api/auth/refresh`

Headers:
```
Authorization: Bearer <REFRESH_TOKEN>
```

4. **Verify User** – `GET /api/auth/verify/<USER_ID>`

---

## 🏢 Listing Endpoints

5. **Get All Listings** – `GET /api/listings/`

6. **Get Single Listing** – `GET /api/listings/<LISTING_ID>`

7. **Create Listing** – `POST /api/listings/`

Headers:
```
Authorization: Bearer <ACCESS_TOKEN>
```
Body:
```json
{
  "title": "Nice Apartment",
  "description": "A great apartment",
  "price": 1200,
  "bedrooms": 2,
  "bathrooms": 1,
  "address": "123 Main St",
  "city": "Cityville",
  "state": "Stateland",
  "zip_code": "12345"
}
```

8. **Update Listing** – `PUT /api/listings/<LISTING_ID>`

9. **Delete Listing** – `DELETE /api/listings/<LISTING_ID>`

10. **Get Amenities** – `GET /api/listings/amenities`

---

## 📝 Review Endpoints

11. **Create Review** – `POST /api/reviews/`
```json
{
  "content": "Great place!",
  "rating": 5,
  "listing_id": "<LISTING_ID>"
}
```

12. **Update Review** – `PUT /api/reviews/<REVIEW_ID>`

13. **Delete Review** – `DELETE /api/reviews/<REVIEW_ID>`

14. **Get Listing Reviews** – `GET /api/reviews/listing/<LISTING_ID>`

---

## 👤 User Endpoints

15. **Get Current User** – `GET /api/users/me`

16. **Update User** – `PUT /api/users/me`
```json
{
  "username": "newusername"
}
```

17. **Get My Listings** – `GET /api/users/me/listings`

---

## 🔍 Search Endpoint

18. **Search Listings** – `GET /api/search/?q=apartment&city=New%20York&min_price=1000`

---

## 📌 Notes
- All protected routes require JWT-based Bearer authentication.
- Listings and reviews are linked via `listing_id`.
- Reviews can only be made by verified tenants.

---

## 📦 Dependencies
See `requirements.txt` for all packages. Key ones:
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Marshmallow

---

## 🧩 Optional Integrations
- Social Media APIs (Twitter, LinkedIn, etc.)
- Visualization Tools: Highcharts, Nivo
- Open datasets for enrichment (Kaggle, Awesome Data)

---

## 👥 Contributing
Pull requests welcome. For major changes, please open an issue first.

---

## 📄 License
[MIT License](LICENSE)

