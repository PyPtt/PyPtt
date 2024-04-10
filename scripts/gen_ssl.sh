
openssl genrsa -out key.pem 2048
openssl req -new -key key.pem -out csr.pem
openssl x509 -req -days 3650 -in csr.pem -signkey key.pem -out cert.pem

mv key.pem cert.pem ./PyPtt/ssl/