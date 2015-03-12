var xhr = new XMLHttpRequest();

xhr.onreadystatechange = function() {
	if(xhr.readyState == 4 && xhr.status === 200) {
		var rrr = xhr.responseText;
		if(xhr.responseText) {
			document.getElementById('city_search_matches').style.display = "block";
			document.getElementById('city_search_matches').innerHTML = xhr.responseText;
		}
	} else {
		hide_cities();
	}
}

function hide_cities() {
	document.getElementById('city_search_matches').style.display = "none";
}

function find_cities() {
	xhr.open('POST', '/find_matching_cities', true);
	xhr.setRequestHeader("content-type","application/x-www-form-urlencoded");
	var city = "city=" + document.getElementById('search_input').value;
	xhr.send(city);
}

function insert_city_from_dropdown(str) {
    document.getElementById('search_input').value = str;
    hide_cities();
}

var elSearchBox = document.getElementById('search_input');
elSearchBox.addEventListener('input', find_cities, false);
