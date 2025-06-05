#!/bin/bash

echo "🚀 Setting up X Advanced Search Backend..."

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual credentials"
fi

# Run the init script to create app structure
echo "🏗️  Creating app structure..."
python scripts/create_init_files.py

# Run migrations
echo "🗄️  Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Default superuser:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠️  Remember to:"
echo "  1. Update .env with your X platform credentials"
echo "  2. Change the default superuser password"
echo "  3. Install and run Redis for Celery (optional)"