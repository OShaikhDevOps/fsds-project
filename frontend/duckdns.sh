#!/bin/bash
# duckdns.sh

# The subdomain and token will be passed as Environment Variables from ECS
echo "Updating DuckDNS for ${SUBDOMAIN}.duckdns.org..."

# Send the update request to DuckDNS
# It automatically detects your Public IP when you call this URL
RESPONSE=$(curl -s "https://www.duckdns.org/update?domains=${SUBDOMAIN}&token=${TOKEN}&ip=")

if [ "$RESPONSE" = "OK" ]; then
    echo "DuckDNS updated successfully!"
else
    echo "DuckDNS update FAILED. Response: $RESPONSE"
fi

# Now start the actual Streamlit app
# Replace 8080 with your actual port if different
streamlit run streamlit_app.py --server.port 8080 --server.address 0.0.0.0