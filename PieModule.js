var PieModule = function(bins, canvas_width, canvas_height) {
    // Create the elements

    // Create the tag:
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    // Append it to body:
    var canvas = $(canvas_tag)[0];
    $("body").append(canvas);
    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");


    // Prep the chart properties and series:
    var datasets = [{
        label: "Data",
        // fillColor: 'rgba(75, 192, 192, 0.2)',
        // strokeColor: "rgba(151,187,205,0.8)",
        // highlightFill: "rgba(151,187,205,0.75)",
        // highlightStroke: "rgba(151,187,205,1)",
        data: []
    }];

    for (var i in bins)
        datasets[0].data.push(1);

    var data = {
        labels: bins,
        datasets: datasets
    };
// var ctx = document.getElementById("myChart").getContext("2d");
    var options = {
    };


    // Create the chart object
    var chart = new Chart(context).Pie(data,options);
// var chart = new Chart(context, config);



    // Now what?
    this.render = function(data) {
        // var new_data = [];
        // for (var i=0;i<5;i++){
        //     new_data.push({value: 2, color: colors[i]});
        // }
        // chart.data = new_data;
        chart.update();
    };

    this.reset = function() {
        chart.destroy();
        // chart = new Chart(context).Bar(data, options);
    };
};