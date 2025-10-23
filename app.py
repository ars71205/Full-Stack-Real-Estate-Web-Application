from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "dreamhouse_secret_key_2024"

# ---------- Database Configuration ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dreamhouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------- Mail Configuration ----------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_app_password'     # Replace with your app password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'
mail = Mail(app)

# ---------- Database Models ----------
class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False, default=3)
    bathrooms = db.Column(db.Integer, nullable=False, default=2)
    location = db.Column(db.String(200), nullable=False, default="Unknown Location")
    
    def __repr__(self):
        return f'<House {self.name}>'

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Inquiry Details
    message = db.Column(db.Text, nullable=False)
    inquiry_type = db.Column(db.String(50), nullable=False, default='general')
    contact_method = db.Column(db.String(20), nullable=False, default='email')
    
    # Property Reference
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=True)
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # new, contacted, closed
    
    # Relationship
    house = db.relationship('House', backref='inquiries')
    
    def __repr__(self):
        return f'<Inquiry {self.name} - {self.inquiry_type}>'

class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default="About Dream House Realty")
    content = db.Column(db.Text, nullable=False)
    mission = db.Column(db.Text, nullable=True)
    contact_email = db.Column(db.String(120), nullable=False, default="info@dreamhouse.com")
    
    def __repr__(self):
        return f'<About {self.title}>'

# ---------- Routes ----------
@app.route('/')
def home():
    """Display all houses on the home page"""
    houses = House.query.all()
    return render_template('home.html', houses=houses)

@app.route('/house/<int:id>')
def house_detail(id):
    """Display individual house details"""
    house = House.query.get_or_404(id)
    return render_template('house_detail.html', house=house)

@app.route('/about')
def about():
    """Display about page content from database"""
    about_content = About.query.first()
    if not about_content:
        # Create default about content if none exists
        about_content = About(
            title="About Dream House Realty",
            content="""Welcome to Dream House Realty, your trusted partner in finding the perfect home. With over 15 years of experience in the real estate industry, we have helped thousands of families find their dream properties.

Our team of dedicated professionals understands that buying or selling a home is one of the most important decisions you'll make. That's why we're committed to providing personalized service, expert guidance, and comprehensive market knowledge every step of the way.""",
            mission="Our mission is to transform the real estate experience by providing exceptional service, innovative solutions, and unwavering dedication to our clients' needs. We believe everyone deserves to find their perfect home.",
            contact_email="info@dreamhouserealty.com"
        )
        db.session.add(about_content)
        db.session.commit()
    return render_template('about.html', about=about_content)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Handle contact form submissions with enhanced inquiry tracking"""
    houses = House.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        house_id = request.form.get('house_id', type=int)
        inquiry_type = request.form.get('inquiry_type', 'general')
        contact_method = request.form.get('contact_method', 'email')
        
        print(f"📝 Form submitted: {name}, {email}, {inquiry_type}")  # Debug
        
        # Basic validation
        if not name or not email or not message:
            flash('Please fill in all required fields (Name, Email, Message).', 'error')
            return render_template('contact.html', houses=houses)
        
        # Email validation
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('contact.html', houses=houses)
        
        try:
            # Create new inquiry with enhanced fields
            new_inquiry = Inquiry(
                name=name,
                email=email,
                phone=phone,
                message=message,
                house_id=house_id,
                inquiry_type=inquiry_type,
                contact_method=contact_method,
                status='new'
            )
            
            # Save to database
            db.session.add(new_inquiry)
            db.session.commit()
            
            print(f"💾 Inquiry saved to database with ID: {new_inquiry.id}")  # Debug
            
            # Send email notification
            email_sent = send_inquiry_email(new_inquiry)
            
            if email_sent:
                flash('Thank you for your inquiry! We will get back to you within 2 hours.', 'success')
            else:
                flash('Thank you for your inquiry! Your message has been received. (Email notification failed)', 'warning')
            
            return redirect(url_for('contact'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {e}")
            flash('Sorry, there was an error submitting your inquiry. Please try again.', 'error')
    
    return render_template('contact.html', houses=houses)

@app.route('/admin/inquiries')
def admin_inquiries():
    """View all inquiries (for admin purposes)"""
    inquiries = Inquiry.query.order_by(Inquiry.timestamp.desc()).all()
    return render_template('admin_inquiries.html', inquiries=inquiries)

@app.route('/test-email')
def test_email():
    """Test email functionality"""
    try:
        msg = Message(
            subject="Test Email from Dream House Realty",
            sender=app.config['MAIL_USERNAME'],
            recipients=["abc098@gmail.com"],  # Your email
            body="This is a test email from your Flask application. If you receive this, email is working!"
        )
        mail.send(msg)
        return "✅ Test email sent! Check your inbox and spam folder."
    except Exception as e:
        return f"❌ Email test failed: {str(e)}"

# ---------- Utility Functions ----------
def send_inquiry_email(inquiry):
    """Send enhanced email notification for new inquiry"""
    try:
        print(f"🔧 Attempting to send email...")
        print(f"🔧 Mail server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
        print(f"🔧 Mail username: {app.config['MAIL_USERNAME']}")
        print(f"🔧 Using TLS: {app.config['MAIL_USE_TLS']}")
        
        house_info = ""
        if inquiry.house_id and inquiry.house:
            house_info = f"""
Interested Property: {inquiry.house.name}
Property Price: ${inquiry.house.price:,}
Property Location: {inquiry.house.location}
Bedrooms: {inquiry.house.bedrooms} | Bathrooms: {inquiry.house.bathrooms}
            """.strip()
        elif inquiry.house_id:
            # If house exists but relationship not loaded
            house = House.query.get(inquiry.house_id)
            if house:
                house_info = f"""
Interested Property: {house.name}
Property Price: ${house.price:,}
Property Location: {house.location}
Bedrooms: {house.bedrooms} | Bathrooms: {house.bathrooms}
                """.strip()
        
        subject = f"New {inquiry.inquiry_type.title()} Inquiry from {inquiry.name}"
        
        body = f"""
NEW INQUIRY - Dream House Realty
{'='*50}

CONTACT INFORMATION:
Name: {inquiry.name}
Email: {inquiry.email}
Phone: {inquiry.phone if inquiry.phone else 'Not provided'}
Preferred Contact: {inquiry.contact_method.title()}

INQUIRY DETAILS:
Type: {inquiry.inquiry_type.title()}
Timestamp: {inquiry.timestamp.strftime('%Y-%m-%d at %H:%M:%S')}
Status: {inquiry.status.title()}

{house_info}

MESSAGE:
{inquiry.message}

{'='*50}
This inquiry was submitted through your Dream House Realty website.
Inquiry ID: {inquiry.id}
        """.strip()
        
        print(f"🔧 Preparing email to: abc098@gmail.com")
        print(f"🔧 Email subject: {subject}")
        
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=["abc098@gmail.com"],  # Your email
            body=body
        )
        
        print(f"🔧 Attempting to send email via SMTP...")
        mail.send(msg)
        print(f"✅ Email sent successfully to abc098@gmail.com")
        return True
        
    except Exception as e:
        print(f"❌ EMAIL SENDING FAILED: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def init_database():
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add sample houses if none exist
        if House.query.count() == 0:
            sample_houses = [
                House(
                    name="Modern Luxury Villa",
                    price=750000,
                    image_url="https://images.unsplash.com/photo-1613977257363-707ba9348227?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
                    description="Stunning modern villa with panoramic views, smart home features, and luxurious amenities. Perfect for entertaining with open floor plan and premium finishes.",
                    bedrooms=4,
                    bathrooms=3,
                    location="Beverly Hills, CA"
                ),
                House(
                    name="Cozy Family Cottage",
                    price=320000,
                    image_url="https://images.unsplash.com/photo-1568605114967-8130f3a36994?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
                    description="Charming cottage in a peaceful neighborhood. Features updated kitchen, spacious backyard, and recently renovated bathrooms. Great family home.",
                    bedrooms=3,
                    bathrooms=2,
                    location="Portland, OR"
                ),
                House(
                    name="Downtown Penthouse",
                    price=1200000,
                    image_url="https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
                    description="Luxurious penthouse in the heart of downtown. Floor-to-ceiling windows, private terrace, and premium building amenities including pool and gym.",
                    bedrooms=3,
                    bathrooms=2,
                    location="New York, NY"
                ),
                House(
                    name="Beachfront Paradise",
                    price=950000,
                    image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
                    description="Direct beach access from this beautiful coastal home. Features include ocean views, updated kitchen, and spacious deck perfect for sunset watching.",
                    bedrooms=4,
                    bathrooms=3,
                    location="Miami, FL"
                )
            ]
            db.session.add_all(sample_houses)
            print("✅ Sample houses added to database")
        
        # Add about content if none exists
        if About.query.count() == 0:
            about_content = About(
                title="About Dream House Realty",
                content="""Welcome to Dream House Realty, your trusted partner in finding the perfect home. With over 15 years of experience in the real estate industry, we have helped thousands of families find their dream properties.

Our team of dedicated professionals understands that buying or selling a home is one of the most important decisions you'll make. That's why we're committed to providing personalized service, expert guidance, and comprehensive market knowledge every step of the way.""",
                mission="Our mission is to transform the real estate experience by providing exceptional service, innovative solutions, and unwavering dedication to our clients' needs. We believe everyone deserves to find their perfect home.",
                contact_email="info@dreamhouserealty.com"
            )
            db.session.add(about_content)
            print("✅ About content added to database")
        
        db.session.commit()
        print("🎉 Database initialized with sample data!")

# ---------- Application Entry Point ----------
if __name__ == "__main__":
    init_database()
    app.run(debug=True)