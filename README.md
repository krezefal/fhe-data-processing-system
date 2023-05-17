# FHE data processing system
Secure data processing system using homomorphic encryption

## Install requirements
1. `pip install -r requirements.txt`
1. `pip install git+https://github.com/krezefal/homomorphic-polynomial-system.git`

## Build / pull docker image
### Build & run
1. `cd database`
1. `sudo docker build -t secure-remote-memory ./`
1. `sudo docker run -d --name secure-remote-memory-container -p 5432:5432 secure-remote-memory`

### Pull & run
1. `sudo docker pull krezefal/secure-remote-memory`
1. `sudo docker run -d --name secure-remote-memory-container -p 5432:5432 krezefal/secure-remote-memory`

## Generating self-signed OpenSSL certificates

`openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
`

It is important to specify the IP address of the server as **Common Name** while generating certs.

## Run the app
`python3 demo_app.py`
