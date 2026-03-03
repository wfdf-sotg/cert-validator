from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import requests
import os
import json

# Function to check if a comma-separated list of certificate codes are valid
# Parameters:
# 	MANDATORY
# 		?codes -> the list of certificate codes to be checked
#		?expiry -> returns the certificate codes that are valid and invalid

class handler(BaseHTTPRequestHandler):

	def do_GET(self):
		try: 
			# Parse input parameters /?codes=7728373450WM,123456789XY
			url_path = urlparse(self.path)
			url_params = parse_qs(url_path.query)
			cert_codes = url_params.get('codes', [''])[0].split(',')
			cert_expiry = url_params.get('expiry', [''])[0]
		
			# Check that cert_code is provided
			if cert_codes.len() == 0 or not cert_expiry:
				self.send_response(400)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(f'Missing "code" or "expiry" query parameter in path: {url_path} and params: {url_params}')
				return

			# Create answer object
			ans = json.loads('{"valid":[],"invalid":[]}')

			# Create new request URL with code and ws_token
			ws_token = os.environ.get('ws_token', '')
			for cert_code in cert_codes:
				new_url = f"https://academy.wfdf.sport/webservice/rest/server.php?wstoken={ws_token}&wsfunction=local_validatecert_validate_certificate&moodlewsrestformat=json&code={cert_code}"
			
				# Call the wrapped API
				response = requests.get(new_url,timeout=10)
			
				# Return error, if we don't receive 200–299 status code
				if 200 > response.status_code or 299 < response.status_code: 
					self.send_response(response.status_code)
					self.send_header('Content-type', 'text/plain')
					self.end_headers()
					self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
					return
				
				# Parse the expiry date
				res_obj = json.loads(response.content.decode('UTF-8'))
				res_valid = res_obj['valid']
				res_expiry = "9999-12-31"	# mapping over NEVER
				if res_obj['expires'] != "NEVER":
					res_expiry = res_obj['expires']

				# Compare the date and validity and add to the correct array
				if res_valid and cert_expiry <= res_expiry:
					ans['valid'].append(cert_code)
				else:
					ans['invalid'].append(cert_code)

			# Return the full response object
			self.send_header('Content-type', response.headers.get('Content-Type', 'application/json'))
			self.end_headers()
			self.wfile.write(ans)
			return
			
		except Exception as e:
			self.send_response(500)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
			return