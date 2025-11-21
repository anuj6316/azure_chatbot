#!/bin/sh
set -e

# Default to localhost:8000 if not set (for local testing)
# Or use the service name 'backend' which works in Docker Compose
if [ -z "$BACKEND_URL" ]; then
    echo "WARNING: BACKEND_URL is not set. Defaulting to http://backend:8000"
    export BACKEND_URL="http://backend:8000"
fi

# Replace the placeholder with the actual URL
sed "s|__BACKEND_URL__|$BACKEND_URL|g" /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the CMD (nginx)
exec "$@"
