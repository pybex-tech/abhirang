# Abhirang Django Project

## Overview
Abhirang is a Django-based e-commerce platform for t-shirts with a clean, minimal design aesthetic.

## Project Structure
```
abhirang/
├── accounts/          # User authentication and profiles
├── cart/              # Shopping cart functionality
├── core/              # Core app with homepage
├── products/          # Product catalog and categories
├── mystore/           # Django project settings
├── static/            # Static files (CSS, images)
├── media/             # User uploaded files
├── templates/         # HTML templates
└── manage.py          # Django management script
```

## Features
- User authentication (login, signup, profile management)
- User profiles with tabs (Overview, Personal Info, Security, Addresses, Orders)
- Address management with multiple addresses
- Product catalog with categories
- Product search functionality
- Shopping cart
- Clean minimal UI design (white/gray/black color scheme)

## Technology Stack
- **Backend**: Django 5.2.5
- **Database**: SQLite3 (default) / PostgreSQL (Docker)
- **Image Processing**: Pillow 10.4.0
- **Deployment**: Docker & Docker Compose

## Getting Started

### Option 1: Local Development (SQLite)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install Django==5.2.5 Pillow==10.4.0 python-decouple==3.8

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Option 2: Docker (PostgreSQL)
```bash
# Copy environment file
cp .env.example .env

# Build and start containers
docker-compose up --build

# Or use Makefile
make build
make up
```

The application will be available at:
- Website: http://localhost:3636
- Admin: http://localhost:3636/admin

## Docker Commands

### Using docker-compose directly:
```bash
docker-compose up -d              # Start in background
docker-compose down               # Stop containers
docker-compose logs -f            # View logs
docker-compose restart            # Restart all services
docker-compose exec web bash      # Access web container shell
```

### Using Makefile:
```bash
make build        # Build containers
make up           # Start containers
make down         # Stop containers
make logs         # View logs
make shell        # Django shell
make migrate      # Run migrations
make superuser    # Create superuser
make test         # Run tests
make clean        # Remove everything
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for Docker)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=abhirang_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

## URL Structure

### Public URLs
- `/` - Homepage
- `/products/` - Product list
- `/products/<slug>/` - Product detail
- `/products/category/<slug>/` - Category products
- `/products/search/` - Search results
- `/cart/` - Shopping cart

### Account URLs
- `/accounts/login/` - User login
- `/accounts/signup/` - User registration
- `/accounts/profile/` - User profile (requires login)
- `/accounts/profile/?tab=overview` - Profile overview
- `/accounts/profile/?tab=personal` - Personal information
- `/accounts/profile/?tab=security` - Security settings
- `/accounts/profile/?tab=addresses` - Address management
- `/accounts/profile/?tab=orders` - Order history
- `/accounts/logout/` - Logout

### Admin URL
- `/admin/` - Django admin panel

## Database Models

### User & Profile
- Extended Django User model
- Profile with bio, gender, phone, profile picture
- Address model for multiple shipping addresses

### Products
- Product model with name, description, price, images
- Category model for product organization

### Cart
- Cart model linked to users
- CartItem model for cart contents

## Development Notes

### Design Philosophy
- Clean, minimal aesthetic (no colorful gradients or animations)
- White/gray/black color scheme
- Simple, functional UI elements
- Mobile responsive design

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# In Docker
docker-compose exec web python manage.py collectstatic
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# In Docker
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test products

# In Docker
docker-compose exec web python manage.py test
```

## Deployment Considerations

### For Production:
1. Set `DEBUG=False`
2. Generate new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` with your domain
4. Use PostgreSQL instead of SQLite
5. Set up static file serving (WhiteNoise or CDN)
6. Configure media file storage (S3 or similar)
7. Use HTTPS with SSL certificates
8. Set up proper logging
9. Use environment-specific settings
10. Set up backup strategy for database

### Security Checklist:
- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use strong database passwords
- [ ] Enable CSRF protection
- [ ] Set up HTTPS
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Regular security updates

## Troubleshooting

### Common Issues:

**Port already in use:**
```bash
# Find and kill process using port 3636
lsof -ti:3636 | xargs kill -9
```

**Database connection errors:**
```bash
# Restart database container
docker-compose restart db

# Check database logs
docker-compose logs db
```

**Static files not loading:**
```bash
# Collect static files
python manage.py collectstatic --clear

# In Docker
docker-compose exec web python manage.py collectstatic --noinput
```

**Migration conflicts:**
```bash
# Show migrations
python manage.py showmigrations

# Fake a migration
python manage.py migrate --fake appname migration_name
```

## Contributing
1. Create feature branch
2. Make changes with clear commits
3. Test thoroughly
4. Submit pull request

## License
[Add your license here]

## Contact
[Add contact information]
