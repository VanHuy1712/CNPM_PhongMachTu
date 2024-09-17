function drawChart(type, labels, data, id='myChart', label='# Doanh Thu') {
    const ctx = document.getElementById(id);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: data,
        borderWidth: 1,
        backgroundColor: [
          'rgba(54, 162, 235, 0.2)',
        ],
        borderColor: [
          'rgb(54, 162, 235)',
        ]
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}