/**
 * Created by MaxGoovaerts on 2/8/2015.
 */
function drawGraph() {
    var ctx = document.getElementById("lineChart").getContext("2d");
    var data = {
        labels: ["January", "February", "March", "April", "May", "June", "July"],
        datasets: [
            {
                label: "My First dataset",
                fillColor: "rgba(220,220,220,0.2)",
                strokeColor: "rgba(220,220,220,1)",
                pointColor: "rgba(220,220,220,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(220,220,220,1)",
                data: [65, 59, 80, 81, 56, 55, 40]
            },
            {
                label: "My Second dataset",
                fillColor: "rgba(151,187,205,0.2)",
                strokeColor: "rgba(151,187,205,1)",
                pointColor: "rgba(151,187,205,1)",
                pointStrokeColor: "#fff",
                pointHighlightFill: "#fff",
                pointHighlightStroke: "rgba(151,187,205,1)",
                data: [28, 48, 40, 19, 86, 27, 90]
            }
        ]
    };
    var myLineChart = new Chart(ctx).Line(data);
    document.getElementById("lineLegend").innerHTML = myLineChart.generateLegend();
}

    function drawPieChart(data) {
        var ctx = document.getElementById("pieChart").getContext("2d");
        var myPieChart = new Chart(ctx).Pie(data);
    }

    function drawGooglePieChart(array) {
        var data = google.visualization.arrayToDataTable(array);

        var options = {
          title: 'Forum Post Categories',
          is3D: true,
            animation: {
                duration: 10000,
                easing: 'out',
                startup: true
              }
        };

        var chart = new google.visualization.PieChart(document.getElementById('piechart_3d'));
        chart.draw(data, options);
    }
