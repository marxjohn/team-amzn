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

    function selectHandler() {
        var selectItem = chart.getSelection()[0];
        var num = selectItem.row + 1
        var url = '/topics/' + num.toString()
        window.location = url
    }

    google.visualization.events.addListener(chart, 'select', selectHandler);
    chart.draw(data, options);
}

function drawSentimentChart(array) {
    var data = google.visualization.arrayToDataTable(array);

    var options = {
        animation: {
            duration: 1000,
            easing: 'out',
            startup: true
          },
        legend: {
          position:"none"
        },
        isStacked: true,
        fontName: "Lato",
        colors: ['#DC3912', '#95a5a6','#109618'],
        bar: {groupWidth: '80%'}
    };

    var chart = new google.visualization.BarChart(document.getElementById('sentiment_barchart'));
    chart.draw(data, options);
}

function drawGeneralLineChart(array, lineDates, clusterNames) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Day');

    for(i=0; i<clusterNames.length; i++) {
        data.addColumn('number', clusterNames[i]);
    }

    for(i=0; i< lineDates.length; i++) {
        row = [new Date(lineDates[i])];

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
            height: '80%'
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
function draw_column_chart(data) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('number', 'Negative');
    lineChartData.addColumn('number', 'Neutral');
    lineChartData.addColumn('number', 'Positive');
    for (key in data) {
        lineChartData.addRows([
            [new Date(parseInt(key)), data[key]['neg'], data[key]['neutral'], data[key]['pos']]
        ]);

    }

var options = {
         'ui': {
            'cssClass':'spikeGraph'
        },
    view: {
            columns: [0, 1]
        },
        fontName: "Lato",
        colors: ['#DC3912', '#95a5a6','#109618'],
        'tooltip': {isHtml:true},
        vAxis: {
            'gridlines': {
                color: 'transparent'
            },
            baselineColor: 'transparent'
        },
        //legend: { position: 'top', maxLines: 3 },
        //bar: { groupWidth: '75%' },
        isStacked: true
      };

var chart = new google.visualization.ColumnChart(document.getElementById("line_chart"));
      chart.draw(lineChartData, options);


}
/**
 * draws the table of posts and their dates
 * @param data from python views.py
 * @returns {google.visualization.ControlWrapper}
 */
function draw_table(data) {
    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('string', 'Sentiment');
    lineChartData.addColumn('string', 'Post');
    for (key in data) {
        lineChartData.addRows([
            [new Date(parseInt(data[key]['date'])), data[key]['sentiment'], data[key]['body']]
        ]);
    }
    // Create a dashboard.
    var dash_container = document.getElementById('dashboard'),
        myDashboard = new google.visualization.Dashboard(dash_container);

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

    myDashboard.bind(searchBar, myTable);
    myDashboard.draw(lineChartData);
}

function drawClusterSentimentChart(array) {
    var data = google.visualization.arrayToDataTable(array);

    var options = {
        animation: {
            duration: 1000,
            easing: 'out',
            startup: true
          },
        legend: {
          position:"none"
        },
        axisTitlesPosition:"none",
        isStacked: true,
        fontName: "Lato",
        colors: ['#DC3912', '#95a5a6','#109618'],
        bar: {groupWidth: '30%'},
        height: '100',
        hAxis: { textPosition: 'none',
        baselineColor: '#fff',
         gridlineColor: '#fff'},
        vAxis: { textPosition: 'none',
        baselineColor: '#fff',
         gridlineColor: '#fff'}
    };

    var chart = new google.visualization.BarChart(document.getElementById('sentiment_barchart'));
    chart.draw(data, options);
}