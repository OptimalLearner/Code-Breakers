var xmlHttp = new XMLHttpRequest();
var url = "http://localhost:5500/JSONData.json";
xmlHttp.open("GET", url, true);
xmlHttp.send();
xmlHttp.onreadystatechange = function() {
    if (this.ready == 4 && this.status == 200) {
        var data = JSON.parse(this.responseText);
        console.log(data);
        var months = data.months_temperature.map(function(elem) {
            return elem.date;
        });
        var high = data.months_temperature.map(function(elem) {
            return elem.high;
        });
        var low = data.months_temperature.map(function(elem) {
            return elem.low;
        });
    }

    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'High Temp',
                data: high,
                backgroundColor: 'transparent',
                borderColor: 'red',
                borderWidth: 4
            }, {
                label: 'Low Temp',
                data: low,
                backgroundColor: 'transparent',
                borderColor: 'green',
                borderWidth: 4
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}