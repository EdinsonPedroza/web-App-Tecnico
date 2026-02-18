#!/bin/bash
set -e  # Exit on error

# Use PORT from Railway, default to 80
export PORT="${PORT:-80}"

# Validate PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: PORT must be numeric, got: $PORT"
    exit 1
fi

# Replace the listen port in nginx config
sed "s/listen 80;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Verify the substitution succeeded
if ! grep -q "listen ${PORT};" /etc/nginx/conf.d/default.conf; then
    echo "ERROR: Failed to configure nginx to listen on port ${PORT}"
    exit 1
fi

echo "Nginx configured to listen on port ${PORT}"

# Start supervisord (which manages both nginx and the backend)
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
