/**
 * Created by MaxGoovaerts and CJ on 2/8/2015.
 */

//Convert date into UTC to avoid Javascript misconverting
function convertDateToUTC(date) {
    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds());
    }

//Draw Pie chart on home page
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

//Draw Sentiment Chart on main page
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
        chartArea: {
            width:"100%",
            left:"30%",
            height:"150%"
        },
        isStacked: true,
        fontName: "Lato",
        colors: ['#DC3912', '#95a5a6','#109618'],
        //bar: {groupWidth: '60%'}
    };

    var chart = new google.visualization.BarChart(document.getElementById('sentiment_barchart'));
    chart.draw(data, options);
}

//Draw Line Chart on main page
function drawGeneralLineChart(array, lineDates, clusterNames) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Day');

    for(i=0; i<clusterNames.length; i++) {
        data.addColumn('number', clusterNames[i]);
    }

    for(i=0; i< lineDates.length; i++) {
        row = [convertDateToUTC(new Date(lineDates[i]))];

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
 * draw word count pie chart on details page
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
 * draws the column chart on the details page
 * y axis is number of posts
 * x axis is date
 * @param data the js data from python views.py
 * @returns {google.visualization.ControlWrapper}
 */
function draw_column_chart(data) {

    var lineChartData = new google.visualization.DataTable();

    lineChartData.addColumn('date', 'Date');
    lineChartData.addColumn('number', 'Negative Posts');
    lineChartData.addColumn('number', 'Neutral Posts');
    lineChartData.addColumn('number', 'Positive Posts');
    for (key in data) {
        lineChartData.addRows([
            [convertDateToUTC(new Date(parseInt(key))), data[key]['neg'], data[key]['neutral'], data[key]['pos']]
        ]);

    }

var options = {
         'ui': {
            'cssClass':'spikeGraph'
        },
        view: {columns: [0, 1]},
        fontName: "Lato",
        colors: ['#DC3912', '#95a5a6','#109618'],
        'tooltip': {isHtml:true},
        legend: { position: 'top', maxLines: 3 },
        bar: { groupWidth: '80%' },
        isStacked: true,
        hAxis: {gridlineColor: '#fff'},
        vAxis: {gridlineColor: '#fff'},
    width: "100%"
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
    lineChartData.addColumn('string', 'Link');
    lineChartData.addColumn('string', 'Post');

    for (key in data) {
        var link = '<a href="https://sellercentral.amazon.com/forums/thread.jspa?messageID='
            + data[key]['messageId'] + "#" + data[key]['messageId'] + '">ASF</a>';
        var date = new Date((parseInt(data[key]['date'])));
        var utcdate = convertDateToUTC(date);
        lineChartData.addRows([
            [utcdate, data[key]['sentiment'], link, data[key]['body']]
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
            'fontName': "Lato",
            'allowHtml': true
        }
    });

    myDashboard.bind(searchBar, myTable);
    myDashboard.draw(lineChartData);
}

//Draw sentiment chart on the details page
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

    var chart = new google.visualization.BarChart(document.getElementById('sentiment_cluster_barchart'));
    chart.draw(data, options);
}