#!/usr/bin/env python
"""
Adapted based on
https://gist.github.com/huyng/814831

Initially written by Nathan Hamiel (2010)
"""

# core python modules
import argparse
import logging
import json
import os

# reverse dns
import socket

# web server
import urlparse
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# local modules

# globals
log = None
dns = {}            # IP: host
omit_headers = [
    "Accept-Charset"
]

def lookup_host(ip):
    """ Attempt to associate IP to DNS name, retain cache """
    if ip not in dns:
        try:
            result = socket.gethostbyaddr(ip)
            dns[ip] = result[0]
        except Exception as e:
            log.warning(
                "Failed to determine hostname for '%s': %s"
                % (ip, e)
            )
            return None
    return dns[ip]

class RequestHandler(BaseHTTPRequestHandler):
    """ Simple class to log request messages """

    def do_REQUEST(self):
        """ Handle all request types """

        # omit specific headers as they create too much noise
        for header in omit_headers:
            if header in self.headers:
                self.headers[header] = "<redacted>"

        # retainer simple dict
        headers = {}
        for header in self.headers:
            headers[header] = self.headers[header]

        data = None
        if 'Content-Length' in self.headers:
            data = self.rfile.read(int(self.headers['Content-Length']))

        parsed = urlparse.urlparse(self.path)
        query_components = urlparse.parse_qs(parsed.query, keep_blank_values=True)
        if 'x-forwarded-for' in self.headers:
            ip = self.headers['x-forwarded-for']
            proxy_ip = self.client_address[0]
            proxy_host = lookup_host(proxy_ip)
        else:
            ip = self.client_address[0]
            proxy_ip = None
            proxy_host = None

        host = lookup_host(ip)
        request = {
            "command": self.command,
            "context": parsed.path,
            "path": self.path,
            "query": query_components,
            "ip": ip,
            "host": host,
            "proxy_ip": proxy_ip,
            "proxy_host": proxy_host,
            "headers": headers,
            "data": data
        }
        response = json.dumps(request)
        log.info(response)

        # custom responses
        self.send_response(200)
        self.send_header("Support", "Tool sourced from https://github.com/jason-matthew/reflect")
        self.send_header("Why", "Internal option for whatsmyip")
        if len(query_components) == 1 and query_components.keys()[0] in ["host", "ip"]:
            # return single value if specific key requested
            result = "%s" % request[query_components.keys()[0]]
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(result.encode(encoding='utf_8'))
        else:
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode(encoding='utf_8'))

    do_GET = do_REQUEST
    do_POST = do_REQUEST
    do_HEAD = do_REQUEST
    do_PUT = do_REQUEST
    do_DELETE = do_REQUEST
    do_PATCH = do_REQUEST


def init_logger(name, level=logging.INFO):
    """
    Typically performed once per namesapce
    Re-init logger during subsequent calls
    """
    logger = logging.getLogger(name)
    if logger is not None and len(logger.handlers):
        # ensure logger is not initialized with 1 or more NullHandler objects
        # remove additional NullHandler objects with recursive call
        handler = logger.handlers[0]
        if isinstance(handler, logging.NullHandler):
            logger.removeHandler(handler)
            return init_logger(name, level)

        logger.debug("Logger '%s' already initialized" % name)
        logger.setLevel(level)
        return logger

    log_format = '%(asctime)-15s %(levelname)-8s %(message)s'
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)
    return logger


def main(port):
    log.info('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    log.info("Server stopped")


if __name__ == "__main__":
    log = init_logger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port",
        default=80, type=int,
        help=(
            "Specify the web server port.  If not provided, script "
            "will default to 8080."
        )
    )
    args = parser.parse_args()
    main(args.port)
