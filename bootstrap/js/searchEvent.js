function showResult() {
    var sum = 0;
    var json = '[{"description": "a sport car is swinging on the race playground", "image_id": "11", "url": "https://38.media.tumblr.com/8952c98f05a5f01377ac98c041cfe63e/tumblr_nqofwqgS8d1siem3jo1_r1_400.gif"}, {"description": "a car drives through a puddle and drenches people at a bus stop.", "image_id": "41257", "url": " https://38.media.tumblr.com/64a238fc39c8ee1d313e40ffa48cda10/tumblr_npwndlNfA31unrb56o1_400.gif"}]';
    obj = JSON.parse(json);
    var x = document.getElementsByClassName("thumbnail");
    console.log(obj[0].url);
    for (i = 0; i < obj.length; i++) {
        sum++;
        x[i].innerHTML = "<img src=" + obj[i].url + " width=\"70%\" height=\"70%\">";
    }
    console.log(sum);
}

function clearResult() {
    var sum = 0;
    var x = document.getElementsByClassName("thumbnail");
    for (i = 0; i < x.length; i++) {
        sum++;
        x[i].innerHTML = "";
    }
    console.log(sum);
}

function textSearch() {
    var string = document.getElementById("textSearch").value;
	string = string.split(' ').join(' AND ');
    string = 'key=' + string
    var response;
    $.ajax({
        type: 'GET',
        url: 'http://localhost:8000/retrieval/text_query',
        processData: false,
        data: string,
        success: function(response) {
            console.log(response);
            var x = $(".thumbnail");
            for (i = 0; i < (response.length < x.length? response.length: x.length); i++) {
                $(x[i]).html("<img src=" + response[i].url + " width=\"70%\" height=\"70%\"/>");
            }
        }
    });
}

function gifSearch() {
    var file = document.getElementById("gif-file").files[0];
    var response;
    $.ajax({
        type: 'POST',
        url: 'http://localhost:8000/retrieval/sample_query',
        processData: false,
        success: function(response) {
            console.log(response);
            var x = $(".thumbnail");
            for (i = 0; i < (response.length < x.length? response.length: x.length); i++) {
                $(x[i]).html("<img src=" + response[i].url + " width=\"70%\" height=\"70%\"/>");
            }
        }
    });
}
