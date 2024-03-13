
$(function() {

    
//   const apiUrl = 'api/get_chart_data';


//   var options = {
//     scales: {
//       yAxes: [{
//         ticks: {
//           beginAtZero: true
//         },
//         gridLines: {
//           color: "rgba(204, 204, 204,0.1)"
//         }
//       }],
//       xAxes: [{
//         gridLines: {
//           color: "rgba(204, 204, 204,0.1)"
//         }
//       }]
//     },
//     legend: {
//       display: false
//     },
//     elements: {
//       point: {
//         radius: 0
//       }
//     }
//   };
  
//   fetch(apiUrl)
//       .then((response) => response.json())
//       .then((data) => {
//           // Once you have the data, initialize your chart
//           // initializeChart(data);
//             console.error("Data in top: "+ data)

//           // Initialize arrays to hold the converted data
//               var labels = [];
//               var dataPoints = [];
//               var backgroundColors = [];
//               var borderColors = [];

//               // Process the original data
//               data.forEach(function(item) {
//                   labels.push(item.Name);            // Push contributor names as labels
//                   dataPoints.push(item.TotalViews);  // Push total views as data points
//                   // You can customize colors here if needed
//                   backgroundColors.push('rgba(255, 99, 132, 0.2)');
//                   borderColors.push('rgba(255,99,132,1)');
//               });
//               console.error("Labels: "+labels)
//               // Create the converted data object
//               var convertedData = {
//                   labels: labels,
//                   datasets: [{
//                       label: '# of Votes',
//                       data: dataPoints,
//                       backgroundColor: backgroundColors,
//                       borderColor: borderColors,
//                       borderWidth: 1,
//                       fill: false
//                   }]
//               };
//               console.error("Convertted data: "+convertedData)
//         //      initializeChart(JSON.stringify(convertedData  ))

//       })
//       .catch((error) => {
//           console.error('Error fetching data:', error);
//       });


var data = {
  labels: ["2013", "2014", "2014", "2015", "2016", "2017"],
  datasets: [{
    label: '# of Votes',
    data: [10, 19, 3, 5, 2, 3],
    backgroundColor: [
      'rgba(255, 99, 132, 0.2)',
      'rgba(54, 162, 235, 0.2)',
      'rgba(255, 206, 86, 0.2)',
      'rgba(75, 192, 192, 0.2)',
      'rgba(153, 102, 255, 0.2)',
      'rgba(255, 159, 64, 0.2)'
    ],
    borderColor: [
      'rgba(255,99,132,1)',
      'rgba(54, 162, 235, 1)',
      'rgba(255, 206, 86, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(153, 102, 255, 1)',
      'rgba(255, 159, 64, 1)'
    ],
    borderWidth: 1,
    fill: false
  }]
};   


var options = {
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        },
        gridLines: {
          color: "rgba(204, 204, 204,0.1)"
        }
      }],
      xAxes: [{
        gridLines: {
          color: "rgba(204, 204, 204,0.1)"
        }
      }]
    },
    legend: {
      display: false
    },
    elements: {
      point: {
        radius: 0
      }
    }
  };
// var myChart = new Chart($('#mychart'),{type:'bar'});

 if ($("#barChart").length) {
  var barChartCanvas = $("#barChart").get(0).getContext("2d");
  // This will get the first returned node in the jQuery collection.
  var barChart = new Chart(barChartCanvas, {
    type: 'bar',
    data: data,
    options: options
  });
 }
 if ($("#lineChart").length) {
  var lineChartCanvas = $("#lineChart").get(0).getContext("2d");
  var lineChart = new Chart(lineChartCanvas, {
    type: 'line',
    data: data,
    options: options
  });
}


});