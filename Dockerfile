FROM ubuntu:25.04

# Update package lists and install necessary dependencies
RUN apt-get update && apt-get dist-upgrade -y && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    openssl \
    lighttpd \
    iproute2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Setup flask app
COPY flask_app/ /flask_app/
RUN /app/venv/bin/pip3 install --no-cache-dir -r /flask_app/requirements.txt
RUN chmod +x /flask_app/app.*

EXPOSE 80 443

CMD ["/usr/sbin/lighttpd", "-D", "-f", "/lighttpd.conf"]
