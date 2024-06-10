sudo dnf update -y
sudo dnf install httpd -y
sudo systemctl enable httpd
sudo systemctl start httpd
sudo dnf install php php-mysqli -y

wget --no-cache https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/index.php
sudo sed -i "s/REPLACE_MARIADB_IP/$1/g" index.php
sudo mv index.php /var/www/html/

wget --no-cache https://raw.githubusercontent.com/tomfcz-ensibs/s6-cloud/main/tp3/sample_files/site.conf
sudo mv site.conf /etc/httpd/conf.d/
sudo systemctl restart httpd