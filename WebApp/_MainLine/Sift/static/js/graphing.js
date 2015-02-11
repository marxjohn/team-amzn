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

//function drawDashboard(mod, post, categoryid, year, month, day) {
//        var data = new google.visualization.DataTable();
//
//        data.addColumn('date', 'Date');
//        data.addColumn('number', 'Posts');
//        for(i=0; i<count.length; i++)
//        {
//            data.addRows([
//                [new Date(year[i], month[i], day[i]), count[i]]
//            ])
//        }
//
//
//        var options = {
//          title: 'Number of Forum Posts over Time',
//          displayAnnotations: true
//        };
//
//        var chart = new google.visualization.AnnotationChart(document.getElementById('linechart_annotation'));
//        chart.draw(data, options);
//    }

