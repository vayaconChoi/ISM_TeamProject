// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#292b2c";

var xValues = ["Now", "10days", "20days", "30days"];

var yValues = [
  {
    label: "사과",
    data: [32000, 34000, 40000, 38000],
    borderColor: "red",
    fill: false,
  },
  {
    label: "배",
    data: [20000, 30000, 28000, 31000],
    borderColor: "green",
    fill: false,
  },
];

var height = Math.max.apply(Math, [Math.max.apply(Math, yValues[0].data), Math.max.apply(Math, yValues[1].data)]) * 1.2;

// line Chart
var ctx = document.getElementById("predicted_price_chart");
var myLineChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: xValues,
    datasets: yValues,
  },
  options: {
    scales: {
      yAxes: [
        {
          ticks: {
            min: 0,
            max: height,
          },
        },
      ],
    },
  },
});
