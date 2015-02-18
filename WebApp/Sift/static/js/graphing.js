/**
 * Created by MaxGoovaerts and CJ on 2/8/2015.
 */

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
function draw_dashboard1(count) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('number', 'Posts');
    for (key in count) {
        //console.log(new Date(parseInt(key)));
        lineChartData.addRows([
            [new Date(parseInt(key)), count[key]['numPosts']]
        ])

    }

    // Create a dashboard.
    var dash_container = document.getElementById('dashboard'),
        myDashboard = new google.visualization.Dashboard(dash_container);


    // Create a date range slider
    var myDateSlider = new google.visualization.ControlWrapper({
        'controlType': 'DateRangeFilter',
        'containerId': 'main_slider',
        'options': {
            'filterColumnLabel': 'Date',
            'ui': {
                'cssClass': 'sliderClass'
            }
        }
    });
    // Line chart visualization
    var myLine = new google.visualization.ChartWrapper({
        'chartType': 'ColumnChart',
        'containerId': 'line_chart',
        view: {
            columns: [0, 1]
        }
    });


    // Bind myLine to the dashboard, and to the controls
    // this will make sure our line chart is update when our date changes
    myDashboard.bind(myDateSlider, myLine);

    myDashboard.draw(lineChartData);

    return myDateSlider;
}
function draw_dashboard2(count) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('string', 'Post');
    for (key in count) {
        for (i = 0; i < count[key]['posts'].length; i++) {
            lineChartData.addRows([
                [new Date(parseInt(key)), count[key]['posts'][i]]
            ])
        }
    }
    console.log(lineChartData);
    // Create a dashboard.
    var dash_container = document.getElementById('dashboard'),
        myDashboard = new google.visualization.Dashboard(dash_container);


    // Create a date range slider
    var myDateSlider = new google.visualization.ControlWrapper({
        'controlType': 'DateRangeFilter',
        'containerId': 'hidden_slider',
        'options': {
            'filterColumnLabel': 'Date',
        }
    });

    // Table visualization
    var myTable = new google.visualization.ChartWrapper({
        'chartType': 'Table',
        'containerId': 'table_chart'
    });

    // Bind myTable to the dashboard, and to the controls
    // this will make sure our table is update when our date changes
    myDashboard.bind(myDateSlider, myTable);

    myDashboard.draw(lineChartData);
    return myDateSlider;

}