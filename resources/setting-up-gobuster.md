## Tooling — Gobuster / Directory Enumeration

VM fix (VirtualBox NAT + IPv6 causes curl/gobuster TLS resets and timeouts):
  sudo nano /etc/sysctl.conf
  # add:
  net.ipv6.conf.all.disable_ipv6 = 1
  net.ipv6.conf.default.disable_ipv6 = 1
  net.ipv6.conf.lo.disable_ipv6 = 1
  sudo sysctl -p

Build combined wordlist (custom paths + seclists):
```bash
cat ~/custom-paths.txt /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt > ~/combined.txt
  sort -u ~/combined.txt -o ~/combined.txt
```

Run:
```bash
gobuster dir -u https://<target> -w ~/combined.txt -x php,txt,bak,zip -t 20 --timeout 15s
```

Notes:
  - testphp.vulnweb.com: unreliable, blocks/drops scanner traffic — don't use for tool testing
  - scanme.nmap.org: reliable, explicitly sanctioned for scan practice — use this to validate tooling
  - 403 on a path ≠ not found — means it exists but access is denied; worth noting, not necessarily exploitable
  - Writable+web-accessible directory pattern (e.g. /images/, /uploads/) relevant both for info-disclosure recon AND as a command-injection output-redirection target
