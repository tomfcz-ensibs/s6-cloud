sudo dnf update -y
sudo yum install mariadb105-server -y
sudo systemctl enable mariadb
sudo systemctl start mariadb

MARIADB_IP='localhost'                # Default to localhost if not set
ROOT_USER='root'                      # Replace with your MariaDB root password
DB_NAME='mydb'                        # Replace with your desired database name
NEW_USER='user'                       # The new username to create
NEW_PASS='user'                       # The new user's password

# Function to create a new database
create_database() {
  mysql -u "$ROOT_USER" -h "$MARIADB_IP" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
  if [ $? -eq 0 ]; then
    echo "Database '$DB_NAME' created successfully."
  else
    echo "Failed to create database '$DB_NAME'."
    exit 1
  fi
}

# Function to create a new user and grant privileges
create_user() {
  mysql -u "$ROOT_USER" -h "$MARIADB_IP" -e "CREATE USER IF NOT EXISTS '$NEW_USER'@'%' IDENTIFIED BY '$NEW_PASS';"
  if [ $? -eq 0 ]; then
    echo "User '$NEW_USER' created successfully."
  else
    echo "Failed to create user '$NEW_USER'."
    exit 1
  fi
  
  mysql -u "$ROOT_USER" -h "$MARIADB_IP" -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$NEW_USER'@'%'; FLUSH PRIVILEGES;"
  if [ $? -eq 0 ]; then
    echo "Privileges granted to user '$NEW_USER' on database '$DB_NAME'."
  else
    echo "Failed to grant privileges to user '$NEW_USER'."
    exit 1
  fi
}

create_table() {
  mysql -u "$ROOT_USER" -h "$MARIADB_IP" "$DB_NAME" -e "
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        date_inscription DATE NOT NULL
    );

    INSERT INTO users (nom, email, date_inscription) VALUES
      ('Alice Dupont', 'alice.dupont@example.com', '2023-01-01'),
      ('Bob Martin', 'bob.martin@example.com', '2023-02-01'),
      ('Claire Leroy', 'claire.leroy@example.com', '2023-03-01');
  "
  if [ $? -eq 0 ]; then
    echo "Table 'users' and data added"
  else
    echo "Failed to add table and data"
    exit 1
  fi
}

# Run the functions
create_database
create_user
create_table