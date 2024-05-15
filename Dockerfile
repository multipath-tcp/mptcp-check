FROM ubuntu:latest

# Update package lists and install necessary dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3.12-venv \
    python3-apt \
    openssl \
    lighttpd \
    iproute2 \
    mptcpize \
    autoconf automake libtool m4 pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Setup flask app
COPY flask_app/ /flask_app/
RUN /app/venv/bin/pip3 install --no-cache-dir -r /flask_app/requirements.txt
RUN chmod +x /flask_app/app.*

EXPOSE 80 443

# mptcpize will not be needed with lighttpd > 1.4.76 and the option "server.network-mptcp"
CMD ["mptcpize", "run", "/usr/sbin/lighttpd", "-D", "-f", "/lighttpd.conf"]