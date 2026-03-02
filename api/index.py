from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import os

class handler(BaseHTTPRequestHandler):

	def do_GET(self):
		# Parse input parameter /?code=7728373450WM
		cert_code = parse_qs(urlparse(self.path)).get('code', [''])[0]
		
		# Create new request URL with code and ws_token
		# ws_token = os.environ.get('VERCEL_TOKEN', '')
		ws_token = "06c3dccfbd90b558fe1e780ded1454ac"
		new_url = f"academy.wfdf.sport/webservice/rest/server.php?wstoken={ws_token}&wsfunction=local_validatecert_validate_certificate&moodlewsrestformat=json&code={cert_code}"
		
		# Call the new API
		try:
			req = urllib.request.Request(new_url)
			with urllib.request.urlopen(req) as response:
 				api_response = response.read()
 				status_code = response.status

			# Return the response
			self.send_response(status_code)
			self.send_header('Content-type', 'application/json')
			self.end_headers()
			self.wfile.write(api_response)

		# handle exceptions
		except urllib.error.HTTPError as e:
			self.send_response(e.code)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"HTTP Error: {e.reason}".encode('utf-8'))

		except Exception as e:
			self.send_response(500)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"Error: {str(e)}".encode('utf-8'))