#!/bin/bash

# Family Album Deployment Script
# Author: Auto-generated
# Date: 2026-05-10

echo "=========================================="
echo "  Family Album Deployment Script"
echo "=========================================="

# Configuration
SERVER="root@106.53.60.19"
PROJECT_DIR="/www/wwwroot/Family_Album"
LOCAL_DIR="/Users/flex/Documents/git/Family_Album"

echo ""
echo "1. Collecting static files locally..."
cd "$LOCAL_DIR"
python3 manage.py collectstatic --noinput

echo ""
echo "2. Uploading database..."
scp "$LOCAL_DIR/db.sqlite3" "$SERVER:$PROJECT_DIR/db.sqlite3"

echo ""
echo "3. Uploading settings.py..."
scp "$LOCAL_DIR/family_album/settings.py" "$SERVER:$PROJECT_DIR/family_album/settings.py"

echo ""
echo "4. Uploading media files..."
scp -r "$LOCAL_DIR/media/" "$SERVER:$PROJECT_DIR/"

echo ""
echo "5. Uploading staticfiles..."
scp -r "$LOCAL_DIR/staticfiles/" "$SERVER:$PROJECT_DIR/"

echo ""
echo "6. Uploading templates..."
scp -r "$LOCAL_DIR/templates/" "$SERVER:$PROJECT_DIR/"

echo ""
echo "7. Uploading photos app..."
scp -r "$LOCAL_DIR/photos/" "$SERVER:$PROJECT_DIR/"

echo ""
echo "8. Fixing permissions..."
ssh "$SERVER" "chown -R www:www $PROJECT_DIR/media/"

echo ""
echo "9. Reloading Nginx..."
ssh "$SERVER" "service nginx reload"

echo ""
echo "10. Restarting Django..."
ssh "$SERVER" "cd $PROJECT_DIR && source venv/bin/activate && kill -9 \$(lsof -i :8000 -t) 2>/dev/null; gunicorn --bind 0.0.0.0:8000 family_album.wsgi:application --daemon"

echo ""
echo "=========================================="
echo "  Deployment completed successfully!"
echo "  Website: http://106.53.60.19"
echo "=========================================="