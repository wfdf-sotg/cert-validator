from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import requests
import os

class handler(BaseHTTPRequestHandler):

	def do_GET(self):
		try: 
			# Parse input parameter /?code=7728373450WM
			url_path = urlparse(self.path)
			url_params = parse_qs(url_path.query)
			cert_code = url_params.get('input', [''])[0]
		
			if not input_string:
				self.send_response(400)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(b'Missing "code" query parameter')
				return
			
			# Create new request URL with code and ws_token
			# ws_token = os.environ.get('VERCEL_TOKEN', '')
			ws_token = "06c3dccfbd90b558fe1e780ded1454ac"
			new_url = f"academy.wfdf.sport/webservice/rest/server.php?wstoken={ws_token}&wsfunction=local_validatecert_validate_certificate&moodlewsrestformat=json&code={cert_code}"
			
			# Call the new API
			response = requests.get(target_url,headers={"Authorization": f"Bearer {ws_token}"},timeout=10)
			
			# 4. Return the response
			self.send_response(response.status_code)
			self.send_header('Content-type', response.headers.get('Content-Type', 'application/json'))
			self.end_headers()
			self.wfile.write(response.content)
			
		except Exception as e:
			self.send_response(500)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"Error: {str(e)}".encode('utf-8'))