from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import requests
import os
import json

# Function to check if a given certificate code is valid
# Parameters:
# 	MANDATORY
# 		?code -> the certificate code to be checked
# 	OPTIONAL
#		?expiry -> if provided, returns TRUE or FALSE, if the certificate is valid on a given date
# 		?email -> if provided, returns TRUE or FALSE, if the certificate belongs to the given email
#		?username -> if provided, returns TRUE or FALSE, if the certificate belongs to the given username

class handler(BaseHTTPRequestHandler):

	def do_GET(self):
		try: 
			# Parse input parameters /?code=7728373450WM
			url_path = urlparse(self.path)
			url_params = parse_qs(url_path.query)
			cert_code = url_params.get('code', [''])[0]
			cert_expiry = url_params.get('expiry', [''])[0]
			cert_email = url_params.get('email', [''])[0]
			cert_user = url_params.get('username', [''])[0]
		
			# Check that cert_code is provided
			if not cert_code:
				self.send_response(400)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(f'Missing "code" query parameter in path: {url_path} and params: {url_params}'.encode('utf-8'))
				return
			
			# Create new request URL with code and ws_token
			ws_token = os.environ.get('ws_token', '')
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
			
			res_obj = json.loads(response.content.decode('UTF-8'))

			# Return the response
			self.send_response(response.status_code)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			
			# if the certificate code is false
			if res_obj['valid'] == False:
				self.wfile.write(str(False).encode('utf-8'))
				return

			# If no additional parameters are given, return the full response
			if not cert_expiry and not cert_email and not cert_user:
				self.wfile.write(response.content)
				return

			# Some parameters were given, so let's check them and return TRUE or FALSE
			res = True

			if cert_expiry: # check expiry date
				if res_obj['expires'] != "NEVER":
					res = cert_expiry <= res_expiry
			if res and cert_email: # check the email is correct
				res = cert_email == res_obj['email']
			if res and cert_user: # check the username
				res = cert_user == res_obj['username']
			
			self.wfile.write(str(res).encode('utf-8'))
			return
			
		except Exception as e:
			self.send_response(500)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
			return