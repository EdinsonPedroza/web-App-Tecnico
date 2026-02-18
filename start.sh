#!/bin/bash
# Use PORT from Railway, default to 80
export PORT="${PORT:-80}"

# Replace the listen port in nginx config
sed "s/listen 80;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start supervisord (which manages both nginx and the backend)
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
