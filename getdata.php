<?php

$result = new stdClass();



function getConnection()
{
	// WAMP Creds
  
  $host=$_ENV["db_host"];
  $port=3306;
  $socket="";
  $user=$_ENV["db_user"];
  $password=$_ENV["db_password"];
  $dbname=$_ENV["db_db"];
	
	
  $con = new mysqli($host, $user, $password, $dbname, $port, $socket)
  	or die ('Could not connect to the database server' . mysqli_connect_error());

  return $con;
}

$date = $_POST["date"];

$con = getConnection();


$nextDay = new DateTime($date);
$result->nextDate = $nextDay;
$nextDay->add(new DateInterval('P1D'));
$nextDay = $nextDay->format('Y-m-d');


$bowlSql = "SELECT * from bowls WHERE LastUpdate BETWEEN '$date' AND '$nextDay'";
$bowlResult = mysqli_query($con,$bowlSql);
$result->message = mysqli_error($con);

$tempSql = "SELECT * from Temperatures WHERE LastUpdate BETWEEN '$date' AND '$nextDay'";
$tempResult = mysqli_query($con,$tempSql);
while ($tempRow = mysqli_fetch_assoc($tempResult))
{
	$result->tempUpperMtnHigh = $tempRow["snowReportWeatherUpperMtnHigh"];
	$result->tempUpperMtnLow = $tempRow["snowReportWeatherUpperMtnLow"];
	$result->tempLowerMtnHigh = $tempRow["snowReportWeatherLowerMtnHigh"];
	$result->tempLowerMtnLow = $tempRow["snowReportWeatherLowerMtnLow"];
}

$snowSql = "SELECT * from NewSnow WHERE LastUpdate BETWEEN '$date' AND '$nextDay'";
$snowResult = mysqli_query($con,$snowSql);
while ($snowRow = mysqli_fetch_assoc($snowResult))
{
	$result->snowLastNight = $snowRow["snowReportNewSnowFallOvernight"];
	$result->snow24 = $snowRow["snowReportNewSnowFall24"];
	$result->snow48 = $snowRow["snowReportNewSnowFall48"];
	$result->snow7days = $snowRow["snowReportNewSnowFall7days"];
}

$result->data = array();
$i=0;

$fieldArray = array();
$bowls = array();
$updates = array();

while ($columnName = mysqli_fetch_field($bowlResult))
{
	array_push($fieldArray, $columnName->name);
}


while ($bowlRow = mysqli_fetch_assoc($bowlResult))
{
	
	$update = new stdClass();
	$update->bowls = array();
	$update->delta = array();
	
	foreach ($fieldArray as $field)
	{
		
		$currentBowl = new stdClass();
		if ($field == "LastUpdate")
		{
			$update->time = $bowlRow[$field];
		}
		else 
		{
			$currentBowl->bowl = $field;
			$currentBowl->status = $bowlRow[$field];
		}
		
		array_push($update->bowls,$currentBowl);
		
	}
	array_push($updates,$update);
	$result->i = $i;
	
	if ($i > 0)
	{
		for ($bowlNumber=0; $bowlNumber < count($updates[$i]->bowls); $bowlNumber++)
		{
			if ($updates[$i]->bowls[$bowlNumber]->status != $updates[$i-1]->bowls[$bowlNumber]->status && $updates[$i]->bowls[$bowlNumber]->bowl != "Id")
			{
				array_push($updates[$i]->delta, $updates[$i]->bowls[$bowlNumber]->bowl . " changed its status to " . $updates[$i]->bowls[$bowlNumber]->status);
			}
		}
	}
	$i++;
}

array_push($result->data,$updates);
array_push($result->fields,$fieldArray);

$result->sql = $bowlSql;

$result->status = "success";

echo json_encode($result);

?>