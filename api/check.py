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

class handler(BaseHTTPRequestHandler):

	def do_GET(self):
		try: 
			# Parse input parameters /?code=7728373450WM
			url_path = urlparse(self.path)
			url_params = parse_qs(url_path.query)
			cert_code = url_params.get('code', [''])[0]
			cert_expiry = url_params.get('expiry', [''])[0]
			cert_email = url_params.get('email', [''])[0]
		
			# Check that cert_code is provided
			if not cert_code:
				self.send_response(400)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(f'Missing "code" query parameter in path: {url_path} and params: {url_params}')
				return
			
			# Create new request URL with code and ws_token
			ws_token = os.environ.get('ws_token', '')
			#ws_token = "06c3dccfbd90b558fe1e780ded1454ac"
			new_url = f"https://academy.wfdf.sport/webservice/rest/server.php?wstoken={ws_token}&wsfunction=local_validatecert_validate_certificate&moodlewsrestformat=json&code={cert_code}"
			
			# Call the wrapped API
			response = requests.get(new_url,headers={"Authorization": f"Bearer {ws_token}"},timeout=10)
			
			# Return error, if we don't receive 200–299 status code
			if 200 > response.status_code or 299 < response.status_code: 
				self.send_response(response.status_code)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
				return
			
			res_obj = json.loads(response.content.decode('UTF-8'))
			res_email = res_obj['email']
			res_expiry = "9999-12-31"	# mapping over NEVER
			if res_obj['expires'] != "NEVER":
				res_expiry = res_obj['expires']

			# Return the response
			self.send_response(response.status_code)

			# If cert_expiry or cert_email is set, return TRUE or FALSE			
			if cert_expiry or cert_email:
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				if cert_expiry and cert_email:
					self.wfile.write(str(cert_expiry <= res_expiry and cert_email == res_email).encode('utf-8'))
					return
				if cert_expiry:
					
					self.wfile.write(str(cert_expiry <= res_expiry).encode('utf-8'))
					return
				else: 
					self.wfile.write(str(cert_email == res_email).encode('utf-8'))
					return
			
			# Else return the full response
			self.send_header('Content-type', response.headers.get('Content-Type', 'application/json'))
			self.end_headers()
			self.wfile.write(response.content)
			return
			
		except Exception as e:
			self.send_response(500)
			self.send_header('Content-type', 'text/plain')
			self.end_headers()
			self.wfile.write(f"Error: {str(e)}".encode('utf-8'))
			return