FROM mongo:7

# Create directory for MongoDB data
RUN mkdir -p /data/db

# Expose MongoDB port
EXPOSE 27017

# Use the default MongoDB entrypoint
CMD ["mongod", "--bind_ip_all"]
