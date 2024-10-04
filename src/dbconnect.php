<?php
// connect to mysql database
$con = new mysqli("db", "root", "root", "test_db") or die("Error " . mysqli_error($con));
