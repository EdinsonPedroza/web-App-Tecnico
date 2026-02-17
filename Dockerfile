# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app

COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY frontend/ .

# In the single-container setup, nginx proxies /api to the backend on localhost
ARG REACT_APP_BACKEND_URL=""
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

# Stage 2: Final image with Python backend + nginx
FROM python:3.11-slim

# Install nginx and supervisord
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Set up the backend
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
RUN mkdir -p uploads

# Copy the built frontend into nginx's html directory
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy nginx and supervisord configuration
COPY nginx.single-container.conf /etc/nginx/conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
