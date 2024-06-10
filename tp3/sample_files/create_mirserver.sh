sudo apt update
sudo apt upgrade -y

sudo apt install -y build-essential libpcap-dev libpcre3-dev libdumbnet-dev bison flex zlib1g-dev libtirpc-dev libssl-dev

cd /tmp
wget https://www.snort.org/downloads/snort/daq-2.0.7.tar.gz
tar -xzvf daq-2.0.7.tar.gz
cd daq-2.0.7
./configure
make
sudo make install

cd /tmp
wget http://luajit.org/download/LuaJIT-2.0.5.tar.gz
tar -xzvf LuaJIT-2.0.5.tar.gz
cd LuaJIT-2.0.5
make
sudo make install
sudo ln -s /usr/local/lib/libluajit-5.1.so.2 /usr/lib/libluajit-5.1.so.2
sudo ldconfig

# Copy RPC headers to /usr/include/rpc/
sudo cp /usr/include/tirpc/rpc/* /usr/include/rpc/
sudo cp /usr/include/tirpc/netconfig.h /usr/include

cd /tmp
wget https://www.snort.org/downloads/snort/snort-2.9.20.tar.gz -O snort.tar.gz
tar -xvzf snort.tar.gz
cd snort-2.9.20
./configure --enable-sourcefire
make
sudo make install

sudo mkdir /etc/snort /etc/snort/rules /var/log/snort

sudo cp etc/snort.conf /etc/snort/snort.conf
sudo mkdir /usr/local/lib/snort_dynamicrules
sudo touch /etc/snort/rules/white_list.rules
sudo touch /etc/snort/rules/black_list.rules
sudo touch /etc/snort/rules/local.rules
sudo touch /etc/snort/rules/app-detect.rules
sudo touch /etc/snort/rules/attack-responses.rules
sudo touch /etc/snort/rules/backdoor.rules
sudo touch /etc/snort/rules/bad-traffic.rules
sudo touch /etc/snort/rules/blacklist.rules
sudo touch /etc/snort/rules/botnet-cnc.rules
sudo touch /etc/snort/rules/browser-chrome.rules
sudo touch /etc/snort/rules/browser-firefox.rules
sudo touch /etc/snort/rules/browser-ie.rules
sudo touch /etc/snort/rules/browser-other.rules
sudo touch /etc/snort/rules/browser-plugins.rules
sudo touch /etc/snort/rules/browser-webkit.rules
sudo touch /etc/snort/rules/chat.rules
sudo touch /etc/snort/rules/content-replace.rules
sudo touch /etc/snort/rules/ddos.rules
sudo touch /etc/snort/rules/dns.rules
sudo touch /etc/snort/rules/dos.rules
sudo touch /etc/snort/rules/experimental.rules
sudo touch /etc/snort/rules/exploit-kit.rules
sudo touch /etc/snort/rules/exploit.rules
sudo touch /etc/snort/rules/file-executable.rules
sudo touch /etc/snort/rules/file-flash.rules
sudo touch /etc/snort/rules/file-identify.rules
sudo touch /etc/snort/rules/file-image.rules
sudo touch /etc/snort/rules/file-multimedia.rules
sudo touch /etc/snort/rules/file-office.rules
sudo touch /etc/snort/rules/file-other.rules
sudo touch /etc/snort/rules/file-pdf.rules
sudo touch /etc/snort/rules/finger.rules
sudo touch /etc/snort/rules/ftp.rules
sudo touch /etc/snort/rules/icmp-info.rules
sudo touch /etc/snort/rules/icmp.rules
sudo touch /etc/snort/rules/imap.rules
sudo touch /etc/snort/rules/indicator-compromise.rules
sudo touch /etc/snort/rules/indicator-obfuscation.rules
sudo touch /etc/snort/rules/indicator-shellcode.rules
sudo touch /etc/snort/rules/info.rules
sudo touch /etc/snort/rules/malware-backdoor.rules
sudo touch /etc/snort/rules/malware-cnc.rules
sudo touch /etc/snort/rules/malware-other.rules
sudo touch /etc/snort/rules/malware-tools.rules
sudo touch /etc/snort/rules/misc.rules
sudo touch /etc/snort/rules/multimedia.rules
sudo touch /etc/snort/rules/mysql.rules
sudo touch /etc/snort/rules/netbios.rules
sudo touch /etc/snort/rules/nntp.rules
sudo touch /etc/snort/rules/oracle.rules
sudo touch /etc/snort/rules/os-linux.rules
sudo touch /etc/snort/rules/os-other.rules
sudo touch /etc/snort/rules/os-solaris.rules
sudo touch /etc/snort/rules/os-windows.rules
sudo touch /etc/snort/rules/other-ids.rules
sudo touch /etc/snort/rules/p2p.rules
sudo touch /etc/snort/rules/phishing-spam.rules
sudo touch /etc/snort/rules/policy-multimedia.rules
sudo touch /etc/snort/rules/policy-other.rules
sudo touch /etc/snort/rules/policy.rules
sudo touch /etc/snort/rules/policy-social.rules
sudo touch /etc/snort/rules/policy-spam.rules
sudo touch /etc/snort/rules/pop2.rules
sudo touch /etc/snort/rules/pop3.rules
sudo touch /etc/snort/rules/protocol-finger.rules
sudo touch /etc/snort/rules/protocol-ftp.rules
sudo touch /etc/snort/rules/protocol-icmp.rules
sudo touch /etc/snort/rules/protocol-imap.rules
sudo touch /etc/snort/rules/protocol-pop.rules
sudo touch /etc/snort/rules/protocol-services.rules
sudo touch /etc/snort/rules/protocol-voip.rules
sudo touch /etc/snort/rules/pua-adware.rules
sudo touch /etc/snort/rules/pua-other.rules
sudo touch /etc/snort/rules/pua-p2p.rules
sudo touch /etc/snort/rules/pua-toolbars.rules
sudo touch /etc/snort/rules/rpc.rules
sudo touch /etc/snort/rules/rservices.rules
sudo touch /etc/snort/rules/scada.rules
sudo touch /etc/snort/rules/scan.rules
sudo touch /etc/snort/rules/server-apache.rules
sudo touch /etc/snort/rules/server-iis.rules
sudo touch /etc/snort/rules/server-mail.rules
sudo touch /etc/snort/rules/server-mssql.rules
sudo touch /etc/snort/rules/server-mysql.rules
sudo touch /etc/snort/rules/server-oracle.rules
sudo touch /etc/snort/rules/server-other.rules
sudo touch /etc/snort/rules/server-webapp.rules
sudo touch /etc/snort/rules/shellcode.rules
sudo touch /etc/snort/rules/smtp.rules
sudo touch /etc/snort/rules/snmp.rules
sudo touch /etc/snort/rules/specific-threats.rules
sudo touch /etc/snort/rules/spyware-put.rules
sudo touch /etc/snort/rules/sql.rules
sudo touch /etc/snort/rules/telnet.rules
sudo touch /etc/snort/rules/tftp.rules
sudo touch /etc/snort/rules/virus.rules
sudo touch /etc/snort/rules/voip.rules
sudo touch /etc/snort/rules/web-activex.rules
sudo touch /etc/snort/rules/web-attacks.rules
sudo touch /etc/snort/rules/web-cgi.rules
sudo touch /etc/snort/rules/web-client.rules
sudo touch /etc/snort/rules/web-coldfusion.rules
sudo touch /etc/snort/rules/web-frontpage.rules
sudo touch /etc/snort/rules/web-iis.rules
sudo touch /etc/snort/rules/web-misc.rules
sudo touch /etc/snort/rules/web-php.rules
sudo touch /etc/snort/rules/x11.rules

sudo cp etc/*.conf* /etc/snort
sudo cp etc/*.map /etc/snort
sudo cp etc/*.dtd /etc/snort

sudo find /etc/snort/ -type f -exec sed -i 's|\.\./rules|rules|g' {} +

sudo snort -T -c /etc/snort/snort.conf -i enX0

wget --no-cache https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/snort.service
sudo mv snort.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable snort
sudo systemctl start snort