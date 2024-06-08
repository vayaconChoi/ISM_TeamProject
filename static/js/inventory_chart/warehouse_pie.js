// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#292b2c";

// 얘네들 Class로 만들어서 데이터 유동적으로 받아올 필요 있어보임
var xValues = ["사과", "배"];
var yValues = [335, 284];
var barColors = ["red", "yellow"];
var text = "00창고 상품현황";
// Pie Chart
var ctx = document.getElementById("WarehousePie");
var warePieChart = new Chart(ctx, {
  type: "pie",
  data: {
    labels: xValues,
    datasets: [
      {
        data: yValues,
        backgroundColor: barColors,
      },
    ],
  },
  options: {
    title: {
      display: true,
      text: text,
    },
  },
});
