FROM ubuntu:latest

RUN sysctl -w net.mptcp.enabled=1

# Update package lists and install necessary dependencies
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3.12-venv \
    python3-apt \
    openssl \
    lighttpd \
    iproute2 \
    mptcpize \
    autoconf automake libtool m4 pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Setup flask app
COPY flask_app/ /flask_app/
RUN /app/venv/bin/pip3 install --no-cache-dir -r /flask_app/requirements.txt
RUN chmod +x /flask_app/app.*

# setup ighttpd
#RUN lighty-enable-mod fastcgi
COPY lighttpd.conf /
RUN mkdir -p /var/cache/lighttpd/uploads

EXPOSE 80 443

#CMD ["/usr/sbin/lighttpd", "-D", "-f", "/lighttpd.conf"]
CMD ["mptcpize", "run", "/usr/sbin/lighttpd", "-D", "-f", "/lighttpd.conf"]