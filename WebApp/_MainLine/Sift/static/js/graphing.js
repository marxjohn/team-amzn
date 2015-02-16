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

    function drawDashboard(post, categoryid, year, month, day) {
        var data = new google.visualization.DataTable();

        data.addColumn('string', 'Category');
        data.addColumn('string', 'Post');
        data.addColumn('date', 'Date');

        for(i=0; i<post.length; i++)
        {
            data.addRows([
                [categoryid[i], post[i], new Date(year[i], month[i], day[i])]
            ])
        }

        var dashboard = new google.visualization.Dashboard(
            document.getElementById('dashboard_div'));

        var catFilter = new google.visualization.ControlWrapper({
            'controlType': 'CategoryFilter',
            'containerId': 'category_filter',
            'options': {
              'filterColumnLabel': 'Category'
            }
        });

        var dataTable = new google.visualization.ChartWrapper({
            'chartType': 'Table',
            'containerId': 'table_div',
            'options': {
                'title': 'Data Table',
                'page': 'enable',
                'pagesize': '20'
            }
        });

        dashboard.bind(catFilter, dataTable);
        dashboard.draw(data);
    }

 function drawTutorialDashboard() {

        // Create our data table.
        var data = google.visualization.arrayToDataTable([
          ['Name', 'Donuts eaten'],
          ['Michael' , 5],
          ['Elisa', 7],
          ['Robert', 3],
          ['John', 2],
          ['Jessica', 6],
          ['Aaron', 1],
          ['Margareth', 8]
        ]);

        // Create a dashboard.
        var dashboard = new google.visualization.Dashboard(
            document.getElementById('tut_dashboard_div'));

        // Create a range slider, passing some options
        var donutRangeSlider = new google.visualization.ControlWrapper({
          'controlType': 'NumberRangeFilter',
          'containerId': 'tut_filter_div',
          'options': {
            'filterColumnLabel': 'Donuts eaten'
          }
        });

        // Create a pie chart, passing some options
        var pieChart = new google.visualization.ChartWrapper({
          'chartType': 'PieChart',
          'containerId': 'tut_chart_div',
          'options': {
            'width': 300,
            'height': 300,
            'pieSliceText': 'value',
            'legend': 'right'
          }
        });

        // Establish dependencies, declaring that 'filter' drives 'pieChart',
        // so that the pie chart will only display entries that are let through
        // given the chosen slider range.
        dashboard.bind(donutRangeSlider, pieChart);

        // Draw the dashboard.
        dashboard.draw(data);
      }

