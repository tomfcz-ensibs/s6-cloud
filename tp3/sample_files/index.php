<?php
$mariadb_ip = "REPLACE_MARIADB_IP";

// Database connection parameters
$database = 'mydb'; // replace with your database name
$username = 'user'; // replace with your database username
$password = 'user'; // replace with your database password

// Create connection
$conn = new mysqli($mariadb_ip, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die('Connection failed: ' . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $query = $_POST['query'];

    // Execute the query
    $result = $conn->query($query);

    if ($result) {
        if ($result instanceof mysqli_result) {
            // Display results in a table
            echo '<table border="1">';
            echo '<tr>';
            while ($field = $result->fetch_field()) {
                echo '<th>' . htmlspecialchars($field->name) . '</th>';
            }
            echo '</tr>';
            while ($row = $result->fetch_assoc()) {
                echo '<tr>';
                foreach ($row as $cell) {
                    echo '<td>' . htmlspecialchars($cell) . '</td>';
                }
                echo '</tr>';
            }
            echo '</table>';
            $result->free();
        } else {
            echo 'Query executed successfully.';
        }
    } else {
        echo 'Error: ' . $conn->error;
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html>
<head>
    <title>Unsafe SQL Execution</title>
</head>
<body>
    <h1>Execute SQL Query</h1>
    <form method="post">
        <label for="query">SQL Query:</label>
        <input type="text" id="query" name="query">
        <input type="submit" value="Execute">
    </form>
</body>
</html>