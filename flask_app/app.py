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
    host = request.host_url

    #ipv6 compatibility
    if ":" in addr:
        addr = f"{addr}:{port}"

    state_info = ''
    state_error = ''
    try:
        conn = check_output(["ss", "-MnH", "dst", f"{addr}", "dport", f"{port}"]).decode("ascii")
        if conn.startswith("ESTAB"):
            state_message = 'are'
            state_class = 'success'
            state_info = 'Nice, even your browser is supporting MPTCP!'
        else:
            state_message = 'are not'
            state_class = 'fail'
            state_info = 'Your browser <strong>is not</strong> supporting MPTCP, but <strong>maybe your system is</strong>, check the cURL command below.'
    except Exception as e:
        state_message = 'are maybe, or maybe not (internal error)'
        state_class = 'error'
        state_error = 'Error: ' + str(e)

    if user.startswith("curl"):
        return "You " + state_message + " using MPTCP.\n"

    return render_template('index.html',
                           state_message=state_message,
                           state_class=state_class,
                           state_info=state_info,
                           state_error=state_error,
                           host=host)

if __name__ == "__main__":
    app.run(host="::", port=80, debug=True)

