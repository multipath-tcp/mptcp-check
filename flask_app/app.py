#!/app/venv/bin/python3

from flask import Flask, request, render_template, send_from_directory
from subprocess import check_output
import os

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(error):
    # Render a custom 404 template
    return render_template('404.html'), 404

@app.route("/")
def mptcp_status_page():
    """
    Flask route to display MPTCP connection status.

    Retrieves the visitor's IP and port, checks for MPTCP data in the connections dictionary,
    and renders the webpage with the connection status.

    Returns:
    Rendered webpage with connection status and MPTCP version if established.
    """

    addr = request.remote_addr
    port = request.environ.get('REMOTE_PORT')
    user = request.environ.get('HTTP_USER_AGENT')

    #ipv6 compatibility
    if ":" in addr:
        addr = f"{addr}:{port}"

    try:
        conn = check_output(["ss", "-MnH", "dst", f"{addr}", "dport", f"{port}"]).decode("ascii")
        if conn.startswith("ESTAB"):
            state_message = 'are'
            state_class = 'success'
        else:
            state_message = 'are not'
            state_class = 'fail'
    except Exception as e:
        state_message = '[error: ' + str(e) + ']'
        state_class = 'error'

    if user.startswith("curl"):
        return "You " + state_message + " using MPTCP.\n"

    return render_template('index.html', state_message=state_message, state_class=state_class)

#this is just to be sure that certbot is able to update
#normally the request is handled by lighttpd
@app.route('/.well-known/<path:filename>')
def serve_cert(filename):
    return send_from_directory('/var/www/.well-known/', filename)

if __name__ == "__main__":
    app.run(host="::", port=80, debug=True)

