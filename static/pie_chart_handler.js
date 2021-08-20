const dataset = {
  data: [],
  backgroundColor: plotColors,
}

const config = {
  type: 'pie',
  data: {
    labels: labels,
    datasets: [dataset],
  },
  options: {
    plugins: {
      title: {
        text: 'Круговая диаграмма',
        display: false,
      },
      legend: {
        display: true,
      },
    },
  },
}

const ctx = document.getElementById('pie-chart').getContext('2d')
const myChart = new Chart(ctx, config)

$(document).ready(function () {
  updatePlot()
  setTimeout(function run () {
    updatePlot()
    setTimeout(run, 60000)
  }, 60000)
})

function clearDataset () {
  dataset.data = Array(limitValues.length + 2).fill(0)
}

function updatePlot () {
  const startDate = document.getElementById('start-date').value

  $.ajax({
    url: apiUrl,
    method: 'get',
    dataType: 'json',
    data: {
      unitId: unitId,
      startDate: startDate,
    },
    success: function (response) {
      clearDataset()

      for (let i = 0; i < response.length; i++) {
        const value = response[i].y
        if (value == null) {
          dataset.data[limitValues.length + 1] += 1
          continue
        }

        let valueId = null
        for (let i = 0; i < limitValues.length; i++) {
          if (value > limitValues[i]) {
            valueId = i
            break
          }
        }
        if (valueId == null) {
          valueId = limitValues.length
        }

        dataset.data[valueId] += 1
      }
      myChart.update()
    },
    error: function (response) {
      console.log('ajax error')
      clearDataset()
      myChart.update()
    },
  })
}
