/**
 * Created by MaxGoovaerts on 2/8/2015.
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

    function drawTimeLineChart(count, year, month, day) {
        var data = new google.visualization.DataTable();

        data.addColumn('date', 'Date');
        data.addColumn('number', 'Posts');
        for(i=0; i<count.length; i++)
        {
            data.addRows([
                [new Date(year[i], month[i], day[i]), count[i]]
            ])
        }


        var options = {
          title: 'Number of Forum Posts over Time',
          displayAnnotations: true
        };

        var chart = new google.visualization.AnnotationChart(document.getElementById('linechart_annotation'));
        chart.draw(data, options);
    }

    function drawDashboard(count) {

        var lineChartData = new google.visualization.DataTable();

        lineChartData.addColumn('date', 'Date');
        lineChartData.addColumn('number', 'Posts');
        for(key in count)
        {
            //console.log(new Date(parseInt(key)));
            lineChartData.addRows([
                [new Date(parseInt(key)), count[key]['numPosts']]
            ])
        }

        // Create a dashboard.
          var dash_container = document.getElementById('dashboard_div'),
            myDashboard = new google.visualization.Dashboard(dash_container);


                // Create a date range slider
          var myDateSlider = new google.visualization.ControlWrapper({
            'controlType': 'ChartRangeFilter',
            'containerId': 'control_div',
            'options': {
              'filterColumnLabel': 'Date'
            }
          });
                // Line chart visualization
          var myLine = new google.visualization.ChartWrapper({
            'chartType' : 'ColumnChart',
            'containerId' : 'line_div',
          });

          // Bind myLine to the dashboard, and to the controls
          // this will make sure our line chart is update when our date changes
          myDashboard.bind(myDateSlider, myLine );

          myDashboard.draw(lineChartData);

    }