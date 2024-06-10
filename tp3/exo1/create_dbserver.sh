sudo yum install -y mariadb105-server
sudo systemctl enable mariadb
sudo systemctl start mariadb

MARIADB_IP=${MARIADB_IP:-'127.0.0.1'}  # Default to localhost if not set
ROOT_USER='root'                      # Replace with your MariaDB root username
ROOT_PASS='your_root_password'        # Replace with your MariaDB root password
DB_NAME='mydb'             # Replace with your desired database name
NEW_USER='user'                       # The new username to create
NEW_PASS='user'                       # The new user's password

# Function to create a new database
create_database() {
  mysql -u "$ROOT_USER" -p"$ROOT_PASS" -h "$MARIADB_IP" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
  if [ $? -eq 0 ]; then
    echo "Database '$DB_NAME' created successfully."
  else
    echo "Failed to create database '$DB_NAME'."
    exit 1
  fi
}

# Function to create a new user and grant privileges
create_user() {
  mysql -u "$ROOT_USER" -p"$ROOT_PASS" -h "$MARIADB_IP" -e "CREATE USER IF NOT EXISTS '$NEW_USER'@'%' IDENTIFIED BY '$NEW_PASS';"
  if [ $? -eq 0 ]; then
    echo "User '$NEW_USER' created successfully."
  else
    echo "Failed to create user '$NEW_USER'."
    exit 1
  fi
  
  mysql -u "$ROOT_USER" -p"$ROOT_PASS" -h "$MARIADB_IP" -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$NEW_USER'@'%'; FLUSH PRIVILEGES;"
  if [ $? -eq 0 ]; then
    echo "Privileges granted to user '$NEW_USER' on database '$DB_NAME'."
  else
    echo "Failed to grant privileges to user '$NEW_USER'."
    exit 1
  fi
}

# Run the functions
create_database
create_user