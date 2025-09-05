#!/bin/bash

echo "🚀 Setting up X Scraper Backend..."

if [ ! -f "manage.py" ]; then
    echo "❌ Error: Run from backend directory"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "📦 Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with credentials"
fi

echo "🗄️  Running migrations..."
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo "Run: python manage.py runserver"