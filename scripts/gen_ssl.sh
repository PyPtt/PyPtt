
#openssl genrsa -out key.pem 2048
openssl ecparam -genkey -name prime256v1 -out key.pem
#openssl genpkey -algorithm ed25519 -out key.pem

openssl req -new -key key.pem -out csr.pem
openssl x509 -req -days 3650 -in csr.pem -signkey key.pem -out cert.pem

mv key.pem cert.pem ./PyPtt/ssl/
rm csr.pem