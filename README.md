# FHE data processing system
Secure data processing system using homomorphic encryption

## Install requirements
1. `pip install -r requirements.txt`
2. `pip install git+https://github.com/krezefal/homomorphic-polynomial-system.git`

## Build / pull docker image
### Build & run
1. `sudo docker build -t secure-remote-memory ./`
2. `sudo docker run -d --name secure-remote-memory-container -p 5432:5432 secure-remote-memory`

### Pull & run
1. `sudo docker pull krezefal/secure-remote-memory`
2. `sudo docker run -d --name secure-remote-memory-container -p 5432:5432 krezefal/secure-remote-memory`

## Run the app
`python3 test_app.py`
