# Web Spelling Quiz

A web-based version of the spelling quiz application built with Flask, designed to run on Apache web servers.

## Features

- 🎯 **Complete K-12 Coverage**: 860+ words spanning grades 1-12
- 🎵 **Text-to-Speech**: Browser-based audio pronunciation of words
- 📊 **Progress Tracking**: Session statistics and performance analytics
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🔒 **Secure**: Built with security best practices
- 🚀 **Easy Deployment**: Automated Apache deployment script

## Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python3 web_quiz.py
   ```

3. **Open in Browser**:
   ```
   http://localhost:5000
   ```

### Production Deployment on Apache

1. **Prepare the Server** (Ubuntu/Debian):
   ```bash
   sudo apt update
   sudo apt install apache2 apache2-dev python3 python3-venv python3-pip
   ```

2. **Deploy the Application**:
   ```bash
   ./deploy.sh
   ```

3. **Configure Domain** (edit `/etc/apache2/sites-available/spelling-quiz.conf`):
   ```apache
   ServerName your-domain.com
   ServerAlias www.your-domain.com
   ```

4. **Restart Apache**:
   ```bash
   sudo systemctl restart apache2
   ```

## Architecture

### Application Structure
```
word_quiz/
├── web_quiz.py          # Flask application
├── wsgi.py              # WSGI entry point
├── word_lists.py        # Word dictionary
├── requirements.txt     # Python dependencies
├── deploy.sh            # Deployment script
├── apache-vhost.conf    # Apache configuration
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── index.html       # Home page
    ├── setup.html       # Quiz setup
    ├── quiz.html        # Quiz interface
    ├── results.html     # Results page
    └── statistics.html  # Statistics page
```

### Database Schema
The application uses SQLite with the following tables:

- **sessions**: Quiz session data and results
- **users**: User accounts (future feature)

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (change in production)
- `DATABASE`: SQLite database path (default: `quiz_sessions.db`)

### Apache Configuration
The application includes a complete Apache virtual host configuration with:
- WSGI deployment
- Security headers
- SSL/HTTPS support (optional)
- Static file serving
- Logging configuration

## Features Detail

### Quiz Modes
- **Sight Words Only**: Focus on high-frequency sight words
- **Regular Words Only**: Standard vocabulary words
- **50/50 Mix**: Equal mix of sight and regular words
- **Random Mix**: All available words

### Grade Level Selection
- Single grade: Focus on specific grade level
- Multiple grades: Mix words from different grade levels
- K-12 coverage: Elementary through high school

### Statistics Tracking
- Session-by-session performance
- Overall accuracy statistics
- Word difficulty analysis
- Progress over time

## Security Features

- CSRF protection with Flask sessions
- SQL injection prevention with parameterized queries
- XSS protection with template escaping
- Security headers in Apache configuration
- Session management

## Deployment Options

### Option 1: Apache + mod_wsgi (Recommended)
- Use the provided `deploy.sh` script
- Automatic setup and configuration
- Production-ready deployment

### Option 2: Gunicorn + Reverse Proxy
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:application

# Configure Apache reverse proxy
ProxyPass / http://localhost:8000/
ProxyPassReverse / http://localhost:8000/
```

### Option 3: Docker (Future Enhancement)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application"]
```

## Customization

### Adding New Words
Edit `word_lists.py` and add entries to the `word_dictionary`:
```python
"newword": {
    "grade_levels": [3, 4], 
    "sight_word": False, 
    "definition": "definition here"
}
```

### Styling
Modify the CSS in `templates/base.html` or add custom stylesheets.

### Audio Settings
The application uses the Web Speech API. Customize in `templates/quiz.html`:
```javascript
utterance.rate = 0.8;      // Speaking rate
utterance.pitch = 1.0;     // Voice pitch
utterance.volume = 1.0;    // Volume level
```

## Troubleshooting

### Common Issues

1. **Apache WSGI Module Not Found**:
   ```bash
   sudo apt install libapache2-mod-wsgi-py3
   sudo a2enmod wsgi
   ```

2. **Permission Errors**:
   ```bash
   sudo chown -R www-data:www-data /var/www/spelling-quiz
   sudo chmod -R 755 /var/www/spelling-quiz
   ```

3. **Database Permissions**:
   ```bash
   sudo chown www-data:www-data quiz_sessions.db
   sudo chmod 664 quiz_sessions.db
   ```

4. **Audio Not Working**:
   - Ensure HTTPS for production (required by many browsers)
   - Check browser compatibility with Web Speech API
   - Verify microphone permissions if needed

### Log Locations
- Apache Error Log: `/var/log/apache2/spelling-quiz_error.log`
- Apache Access Log: `/var/log/apache2/spelling-quiz_access.log`
- Application Database: `/var/www/spelling-quiz/quiz_sessions.db`

## Performance Optimization

### Database
- Regular database cleanup of old sessions
- Index optimization for frequent queries
- Consider PostgreSQL for high-traffic sites

### Caching
- Enable Apache mod_cache for static content
- Use Flask-Caching for word list caching
- Browser caching headers for assets

### Monitoring
- Set up log rotation
- Monitor disk space usage
- Track database size growth
- Performance monitoring with tools like New Relic

## License

This project extends the original spelling quiz game for web deployment.

## Support

For deployment issues or questions, check:
1. Apache error logs
2. Application logs
3. Browser developer console
4. Network connectivity

The application is designed to be self-contained and easy to deploy on standard LAMP stack servers.