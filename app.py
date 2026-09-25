from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
from datetime import datetime
import os


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "zenvora-development-secret-key"
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================
#
# LOCAL:
# If DATABASE_URL is not present, SQLite is used.
#
# RENDER:
# Render provides DATABASE_URL for PostgreSQL.
#
# This means:
# Local computer -> zenvora.db
# Render         -> PostgreSQL
#
# =========================================================

database_url = os.environ.get("DATABASE_URL")

if database_url:

    # Some PostgreSQL URLs may use postgres://
    # SQLAlchemy expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///zenvora.db"


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# ADMIN MODEL
# =========================================================

class Admin(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# PROPERTY MODEL
# =========================================================

class Property(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    purpose = db.Column(
        db.String(50),
        nullable=False
    )

    location = db.Column(
        db.String(200),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    bedrooms = db.Column(
        db.Integer,
        default=0
    )

    bathrooms = db.Column(
        db.Integer,
        default=0
    )

    area = db.Column(
        db.Integer,
        default=0
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    image = db.Column(
        db.String(500),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="Available"
    )

    featured = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# CART / SHORTLIST MODEL
# =========================================================

class Cart(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("property.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# WISHLIST MODEL
# =========================================================

class Wishlist(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("property.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# INQUIRY MODEL
# =========================================================

class Inquiry(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("property.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(50),
        default="New"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# DEAL MODEL
# =========================================================

class Deal(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("property.id"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    deal_type = db.Column(
        db.String(50),
        default="Sale"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# ADMIN LOGIN DECORATOR
# =========================================================

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):

            flash(
                "Please login as administrator first.",
                "warning"
            )

            return redirect(
                url_for("admin_login")
            )

        return function(*args, **kwargs)

    return decorated_function


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def create_database():

    with app.app_context():

        db.create_all()

        # -------------------------------------------------
        # CREATE DEFAULT ADMIN
        # -------------------------------------------------

        # Fixed default admin credentials for Zenvora
        # Username: admin
        # Password: admin123
        admin_username = "admin"
        admin_password = "admin123"

        existing_admin = Admin.query.first()

        if existing_admin:

            # Keep the existing admin account but reset its
            # username and password from the environment/defaults.
            existing_admin.username = admin_username
            existing_admin.password = generate_password_hash(
                admin_password
            )

            print(
                f"Admin credentials updated: {admin_username}"
            )

        else:

            new_admin = Admin(
                username=admin_username,
                password=generate_password_hash(
                    admin_password
                )
            )

            db.session.add(new_admin)

            print(
                f"Default admin created: {admin_username}"
            )

        # -------------------------------------------------
        # CREATE DEMO PROPERTIES ONLY IF DATABASE IS EMPTY
        # -------------------------------------------------

        if Property.query.count() == 0:

            demo_properties = [

                Property(
                    title="Azure Heights Luxury Apartment",
                    category="Apartment",
                    purpose="Buy",
                    location="Mumbai",
                    price=12500000,
                    bedrooms=3,
                    bathrooms=3,
                    area=1850,
                    description=(
                        "A sophisticated luxury apartment "
                        "offering spacious interiors, premium "
                        "finishes and a comfortable modern "
                        "lifestyle in Mumbai."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600607687920-4e2a09cf159d"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=True
                ),

                Property(
                    title="The Palm Villa",
                    category="Villa",
                    purpose="Buy",
                    location="Panvel",
                    price=28500000,
                    bedrooms=4,
                    bathrooms=4,
                    area=4200,
                    description=(
                        "A premium private villa with generous "
                        "living spaces, elegant architecture "
                        "and a peaceful residential setting."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600585154340-be6161a56a0c"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=True
                ),

                Property(
                    title="Zenith Sky Penthouse",
                    category="Penthouse",
                    purpose="Lease",
                    location="Bandra, Mumbai",
                    price=450000,
                    bedrooms=4,
                    bathrooms=5,
                    area=3500,
                    description=(
                        "An elegant high-rise penthouse featuring "
                        "large living areas, premium interiors "
                        "and an impressive city lifestyle."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600607688969-a5bfcd646154"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=True
                ),

                Property(
                    title="Urban Nest Apartment",
                    category="Apartment",
                    purpose="Rent",
                    location="Thane",
                    price=65000,
                    bedrooms=2,
                    bathrooms=2,
                    area=1250,
                    description=(
                        "A modern apartment designed for comfortable "
                        "urban living with practical spaces and "
                        "excellent connectivity."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600566753086-00f18fb6b3ea"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=False
                ),

                Property(
                    title="Emerald Garden Villa",
                    category="Villa",
                    purpose="Rent",
                    location="Lonavala",
                    price=120000,
                    bedrooms=4,
                    bathrooms=4,
                    area=3800,
                    description=(
                        "A beautiful villa surrounded by greenery, "
                        "perfect for peaceful living away from "
                        "the busy city environment."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600047509807-ba8f99d2cdde"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=False
                ),

                Property(
                    title="Crown View Penthouse",
                    category="Penthouse",
                    purpose="Buy",
                    location="Pune",
                    price=19000000,
                    bedrooms=3,
                    bathrooms=4,
                    area=2700,
                    description=(
                        "A contemporary penthouse with spacious "
                        "rooms, stylish interiors and beautiful "
                        "views in one of Pune's desirable areas."
                    ),
                    image=(
                        "https://images.unsplash.com/"
                        "photo-1600607687939-ce8a6c25118c"
                        "?auto=format&fit=crop&w=1200&q=85"
                    ),
                    status="Available",
                    featured=False
                )
            ]

            db.session.add_all(
                demo_properties
            )

        db.session.commit()


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    featured_properties = Property.query.filter_by(
        status="Available",
        featured=True
    ).order_by(
        Property.created_at.desc()
    ).limit(3).all()

    latest_properties = Property.query.filter_by(
        status="Available"
    ).order_by(
        Property.created_at.desc()
    ).limit(6).all()

    return render_template(
        "index.html",
        featured_properties=featured_properties,
        latest_properties=latest_properties
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill in all fields.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return render_template(
                "register.html"
            )

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password
            )
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session["user_id"] = user.id
            session["user_name"] = user.name

            flash(
                f"Welcome back, {user.name}!",
                "success"
            )

            # ---------------------------------------------
            # RETURN USER TO PROPERTY THEY TRIED TO OPEN
            # ---------------------------------------------

            next_property = session.pop(
                "next_property",
                None
            )

            if next_property:

                return redirect(
                    url_for(
                        "property_detail",
                        property_id=next_property
                    )
                )

            return redirect(
                url_for("index")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "user_id",
        None
    )

    session.pop(
        "user_name",
        None
    )

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# PROPERTIES
# =========================================================

@app.route("/properties")
def properties():

    category = request.args.get(
        "category",
        ""
    ).strip()

    purpose = request.args.get(
        "purpose",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Property.query.filter_by(
        status="Available"
    )

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------

    if category:

        query = query.filter(
            Property.category == category
        )

    # -----------------------------------------------------
    # PURPOSE FILTER
    # -----------------------------------------------------

    if purpose:

        query = query.filter(
            Property.purpose == purpose
        )

    # -----------------------------------------------------
    # LOCATION FILTER
    # -----------------------------------------------------

    if location:

        query = query.filter(
            Property.location.ilike(
                f"%{location}%"
            )
        )

    # -----------------------------------------------------
    # SEARCH BY PROPERTY NAME OR LOCATION
    # -----------------------------------------------------

    if search:

        query = query.filter(
            db.or_(
                Property.title.ilike(
                    f"%{search}%"
                ),
                Property.location.ilike(
                    f"%{search}%"
                )
            )
        )

    property_list = query.order_by(
        Property.created_at.desc()
    ).all()

    return render_template(
        "properties.html",
        properties=property_list,
        category=category,
        purpose=purpose,
        location=location,
        search=search
    )


# =========================================================
# PROPERTY DETAIL
# =========================================================

@app.route("/property/<int:property_id>")
def property_detail(property_id):

    property_item = Property.query.get_or_404(
        property_id
    )

    # -----------------------------------------------------
    # REQUIRE USER LOGIN
    # -----------------------------------------------------

    if not session.get("user_id"):

        flash(
            "Please login to view complete property details.",
            "warning"
        )

        session["next_property"] = property_id

        return redirect(
            url_for("login")
        )

    # -----------------------------------------------------
    # SIMILAR PROPERTIES
    # -----------------------------------------------------

    similar_properties = Property.query.filter(
        Property.status == "Available",
        Property.id != property_id,
        db.or_(
            Property.category == property_item.category,
            Property.purpose == property_item.purpose
        )
    ).order_by(
        Property.created_at.desc()
    ).limit(3).all()

    return render_template(
        "property_detail.html",
        property=property_item,
        similar_properties=similar_properties
    )


# =========================================================
# ADD TO SHORTLIST / CART
# =========================================================

@app.route("/cart/add/<int:property_id>")
def add_cart(property_id):

    if not session.get("user_id"):

        flash(
            "Please login first.",
            "warning"
        )

        session["next_property"] = property_id

        return redirect(
            url_for("login")
        )

    property_item = Property.query.get_or_404(
        property_id
    )

    user_id = session["user_id"]

    existing = Cart.query.filter_by(
        user_id=user_id,
        property_id=property_id
    ).first()

    if existing:

        flash(
            "Property is already in your shortlist.",
            "info"
        )

        return redirect(
            request.referrer or
            url_for(
                "property_detail",
                property_id=property_id
            )
        )

    cart_item = Cart(
        user_id=user_id,
        property_id=property_item.id
    )

    db.session.add(cart_item)
    db.session.commit()

    flash(
        "Property added to your shortlist.",
        "success"
    )

    return redirect(
        request.referrer or
        url_for(
            "property_detail",
            property_id=property_id
        )
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.route("/cart/remove/<int:property_id>")
def remove_cart(property_id):

    if not session.get("user_id"):

        return redirect(
            url_for("login")
        )

    cart_item = Cart.query.filter_by(
        user_id=session["user_id"],
        property_id=property_id
    ).first()

    if cart_item:

        db.session.delete(
            cart_item
        )

        db.session.commit()

        flash(
            "Property removed from shortlist.",
            "success"
        )

    return redirect(
        url_for("cart")
    )


# =========================================================
# CART / SHORTLIST
# =========================================================

@app.route("/cart")
def cart():

    if not session.get("user_id"):

        flash(
            "Please login to view your shortlist.",
            "warning"
        )

        return redirect(
            url_for("login")
        )

    cart_items = Cart.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Cart.created_at.desc()
    ).all()

    shortlisted_properties = []

    for item in cart_items:

        property_item = Property.query.get(
            item.property_id
        )

        if property_item:

            shortlisted_properties.append(
                property_item
            )

    return render_template(
        "cart.html",
        cart_items=shortlisted_properties
    )


# =========================================================
# WISHLIST
# =========================================================

@app.route("/wishlist/<int:property_id>")
def wishlist(property_id):

    if not session.get("user_id"):

        flash(
            "Please login to save properties.",
            "warning"
        )

        session["next_property"] = property_id

        return redirect(
            url_for("login")
        )

    property_item = Property.query.get_or_404(
        property_id
    )

    user_id = session["user_id"]

    existing = Wishlist.query.filter_by(
        user_id=user_id,
        property_id=property_item.id
    ).first()

    if existing:

        db.session.delete(
            existing
        )

        db.session.commit()

        flash(
            "Property removed from wishlist.",
            "success"
        )

    else:

        wishlist_item = Wishlist(
            user_id=user_id,
            property_id=property_item.id
        )

        db.session.add(
            wishlist_item
        )

        db.session.commit()

        flash(
            "Property saved to wishlist.",
            "success"
        )

    return redirect(
        request.referrer or
        url_for(
            "property_detail",
            property_id=property_id
        )
    )


# =========================================================
# INQUIRY
# =========================================================

@app.route(
    "/inquiry/<int:property_id>",
    methods=["POST"]
)
def inquiry(property_id):

    if not session.get("user_id"):

        flash(
            "Please login before sending an inquiry.",
            "warning"
        )

        session["next_property"] = property_id

        return redirect(
            url_for("login")
        )

    property_item = Property.query.get_or_404(
        property_id
    )

    message = request.form.get(
        "message",
        ""
    ).strip()

    if not message:

        flash(
            "Please enter your message.",
            "danger"
        )

        return redirect(
            url_for(
                "property_detail",
                property_id=property_id
            )
        )

    inquiry_item = Inquiry(
        user_id=session["user_id"],
        property_id=property_item.id,
        message=message,
        status="New"
    )

    db.session.add(
        inquiry_item
    )

    db.session.commit()

    flash(
        "Your inquiry has been sent successfully.",
        "success"
    )

    return redirect(
        url_for(
            "property_detail",
            property_id=property_id
        )
    )


# =========================================================
# USER PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if not session.get("user_id"):

        flash(
            "Please login to view your profile.",
            "warning"
        )

        return redirect(
            url_for("login")
        )

    user = User.query.get_or_404(
        session["user_id"]
    )

    wishlist_items = Wishlist.query.filter_by(
        user_id=user.id
    ).all()

    cart_items = Cart.query.filter_by(
        user_id=user.id
    ).all()

    inquiries = Inquiry.query.filter_by(
        user_id=user.id
    ).order_by(
        Inquiry.created_at.desc()
    ).all()

    return render_template(
        "profile.html",
        user=user,
        wishlist_items=wishlist_items,
        cart_items=cart_items,
        inquiries=inquiries
    )

# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password,
            password
        ):

            session["admin_logged_in"] = True
            session["admin_username"] = admin.username

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid admin username or password.",
            "danger"
        )

    return render_template(
        "admin_login.html"
    )

# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    session.pop(
        "admin_id",
        None
    )

    session.pop(
        "admin_username",
        None
    )

    flash(
        "Admin logged out successfully.",
        "success"
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    properties = Property.query.order_by(
        Property.created_at.desc()
    ).all()

    inquiries = Inquiry.query.order_by(
        Inquiry.created_at.desc()
    ).all()

    deals = Deal.query.order_by(
        Deal.created_at.desc()
    ).all()

    total_users = User.query.count()

    total_properties = Property.query.count()

    available_properties = Property.query.filter_by(
        status="Available"
    ).count()

    total_inquiries = Inquiry.query.count()

    total_deals = Deal.query.count()

    total_revenue = db.session.query(
        db.func.coalesce(
            db.func.sum(Deal.amount),
            0
        )
    ).scalar()

    return render_template(
        "admin_dashboard.html",
        users=users,
        properties=properties,
        inquiries=inquiries,
        deals=deals,
        total_users=total_users,
        total_properties=total_properties,
        available_properties=available_properties,
        total_inquiries=total_inquiries,
        total_deals=total_deals,
        total_revenue=total_revenue
    )


# =========================================================
# ADMIN - ADD PROPERTY
# =========================================================

@app.route(
    "/admin/property/add",
    methods=["GET", "POST"]
)
@admin_required
def admin_add_property():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        purpose = request.form.get(
            "purpose",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        ).strip()

        bedrooms = request.form.get(
            "bedrooms",
            "0"
        ).strip()

        bathrooms = request.form.get(
            "bathrooms",
            "0"
        ).strip()

        area = request.form.get(
            "area",
            "0"
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        image = request.form.get(
            "image",
            ""
        ).strip()

        featured = request.form.get(
            "featured"
        ) == "on"

        if not title or not category or not purpose or not location:

            flash(
                "Please fill in all required property fields.",
                "danger"
            )

            return render_template(
                "add_property.html"
            )

        try:

            price_value = float(price)
            bedrooms_value = int(bedrooms)
            bathrooms_value = int(bathrooms)
            area_value = int(area)

        except ValueError:

            flash(
                "Price, bedrooms, bathrooms and area must contain valid numbers.",
                "danger"
            )

            return render_template(
                "add_property.html"
            )

        new_property = Property(
            title=title,
            category=category,
            purpose=purpose,
            location=location,
            price=price_value,
            bedrooms=bedrooms_value,
            bathrooms=bathrooms_value,
            area=area_value,
            description=description,
            image=image or (
                "https://images.unsplash.com/"
                "photo-1600607687939-ce8a6c25118c"
                "?auto=format&fit=crop&w=1200&q=85"
            ),
            status="Available",
            featured=featured
        )

        db.session.add(
            new_property
        )

        db.session.commit()

        flash(
            "Property listed successfully.",
            "success"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "add_property.html"
    )


# =========================================================
# ADMIN - DELETE PROPERTY
# =========================================================

@app.route(
    "/admin/property/delete/<int:property_id>"
)
@admin_required
def admin_delete_property(property_id):

    property_item = Property.query.get_or_404(
        property_id
    )

    # Delete related cart records
    Cart.query.filter_by(
        property_id=property_id
    ).delete(
        synchronize_session=False
    )

    # Delete related wishlist records
    Wishlist.query.filter_by(
        property_id=property_id
    ).delete(
        synchronize_session=False
    )

    # Delete related inquiry records
    Inquiry.query.filter_by(
        property_id=property_id
    ).delete(
        synchronize_session=False
    )

    # Delete related deal records
    Deal.query.filter_by(
        property_id=property_id
    ).delete(
        synchronize_session=False
    )

    db.session.delete(
        property_item
    )

    db.session.commit()

    flash(
        "Property deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - UPDATE PROPERTY STATUS
# =========================================================

@app.route(
    "/admin/property/status/<int:property_id>",
    methods=["POST"]
)
@admin_required
def admin_update_property_status(property_id):

    property_item = Property.query.get_or_404(
        property_id
    )

    status = request.form.get(
        "status",
        "Available"
    ).strip()

    allowed_statuses = [
        "Available",
        "Sold",
        "Rented",
        "Leased"
    ]

    if status not in allowed_statuses:

        flash(
            "Invalid property status.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    property_item.status = status

    db.session.commit()

    flash(
        "Property status updated.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - UPDATE INQUIRY
# =========================================================

@app.route(
    "/admin/inquiry/status/<int:inquiry_id>",
    methods=["POST"]
)
@admin_required
def admin_update_inquiry(inquiry_id):

    inquiry_item = Inquiry.query.get_or_404(
        inquiry_id
    )

    status = request.form.get(
        "status",
        "New"
    ).strip()

    allowed_statuses = [
        "New",
        "Contacted",
        "Closed"
    ]

    if status not in allowed_statuses:

        flash(
            "Invalid inquiry status.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    inquiry_item.status = status

    db.session.commit()

    flash(
        "Inquiry status updated.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN - ADD DEAL
# =========================================================

@app.route(
    "/admin/deal/add",
    methods=["POST"]
)
@admin_required
def admin_add_deal():

    property_id = request.form.get(
        "property_id"
    )

    user_id = request.form.get(
        "user_id"
    )

    amount = request.form.get(
        "amount",
        "0"
    )

    deal_type = request.form.get(
        "deal_type",
        "Sale"
    ).strip()

    try:

        property_id = int(
            property_id
        )

        amount = float(
            amount
        )

        if user_id:
            user_id = int(user_id)
        else:
            user_id = None

    except (
        ValueError,
        TypeError
    ):

        flash(
            "Invalid deal information.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    property_item = Property.query.get(
        property_id
    )

    if not property_item:

        flash(
            "Property not found.",
            "danger"
        )

        return redirect(
            url_for("admin_dashboard")
        )

    new_deal = Deal(
        property_id=property_id,
        user_id=user_id,
        amount=amount,
        deal_type=deal_type
    )

    db.session.add(
        new_deal
    )

    # Automatically mark property as completed
    if deal_type.lower() == "sale":

        property_item.status = "Sold"

    elif deal_type.lower() == "rent":

        property_item.status = "Rented"

    elif deal_type.lower() == "lease":

        property_item.status = "Leased"

    db.session.commit()

    flash(
        "Deal recorded successfully.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# CONTEXT PROCESSOR
# =========================================================
#
# Makes cart_count and wishlist_count available to
# base.html and other templates.
#
# =========================================================

@app.context_processor
def inject_global_data():

    cart_count = 0
    wishlist_count = 0

    if session.get("user_id"):

        cart_count = Cart.query.filter_by(
            user_id=session["user_id"]
        ).count()

        wishlist_count = Wishlist.query.filter_by(
            user_id=session["user_id"]
        ).count()

    return {
        "cart_count": cart_count,
        "wishlist_count": wishlist_count
    }


# =========================================================
# CREATE DATABASE
# =========================================================

# -------------------------------------------------
# CREATE / UPDATE DEFAULT ADMIN
# -------------------------------------------------

admin_username = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

admin_password = os.environ.get(
    "ADMIN_PASSWORD",
    "admin123"
)

existing_admin = Admin.query.filter_by(
    username=admin_username
).first()

if existing_admin:

    existing_admin.password = generate_password_hash(
        admin_password
    )

    print(
        f"Admin credentials updated: {admin_username}"
    )

else:

    new_admin = Admin(
        username=admin_username,
        password=generate_password_hash(
            admin_password
        )
    )

    db.session.add(new_admin)

    print(
        f"Admin created: {admin_username}"
    )

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        debug=True,
        host="0.0.0.0",
        port=port
    )