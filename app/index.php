<html>
<?php

?>


<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha.6/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.6.4/js/bootstrap-datepicker.min.js"></script>
<style>

.site 
{
	width: 100px;
	height: 100px;
	border: 1px solid black;
}

</style>
<script>

var x 

function getData()
{
	$.post("getData.php", { date: $("#date").val() }, function(result)
	{
		x = result
		output = ""
		//console.log(result.data[0].delta)
		
		output += "<table class=\"full-table table-striped table-hover\">"
		
		output += "<tr>"
		output += "<th></th>"
		for (i=0; i<result.data[0].length; i++)
		{
			output += "<th>"+result.data[0][i].time.substring(10,16)+"</th>"
		}
		output += "</tr>"
		for (i=2; i<result.data[0][0].bowls.length; i++)
		{
			
			output += "<tr>"
			
			output += "<td>"+result.data[0][0].bowls[i].bowl.replace(/_/g," ").replace("39","'")+"</td>"
			
			for (j= 0; j < result.data[0].length; j++)
			{
				cls = result.data[0][j].bowls[i].status.replace(" ","").toLowerCase()
				output += "<td><div class=\"status "+cls+"\">"+result.data[0][j].bowls[i].status+"</div></td>"
			}

			output += "</tr>"
		}
		
		
		output += "</table>"
		
		$("#data").html(output)
		$("#currentDate").html($("#date").val())
		$("#temperature").html(result.tempLowerMtnLow + "&#176;C / " + result.tempLowerMtnHigh + "&#176;C")
		$("#newSnow").html(result.snow24 + "cm / 24 hrs")
		console.log(result)
		
	}, 
	"json")
	
	.fail(function(result) {
		console.log(result)
	})
}

$(function()
{
	$("#btn_go").on("click",function() { getData() })
})
</script>
</head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
<link rel="stylesheet" href="styles.css">
<body>
	<div class="mainContainer">
		<div class="container">
			<div class="lgTxt" id="currentDate">
			</div>
			<div class="container">
				<input type="date" id="date">
				<button type="button" class="btn btn-success" id="btn_go">GO</button>
			</div>
			<div class="container temperatureContainer">
				<div><img src="cloudy.png" width="100" ></div>
				<div>
					<div class="temperature">
						<table>
						<tr>
							<td class="lgTxt">New Snow:</td>
							<td class="lgTxt"><div id="newSnow"></div></td>
						</tr>
						<tr>
							<td class="lgTxt">Temperature:</td>
							<td class="lgTxt"><div id="temperature"></div></td>
						</tr>
						</table>
					</div>
				</div>
			</div>
		</div>
		
		<div class="predictionContainer">
		</div>
		
		<div class="historyContainer">
			<div id="data">
			</div>
		</div>
		
		
		</div>
	</div>

</body>

</html>


