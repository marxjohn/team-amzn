/**
 * Created by CJ on 2/18/2015.

 * this function allows for multiple dashboards to act as one
 * useful because the different charts will use different data.
 * the slider from control 2 is tied to the slider from control1
 * so that one changes the other.
 */
function draw_all_dashboards(data) {
    var control1 = draw_dashboard1(data);
    var control2 = draw_dashboard2(data);
    google.visualization.events.addListener(control1, 'statechange', function () {
        control2.setState({
            'lowValue': new Date(control1.getState()['lowValue']),
            'highValue': new Date(control1.getState()['highValue'])
        });
        control2.draw();
    });
}