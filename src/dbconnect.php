<?php
// Connect to MySQL database. The hostname will be the 'db' service name in the docker-compose.yml file
$con = new mysqli("db", "root", "root", "root_db") or die("Error " . mysqli_error($con));
