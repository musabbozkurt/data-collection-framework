<?php
session_start();
include_once 'dbconnect.php';
?>
<!DOCTYPE html>
<html>
<head>
	<title>Home | Welcome</title>
	<meta content="width=device-width, initial-scale=1.0" name="viewport" >
	<link rel="stylesheet" href="css/bootstrap.min.css" type="text/css" />
	<style>
            .arayuz_icerik{min-height:480px;padding:20px;}
            .arayuz_basliklar{border:1px solid silver;min-height: 50px;width:150px;float:left;padding:5px;background:rgba(100, 100, 100, 0.5);}
            .menu{border:2px solid silver;padding:8px;text-align: center;margin-bottom:25px;}
            .menu:hover{background:#0066FF;}
            .menu:hover{color:#000000;}
            
            fieldset{margin-left:40px;margin-top:3%;width:75%;float:left;background:rgba(100, 100, 100, 0.5);}
            
            .msj{display:none;color:white;}
        </style>
</head>
<body text=white>
	<img src='b.png' style='position:fixed;top:0px;left:0px;width:100%;height:100%;z-index:-1;'>
	<script>
            function arayuz_degis(icerikno,baslik,renk){         
                document.getElementById('baslik').innerHTML = "<font color='"+renk+"'>"+baslik+"</font>";        
                //console.log(arayuz_basliklar);
                var icerikler = document.getElementsByClassName("arayuz_icerik");
                for(var i=0;i < icerikler.length;i++){
                    icerikler[i].style.display="none";
                }
                var icerik=document.getElementsByClassName(icerikno);
                icerik[0].style.display="block";
            }

        </script>
<nav class="navbar navbar-default" role="navigation">
	<div class="container-fluid">
		<div class="navbar-header">
			<button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar1">
				<span class="sr-only">Toggle navigation</span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
				<span class="icon-bar"></span>
			</button>
			<a class="navbar-brand" href="index.php">Homepage</a>
		</div>
		<div class="collapse navbar-collapse" id="navbar1">
			<ul class="nav navbar-nav navbar-right">
				<?php if (isset($_SESSION['usr_id'])) { ?>
				<li><p class="navbar-text">Signed in as <?php echo $_SESSION['usr_name']; ?></p></li>
				<li><a href="logout.php">Log Out</a></li>
				<?php } else { ?>
				<li><a href="login.php">Login</a></li>
				<li><a href="register.php">Sign Up</a></li>
				<?php } ?>
			</ul>
		</div>
	</div>
</nav>

<?php if (isset($_SESSION['usr_id'])) { ?>
	<div class="arayuz_basliklar" style="margin-top:3%;">
            
            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme1','MAIN PAGE','#FFFFFF');" style="color:white">Main Page</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme2','COLLECTING TWEETS','white');" style="color:white">Collecting Tweets</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme3','COLLECTING FOLLOWERS','white');" style="color:white">Collecting Followers</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme4','STRORING DATA','white');" style="color:white">Storing Data</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme5','ANALYSIS','white');" style="color:white">Analysis of Tweets</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme6','STREAMING','white');" style="color:white">Streaming</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme7','CROSS VALIDATION & F1 MACRO SCORING','white');" style="color:white">Finding Cross Validation and F1 Macro Scoring</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme8','TERM FREQUENCY','white');" style="color:white">Finding Term Frequency</a> </div>
            
        </div> 
        
        <fieldset>
            <legend id="baslik" style="color:white;" >MAIN PAGE</legend>
        
        <div class="arayuz_icerik sekme1"><h1 style="color:#FFFFFF">Welcome</h1></div>

        <div class="arayuz_icerik sekme2" style="display: none;">
            <div class="menu" style="margin-top:150px;"> <a href="javascript:;" onclick="arayuz_degis('sekme9','UserList','white');" style="color:white">Collect Tweets From User List</a> </div>
            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme10','UserName','white');" style="color:white">Collect Tweets From User Name</a> </div>     
	</div>

		<div class="arayuz_icerik sekme9" style="display: none;" >
			<form method="POST" action="client.php">
		    		How many tweets do you want to collect? : <input type="text" 					name="numberoftweet" id="numberoftweet"> <br><br>
		    		<input type="submit" name="submit1" value="Collect Tweet">
			</form>
		</div>

		<div class="arayuz_icerik sekme10" style="display: none;">
			<form method="POST" action="client.php">
				Please enter username : <input type="text" name="username" id="username"> <br><br>
		    		How many tweets do you want to collect? : <input type="text" name="numberoftweet" id="numberoftweet"> <br><br>
		    		<input type="submit" name="submit2" value="Collect Tweet"/>
			</form>
		</div>

        <div class="arayuz_icerik sekme3" style="display: none;">
            <div class="menu" style="margin-top:150px;"> <a href="javascript:;" onclick="arayuz_degis('sekme11','UserList','white');" style="color:white">Collect Followers From User List</a> </div>
            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme12','UserName','white');" style="color:white">Collect Followers From User Name</a> </div>
	</div>

		<div class="arayuz_icerik sekme11" style="display: none;">
			<form method="POST" action="client.php">
		    		<input type="submit" name="submit3" value="Collect Followers"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme12" style="display: none;">
			<form method="POST" action="client.php">
			    Please enter username : <input type="text" name="username" 				    id="username"> <br><br>
			    <input type="submit" name="submit4" value="Collect Followers"/>
			</form>
		</div>

        <div class="arayuz_icerik sekme4" style="display: none;">
		<form method="POST" action="client.php">
		    Please Enter Database Name : <input type="text" name="databasename" id="databasename"> <br><br>
		    Please Enter Collection Name : <input type="text" name="collectionname" id="collectionname"> <br><br>
		    Store your data to Mongo Database make sure your path is okay or change it from config file<br>
		    <input type="submit" name="submit5" value="Store Data"/>
		</form>
        </div>

	<div class="arayuz_icerik sekme5" style="display: none;" >

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme13','Plot Language','white');" style="color:white">Plot Language Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme14','Plot Country','white');" style="color:white">Plot Country Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme15','Plot Location','#FFFFFF');" style="color:white">Plot Location Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme16','Plot Timezone','white');" style="color:white">Plot Timezone Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme17','Plot Tweet','white');" style="color:white">Plot Tweet Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme18','Plot Tweet Create','white');" style="color:white">Plot Tweet Create at Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme19','Plot User ID','white');" style="color:white">Plot User ID Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme20','Plot String of ID','white');" style="color:white">Plot String of ID Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme21','Plot Username','white');" style="color:white">Plot Username Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme22','Plot ScreenName','white');" style="color:white">Plot ScreenName Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme23','Plot Followers_Count','#FFFFFF');" style="color:white">Plot Followers_Count Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme24','Plot Friends_Count','white');" style="color:white">Plot Friends_Count Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme25','Plot User Language','white');" style="color:white">Plot User Language Analysis</a> </div>

            <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme26','Plot Retweet Count','white');" style="color:white">Plot Retweet Count Analysis</a> </div>

	    <div class="menu"> <a href="javascript:;" onclick="arayuz_degis('sekme27','Plot Favorite Count','white');" style="color:white">Plot Favorite Count Analysis</a> </div>

	</div>

		<div class="arayuz_icerik sekme13" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 			        name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit6" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme14" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit7" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme15" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit8" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme16" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit9" value="Plot">
			</form>
		</div>

		<div class="arayuz_icerik sekme17" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"><br><br>
			    <input type="submit" name="submit10" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme18" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit11" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme19" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit12" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme20" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit13" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme21" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit14" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme22" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit15" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme23" style="display: none;" >
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit16" value="Plot">
			</form>
		</div>

		<div class="arayuz_icerik sekme24" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? <input type="text" 					name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit17" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme25" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit18" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme26" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit19" value="Plot"/>
			</form>
		</div>

		<div class="arayuz_icerik sekme27" style="display: none;">
			<form method="POST" action="client.php">
			    How many bars do you want to see in your plot? : <input type="text" 				name="numberofbar" id="numberofbar"> <br><br>
			    <input type="submit" name="submit20" value="Plot"/>
			</form>
		</div>

	<div class="arayuz_icerik sekme6" style="display: none;" >
		<form method="POST" action="client.php">
		    Please Enter Database Name : <input type="text" name="databasename" id="databasename"> <br><br>
		    Please Enter Collection Name : <input type="text" name="collectionname" id="collectionname"> <br><br>
		    Please Enter File Name : <input type="text" name="filename" id="filename"> <br><br>
		    Please Enter Finishing Date as "Year-Month-Day Hour:Minute:Second"(Ex:2016-12-30 15:27:30) : <input type="text" name="finishingdate" id="finishingdate"> <br><br>
		    Please Enter a word, hashtag or something else for filter : <input type="text" name="filterword" id="filterword"> <br><br>
		    <input type="submit" name="submit21" value="Run Streaming"/>
		</form>
	</div>

	<div class="arayuz_icerik sekme7" style="display: none;" >
		<form method="POST" action="client.php">
		    Enter number for N for cross validation? : <input type="text" name="nforcross" id="nforcross"> <br><br>
		    Enter number of split? : <input type="text" name="numberofsplit" id="numberofsplit"> <br><br>
		    Enter number for test size between 0 and 1? it might be 0.3 : <input type="text" name="testsize" id="testsize"> <br><br>
		    Enter random state you might enter 0(zero)? : <input type="text" name="randomstate" id="randomstate"> <br><br>
		    Enter number for test size between 0 and 1 for train test? you might enter 0.4 or 0.6 : <input type="text" name="traintest" id="traintest"> <br><br>
		    Enter number for C for kernel in svc you might enter 1(one)? : <input type="text" name="numberforc" id="numberforc"> <br><br>
		    <input type="submit" name="submit22" value="Calculate"/>
		</form>
	</div>

	<div class="arayuz_icerik sekme8" style="display: none;" >
		<form method="POST" action="client.php">
		    Enter number to display the most frequent words (or tokens), are not exactly meaningful : <input type="text" name="frequentword" id="frequentword"> <br><br>
		    Enter number to print top of maximum term : <input type="text" name="topofmax" id="topofmax"> <br><br>
		    Enter a word, hashtag or something else to find Co-occurrence : <input type="text" name="cooccurance" id="cooccurance"> <br><br>
		    <input type="submit" name="submit23" value="Collect Tweet"/>
		</form>
	</div>

	

        </fieldset>
        <article>
<?php
if(!empty($_POST)){
	//Allow the script to hang around waiting for connections.
	set_time_limit(0);

	// Turn on implicit output flushing so we see what we're getting as it comes in.
	ob_implicit_flush();

	// Set timeout in seconds
	$timeout = 3;

	// Create a TCP/IP client socket.
	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	if ($socket === false) 
	{
	    $result2 = "Error: socket_create() failed: reason: " .socket_strerror(socket_last_error()). "\n";
	}

	// Server data
	$host = '127.0.0.1';
	$port = 5555;

	$error = NULL;
	$attempts = 0;
	$timeout *= 1000;  // adjust because we sleeping in 1 millisecond increments
	$connected = FALSE;
	while (!($connected = socket_connect($socket, $host, $port)) && ($attempts++ < $timeout)) 
	{
	    $error = socket_last_error();
	    if ($error != SOCKET_EINPROGRESS && $error != SOCKET_EALREADY) 
	    {
		echo "Error Connecting Socket: ".socket_strerror($error) . "\n";
		socket_close($socket);
		return NULL;
	    }
	    usleep(1000);
	}


	if (!$connected) 
	{
	    echo "Error Connecting Socket: Connect Timed Out After " . $timeout/1000 . " seconds. ".socket_strerror(socket_last_error()) . "\n";
	    socket_close($socket);
	    return NULL;
	}
        //catching commands
///////////tweets from userlist//////////////////////////////////////////////////////////////////
	if (isset($_POST['submit1'])){
		
	    $val1 = htmlentities($_POST['numberoftweet']);
	    $arr = array('msg0'=>"collecttweetfromuserlist",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//it works
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////tweets from username input////////////////////////////////////////////////
	if (isset($_POST['submit2'])){  

	    $val1 = htmlentities($_POST['username']);
	    $val2 = htmlentities($_POST['numberoftweet']);
	    $arr = array('msg0'=>"collecttweetfromusername",'msg1'=>$val1,'msg2'=>$val2);

	    // Write to the socket
	    $msg = json_encode($arr);
	    echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        echo "<br>";
	        echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

///////////followers from userlist///////////////////////////////////////////
	if (isset($_POST['submit3'])){
		
	    $arr = array('msg0'=>"collectfollowerfromuserlist");

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}
	
///////////followers from username input///////////////////////////////////////
	if (isset($_POST['submit4'])){
		
	    $val1 = htmlentities($_POST['username']);
	    $arr = array('msg0'=>"collectfollowerfromusername",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////storing data into mongodb//////////////////////////////////////////////////////////
	if (isset($_POST['submit5'])){

	    $val1 = htmlentities($_POST['databasename']);
	    $val2 = htmlentities($_POST['collectionname']);
	    $arr = array('msg0'=>"storedata",'msg1'=>$val1,'msg2'=>$val2);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Language Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit6'])){

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotlanguage",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Country Analysis/////////////////////////////////////////////////////////////
	
	if (isset($_POST['submit7'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotcountry",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Location Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit8'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotlocation",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Timezone Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit9'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plottimezone",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

///////////Plotting Tweet Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit10'])){

		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plottweet",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//it works
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);

	    }*/
	}

//////////Plotting Tweet Create at Analysis//////////////////////////////////////////////////////
	if (isset($_POST['submit11'])){  

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plottweetcreatedat",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        echo "<br>";
	        echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);

	    }*/
	}

///////////Plotting User ID Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit12'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotuserid",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}
	
///////////Plotting String of ID Analysis/////////////////////////////////////////////////////////
	if (isset($_POST['submit13'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotstringofid",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);

	    }*/
	}

////////////Plotting Username Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit14'])){

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotusername",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting ScreenName Analysis/////////////////////////////////////////////////////////////
	if (isset($_POST['submit15'])){

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotscreenname",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Followers_Count Analysis/////////////////////////////////////////////////////
	if (isset($_POST['submit16'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotfollowerscount",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Friends_Count Analysis/////////////////////////////////////////////////////////
	if (isset($_POST['submit17'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotfriendscount",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting User Language Analysis//////////////////////////////////////////////////////
	if (isset($_POST['submit18'])){
		
	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotuserlanguage",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Retweet Count Analysis/////////////////////////////////////////////////////	
if (isset($_POST['submit19'])){

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotretweet",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Plotting Favorite Count Analysis////////////////////////////////////////////////////////
	if (isset($_POST['submit20'])){

	    $val1 = htmlentities($_POST['numberofbar']);
	    $arr = array('msg0'=>"plotfavourite",'msg1'=>$val1);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Streaming///////////////////////////////////////////////////////////////////
	if (isset($_POST['submit21'])){

	    $val1 = htmlentities($_POST['databasename']);
	    $val2 = htmlentities($_POST['collectionname']);
	    $val3 = htmlentities($_POST['filename']);
	    $val4 = htmlentities($_POST['finishingdate']);
	    $val5 = htmlentities($_POST['filterword']);
	    $arr = array('msg0'=>"stream",'msg1'=>$val1,'msg2'=>$val2,'msg3'=>$val3,'msg4'=>$val4,'msg5'=>$val5);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Finding Cross Validation and F1 Macro Scoring///////////////////////////////////////////
	if (isset($_POST['submit22'])){
		    
	    $val1 = htmlentities($_POST['nforcross']);
	    $val2 = htmlentities($_POST['numberofsplit']);
	    $val3 = htmlentities($_POST['testsize']);
	    $val4 = htmlentities($_POST['randomstate']);
	    $val5 = htmlentities($_POST['traintest']);
	    $val6 = htmlentities($_POST['numberforc']);
	    $arr = array('msg0'=>"crossvalidation",'msg1'=>$val1,'msg2'=>$val2,'msg3'=>$val3,'msg4'=>$val4,'msg5'=>$val5,'msg6'=>$val6);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}

//////////Finding Term Frequency//////////////////////////////////////////////////////
	if (isset($_POST['submit23'])){

	    $val1 = htmlentities($_POST['frequentword']);
	    $val2 = htmlentities($_POST['topofmax']);
	    $val3 = htmlentities($_POST['cooccurance']);
	    $arr = array('msg0'=>"termfrequency",'msg1'=>$val1,'msg2'=>$val2,'msg3'=>$val3);

	    // Write to the socket
	    $msg = json_encode($arr);
	    //echo "sending $msg <br>";    
	    socket_write($socket, $msg, strlen($msg)) or die("Could not write input\n");

	    //Read from socket
	    $resultLength = socket_read($socket, 1024);
	    if (strlen($resultLength) == 0) {
	        echo "Emptyness passed back from server";
	    }
	    else {
	        //$Telemetry = socket_read($socket1, strlen($resultLength));
	        //echo "<br>";
	        //echo $resultLength;//$Telemetry;
	    }
	    // close the socket
	    /*if($msg['msg0']=="killserver"){
	        socket_close($socket);
	    }*/
	}
}
?>
</article>
				
<?php } else { ?>
		
<?php } ?>

<script src="js/jquery-1.10.2.js"></script>
<script src="js/bootstrap.min.js"></script>

</body>

</html>
