/**
 * Created by MaxGoovaerts and CJ on 2/8/2015.
 */

function drawGeneralPieChart(array) {
    var data = google.visualization.arrayToDataTable(array);

    var options = {
      is3D: true,
        animation: {
            duration: 10000,
            easing: 'out',
            startup: true
          },
        fontName: "Lato"
    };

    var chart = new google.visualization.PieChart(document.getElementById('general_piechart_3d'));
    chart.draw(data, options);
}

function drawGeneralLineChart(array, lineDates, clusterNames) {
    var data = new google.visualization.DataTable();
    console.log(array);
    data.addColumn('date', 'Day');

    for(i=0; i<clusterNames.length; i++) {
        data.addColumn('number', clusterNames[i]);
    }

    for(i=0; i< lineDates.length; i++) {
        row = [new Date(parseInt(lineDates[i]))];

        for(j=0; j<clusterNames.length; j++) {
            row.push(array[lineDates[i]][j]);
        }
        data.addRows([row]);
    }

    //Calculate width of scrolling X-Axis based on number of date posts
    var width = data.getNumberOfRows()*8;

    if(width < 700)
        width = "90%"

    var options = {
        animation: {
            duration: 1000,
            easing: 'out',
            startup: true
          },
        fontName: "Lato",
        legend: {
            position: 'hidden'
        },
        width: width,
        chartArea: {
            left: 70,
            width: '100%',
            height: '90%'
        },
        fontSize: 14,
        vAxis: {title: "Cluster Volume"},
        hAxis: {gridlines: {count: data.getNumberOfRows()/31}}

    };

    var chart = new google.visualization.LineChart(document.getElementById('general_line_chart'));
    chart.draw(data, options);
}
/**
 * draw a word count pie chart on details page
 * @param array
 */
function drawWordPieChart(array) {
    var data = google.visualization.arrayToDataTable(array);

    var options = {
      is3D: true,
        animation: {
            duration: 10000,
            easing: 'out',
            startup: true
          },
        fontName: "Lato",
        title: 'Top Ten Words'
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart_3d'));
    chart.draw(data, options);
}

/**
 * draws the line chart
 * y axis is number of posts
 * x axis is date
 * @param data the js data from python views.py
 * @returns {google.visualization.ControlWrapper}
 */
function draw_dashboard1(data) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('number', 'Posts');
    for (key in data) {
        //console.log(new Date(parseInt(key)));
        lineChartData.addRows([
            [new Date(parseInt(key)), data[key]['numPosts']]
        ]);

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
                'cssClass': 'sliderClass',
                'label':''
            }
        }
    });
    // Line chart visualization
    var myLine = new google.visualization.ChartWrapper({
        'chartType': 'ColumnChart',
        'containerId': 'line_chart',
        'ui': {
            'cssClass':'spikeGraph'
        },
        view: {
            columns: [0, 1]
        },
        'options': {
            fontName: "Lato",
            'colors': ['#F5881D'],
            'tooltip': {isHtml:true}
        },
        vAxis: {
            'gridlines': {
                color: 'transparent'
            },
            baselineColor: 'transparent'
        }
    });


    // Bind myLine to the dashboard, and to the controls
    // this will make sure our line chart is update when our date changes
    myDashboard.bind(myDateSlider, myLine);

    myDashboard.draw(lineChartData);

    return myDateSlider;
}
/**
 * draws the table of posts and their dates
 * @param data from python views.py
 * @returns {google.visualization.ControlWrapper}
 */
function draw_dashboard2(data) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('string', 'Post');
    for (key in data) {
        for (i = 0; i < data[key]['posts'].length; i++) {
            lineChartData.addRows([
                [new Date(parseInt(key)), data[key]['posts'][i]]
            ]);
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
            'filterColumnLabel': 'Date'
        }
    });

    // Create a searchbar
    var searchBar = new google.visualization.ControlWrapper({
        'controlType': 'StringFilter',
        'containerId': 'searchTable',
        'options': {
            'filterColumnLabel': 'Post',
            'matchType': 'any',
            'ui': {'label': 'Search Posts', 'labelSeparator': ':'}
        }

    });

    // Table visualization
    var myTable = new google.visualization.ChartWrapper({
        'chartType': 'Table',
        'containerId': 'table_chart',
        'options': {
            'page': 'enable',
            'pageSize': 50,
            'sortColumn': 0,
            'fontName': "Lato"
        }
    });


    // Bind myTable to the dashboard, and to the controls
    // this will make sure our table is update when our date changes
    myDashboard.bind(myDateSlider, myTable);
    myDashboard.bind(searchBar, myTable);


    myDashboard.draw(lineChartData);
    return myDateSlider;

}