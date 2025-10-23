# 🏠 Dream House Realty - Real Estate Web Application

A full-stack Flask web application for real estate listings with inquiry management system. Features property displays, contact forms and email features.



**✨ Features**
- Property Listings: Beautiful display of houses with images, prices, and details
- Inquiry Management: Comprehensive contact forms with database storage
- Email Notifications: Automatic email alerts for new inquiries
- Admin Dashboard: View all customer inquiries and submissions
- Responsive Design: Works seamlessly on desktop and mobile devices
- Dynamic Content: About page content managed through database



**Technology Stack**
Backend: Flask, Python
Database: SQLite with SQLAlchemy ORM
Email: Flask-Mail with Gmail SMTP
Frontend: HTML5, CSS3, JavaScript
Templates: Jinja2 templating engine



**📊 Key Features Explained**
- Property Management
Dynamic property listings with searchable database
Individual property detail pages with full specifications
Image integration from external URLs



**Inquiry System**
Multi-field contact forms with validation
Database persistence for all customer inquiries
Automatic email notifications to admin
Inquiry status tracking (new, contacted, closed)



**🔧 Configuration**
**Email Setup**
Enable 2-factor authentication on Gmail
Generate App Password from Google Account settings
Update MAIL_USERNAME and MAIL_PASSWORD in app.py
**Database**
SQLite database automatically created on first run
Sample properties and about content pre-loaded
No additional database setup required



**🌐 Routes Overview**
/ - Homepage with all property listings
/house/<id> - Individual property details
/about - About us page (dynamic content)
/contact - Contact form with inquiry submission
/admin/inquiries - Admin inquiry dashboard
/test-email - Email functionality test
