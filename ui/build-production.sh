#!/bin/bash
# prplOS LCM Log Analysis System - Frontend Production Build Script

set -e

echo "🚀 Building prplOS LCM Log Analysis System Frontend for Production"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the ui directory."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js 18+ is required. Current version: $(node --version)"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist node_modules/.vite

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Type checking (optional - skip for now)
# echo "🔍 Running TypeScript type checking..."
# npm run type-check

# Linting (optional - skip for now)
# echo "🔍 Running ESLint..."
# npm run lint

# Build the application
echo "🏗️  Building application..."
npx vite build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "📁 Build output: $(du -sh dist | cut -f1)"

# Show build info
echo ""
echo "📊 Build Information:"
echo "  - Build size: $(du -sh dist | cut -f1)"
echo "  - Files: $(find dist -type f | wc -l)"
echo "  - Main bundle: $(ls -lh dist/assets/*.js | head -1 | awk '{print $5}')"
echo "  - CSS bundle: $(ls -lh dist/assets/*.css | head -1 | awk '{print $5}')"

echo ""
echo "🎉 Frontend is ready for production deployment!"
