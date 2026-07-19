#!/bin/bash

# Web Spelling Quiz Deployment Script
# This script helps deploy the Flask application to an Apache web server

echo "🎯 Web Spelling Quiz Deployment Script"
echo "======================================="

# Configuration
APP_NAME="spelling-quiz"
DEPLOY_DIR="/var/www/${APP_NAME}"
VENV_DIR="${DEPLOY_DIR}/venv"
APACHE_SITE="${APP_NAME}.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons."
   print_warning "Please run as a user with sudo privileges."
   exit 1
fi

# Check if Apache is installed
if ! command -v apache2 &> /dev/null; then
    print_error "Apache2 is not installed. Please install it first:"
    echo "  sudo apt update"
    echo "  sudo apt install apache2 apache2-dev"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install it first."
    exit 1
fi

print_step "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-venv python3-pip libapache2-mod-wsgi-py3

print_step "Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown $USER:$USER "$DEPLOY_DIR"

print_step "Copying application files..."
cp -r . "$DEPLOY_DIR/"
cd "$DEPLOY_DIR"

print_step "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

print_step "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

print_step "Setting up database..."
python3 -c "from web_quiz import init_db; init_db()"

print_step "Setting file permissions..."
sudo chown -R www-data:www-data "$DEPLOY_DIR"
sudo chmod -R 755 "$DEPLOY_DIR"
sudo chmod 644 "$DEPLOY_DIR/quiz_sessions.db" 2>/dev/null || true

print_step "Configuring Apache virtual host..."
sudo cp apache-vhost.conf "/etc/apache2/sites-available/${APACHE_SITE}"

# Enable required Apache modules
print_step "Enabling Apache modules..."
sudo a2enmod wsgi
sudo a2enmod headers
sudo a2enmod rewrite

# Enable the site
print_step "Enabling the site..."
sudo a2ensite "$APACHE_SITE"

# Test Apache configuration
print_step "Testing Apache configuration..."
if sudo apache2ctl configtest; then
    print_success "Apache configuration is valid"
else
    print_error "Apache configuration has errors"
    exit 1
fi

# Restart Apache
print_step "Restarting Apache..."
sudo systemctl restart apache2

if sudo systemctl is-active --quiet apache2; then
    print_success "Apache is running"
else
    print_error "Failed to start Apache"
    exit 1
fi

echo ""
print_success "Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Update DNS to point to this server"
echo "   2. Edit /etc/apache2/sites-available/${APACHE_SITE} with your domain name"
echo "   3. Consider setting up SSL/HTTPS"
echo "   4. Set up monitoring and backups"
echo ""
echo "🌐 Access your spelling quiz at: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📁 Application directory: $DEPLOY_DIR"
echo "📊 Database location: $DEPLOY_DIR/quiz_sessions.db"
echo "📝 Apache config: /etc/apache2/sites-available/${APACHE_SITE}"
echo ""
print_warning "Remember to:"
echo "   - Change the secret key in production"
echo "   - Set up regular database backups"
echo "   - Monitor disk space and logs"