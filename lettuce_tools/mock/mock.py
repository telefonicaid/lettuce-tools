# -*- coding: utf-8 -*-

import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import argparse


class RequestHandler(BaseHTTPRequestHandler):
    """
    Handler for the HTTP requests received by the mock.
    """

    responses_qeues = dict()
    requests_qeues = dict()

    def do_GET(self):
        """
        Handle the GET requests.
        """
        if "mock_configurations" in self.path:
            """Send the oldest request received in the path specified."""
            resource = self.path.replace("/mock_configurations", "")
            self.recover_request(resource)
            self.log_message("%s", "GET con mock config")

        elif "queues" in self.path:
            """Send the current queues for requests and responses."""
            self.get_queues()

        else:
            """Otherwise, serve the previously uploaded content."""
            self.store_request(self.path, "GET")
            self.serve_response()

    def do_DELETE(self):
        """
        Handle the DELETE requests.
        """
        if "queues" in self.path:
            """Empty the current queues for requests and responses."""
            self.empty_queues()
        else:
            """Otherwise, serve the previously uploaded content."""
            self.store_request(self.path, "DELETE")
            self.serve_response()

    def do_PUT(self):
        """
        Handle the PUT requests.
        """
        """Serve the previously uploaded content."""
        self.store_request(self.path, "PUT")
        self.serve_response()

    def do_POST(self):
        """
        Handle the POST requests.
        """
        if "mock_configurations" in self.path:
            """Store the response to be served in the path specified."""
            resource = self.path.replace("/mock_configurations", "")
            self.store_response(resource)

        else:
            """Otherwise, serve the previously uploaded content."""
            self.store_request(self.path, "POST")
            self.serve_response()

    def recover_request(self, resource):
        """
        Return the oldest stored request to the resource
        """
        try:
            request_info = self.requests_qeues[resource].pop(0)
        except:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

        """Send in the body the request information, the POST body or GET params
        ."""
        self.wfile.write(json.dumps(request_info))

    def store_request(self, resource, method):
        """
        Stores the information provided in the request
        """
        content_type = self.headers.getheader('Content-Type')
        body = ""
        query_params = ""

        """Obtain body in post requests"""
        try:
            content_length = int(self.headers.getheader('Content-Length'))
            body = self.rfile.read(content_length)
        except:
            """ No body means that it could be a GET request """
            if len(resource.split("?")) > 1:
                query_params = resource.split("?").pop()

        request_data = {"body": body, "query_params": query_params, "content_type": content_type, "method": method}

        """Add the content to the configured resource queue"""
        if resource.split("?").pop(0) not in self.requests_qeues:
            self.requests_qeues[resource.split("?").pop(0)] = []
            self.requests_qeues[resource.split("?").pop(0)].append(request_data)
        else:
            self.requests_qeues[resource.split("?").pop(0)].append(request_data)

    def store_response(self, resource):
        """
        Store the content of the configuration request received so that it can
        be used later to build responses.
        The content is expected to be a JSON element with the path of the
        request as key and the following JSON elements as value:
        - status_code: HTTP status code to be sent in the response.
        - headers: headers to be included in the response.
        - body: body to be included in the response.
        - delay: delay in seconds before sending the response.
        """

        """Get the content from the POST request."""
        content_length = int(self.headers.getheader('Content-Length'))
        body = self.rfile.read(content_length)
        response = json.loads(body)

        """Add the content to the configured resource queue"""
        if resource not in self.responses_qeues:
            self.responses_qeues[resource] = []
            self.responses_qeues[resource].append(response)
        else:
            self.responses_qeues[resource].append(response)

        """Add the content to the dictionary of responses."""
        #self.responses_dict.update(response)

        """Send the response to the request."""
        self.send_response(204)
        self.end_headers()

    def serve_response(self):
        """Get the data for the response from the dictionary of responses."""
        try:
            response_info = self.responses_qeues[self.path.split("?").pop(0)].pop(0)
        except:
            self.send_response(404)
            self.end_headers()
            return

        """If response_info has also a delay set, wait the time specified."""
        if "delay" in response_info:
            time.sleep(response_info["delay"])

        """Send the status code."""
        status_code = response_info["status_code"]
        self.send_response(status_code)

        """Send specific headers, if any."""
        if "headers" in response_info:
            headers = response_info["headers"]
            for header_name in headers.keys():
                self.send_header(header_name, headers.get(header_name))
        self.end_headers()

        """Send the body, if any."""
        if "body" in response_info:
            body = response_info["body"]
            self.wfile.write(json.dumps(body))

    def get_queues(self):
        """Get the requests and responses queues."""
        try:
            body = dict()
            body.update({"requests": self.requests_qeues})
            body.update({"responses": self.responses_qeues})
            self.wfile.write(json.dumps(body))
        except:
            self.send_response(500)
            self.end_headers()
            return

    def empty_queues(self):
        """Empty the requests and responses queues."""
        self.requests_qeues.clear()
        self.responses_qeues.clear()
        self.send_response(204)
        self.end_headers()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mock server for REST APIs")
    parser.add_argument("--host", type=str, nargs="?", default="127.0.0.1",
                        help="Host where to start the mock (127.0.0.1 by default)")
    parser.add_argument("--port", type=int, nargs="?", default=8000,
                        help="Port where to start the mock (8000 by default)")
    args = parser.parse_args()
    try:
        mock_server = HTTPServer((args.host, args.port), RequestHandler)
        print "Starting mock server."
        mock_server.serve_forever()
    except KeyboardInterrupt:
        print "Stopping mock server."
        mock_server.server_close()
        print "Mock stopped."
    except Exception as e:
        print "Unexpected error: " + str(e)
