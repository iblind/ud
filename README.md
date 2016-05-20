# ud

## Server setup config, assuming Ubuntu 14.04

1. sudo apt-get install python-pip build-essential libssl-dev libffi-dev python-dev tor privoxy

2. pip install cryptography paramiko dataset BeautifulSoup4 stem

3. /etc/init.d/tor restart 

4. tor --hash-password tor,pwwp

5. a)  nano /etc/tor/torrc    b) uncomment lines pertaining to  port 9051 + pw section (if you need further details, check the sacharya.com post)

6. /etc/init.d/tor restart

7. a) nano /etc/privoxy/config b) uncomment line that ends with 9050 .

8. /etc/init.d/privoxy restart

9. feelsgoodman.jpeg

