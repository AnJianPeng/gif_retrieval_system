function showResult() {
	var sum = 0;
	var x = document.getElementsByClassName("img-thumbnail");
	for (i = 0; i < x.length; i++) {
		sum++;
		if (i < x.length - 1) x[i].src = x[i+1].src;
		else x[i].src = "img/carDrifting2.gif";
		x[i].style.display = "block";
	}
	console.log(sum);
}

function clearResult() {
	var sum = 0;
	var x = document.getElementsByClassName("img-thumbnail");
	for (i = 0; i < x.length; i++) {
		sum++;
		x[i].style.display = "none";
	}
	console.log(sum);
}