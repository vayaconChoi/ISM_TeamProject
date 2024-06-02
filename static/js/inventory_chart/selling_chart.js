// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#292b2c";

var xValues = [
    '2024.01','2024.02','2024.03','2024.04','2024.05'
]

var yValues =[
    {
        label: "사과",
        data: [7830, 2478, 2210, 1330, 1110],
        borderColor: "red",
        fill: false
    },
    {
        label: "배",
        data: [7000, 6000, 5000, 4000, 2700],
        borderColor: "green",
        fill: false
    },
]

var height = Math.max.apply( 
    Math,
    [Math.max.apply(Math,yValues[0].data),  Math.max.apply(Math, yValues[1].data)] 
) * 1.2;

// line Chart
var ctx = document.getElementById("InventoryLine");
var myLineChart = new Chart(ctx,{
    type: "line",
    data: {
        labels: xValues,
        datasets: yValues
    },
    options: {
        scales:{
            yAxes:[
                {
                    ticks:{
                        min: 0,
                        max: height
                    }
                }
            ]
        }
    }
});