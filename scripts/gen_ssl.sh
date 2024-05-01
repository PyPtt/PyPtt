
#openssl genrsa -out key.pem 2048
openssl ecparam -genkey -name prime256v1 -out key.pem
#openssl genpkey -algorithm ed25519 -out key.pem

openssl req -new -key key.pem -out csr.pem -subj "/C=TW/ST=State/L=City/O=Organization/OU=Organizational Unit/CN=Common Name"
openssl x509 -req -days 3650 -in csr.pem -signkey key.pem -out cert.pem

echo "Generated key.pem, csr.pem, and cert.pem"
