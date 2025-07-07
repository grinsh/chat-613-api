import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

print("Certificates loaded from:", certifi.where())