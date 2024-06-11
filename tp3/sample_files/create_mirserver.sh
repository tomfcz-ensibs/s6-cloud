sudo apt update
sudo apt upgrade -y

sudo DEBIAN_FRONTEND=noninteractive apt install -y snort
echo 'alert ip any any -> any any (msg:"SQL Injection Attempt"; content:"1+%3D+1"; nocase; classtype:attempted-recon; sid:1000003;)' | sudo tee -a /etc/snort/rules/local.rules