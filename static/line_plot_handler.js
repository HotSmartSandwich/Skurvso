const limitValues = [
  2000,
  1000,
]
const plotColors = [
  'rgb(0,0,255)',
  'rgb(255,128,0)',
  'rgb(255,0,0)',
]

const datasets = []
for (let i = 0; i <= limitValues.length; i++) {
  datasets.push({
    borderColor: plotColors[i],
    data: [],
    fill: true,
    stepped: 'middle',
  })
}

function clearDatasets () {
  for (let i = 0; i < datasets.length; i++) {
    datasets[i].data = []
  }
}

const config = {
  type: 'line',
  data: {
    datasets: datasets,
  },
  options: {
    plugins: {
      title: {
        text: 'График измерений',
        display: false,
      },
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        title: {
          display: false,
          text: 'Время',
          font: {
            size: 16,
          },
        },
        type: 'time',
        time: {
          displayFormats: {
            millisecond: 'HH:mm:ss',
            second: 'HH:mm:ss',
            minute: 'HH:mm',
            hour: 'HH',
          },
        },
      },
      y: {
        title: {
          display: false,
          text: 'Ток, А',
          font: {
            size: 16,
          },
        },
      },
    },
    elements: {
      point: {
        radius: 0,
      },
      line: {
        borderWidth: 1,
      },
    },
    interaction: {
      mode: false,
    },
    animation: false,
  },
}

const ctx = document.getElementById('chart').getContext('2d')
const myChart = new Chart(ctx, config)

let delayedUpdateTimerId = null

$(document).ready(function () {
  updatePlot()
})

$('#startDate').change(function (e) {
  updatePlotWithDelay()
})
$('#startTime').change(function (e) {
  updatePlotWithDelay()
})
$('#endTime').change(function (e) {
  updatePlotWithDelay()
})
$('#pointsNumber').change(function (e) {
  updatePlot()
})

let autoUpdateTimerId = null
$('#autoUpdateButton').click(function (e) {
  if (e.target.checked) {
    autoUpdateTimerId = setTimeout(function run () {
      updatePlot()
      autoUpdateTimerId = setTimeout(run, 1000)
    }, 1000)
  } else {
    clearTimeout(autoUpdateTimerId)
  }
})

function updatePlotWithDelay () {
  clearTimeout(delayedUpdateTimerId)
  delayedUpdateTimerId = setTimeout(function () {
    updatePlot()
  }, 500)
}

function updatePlot () {
  const startDate = document.getElementById('startDate').value
  const startTime = document.getElementById('startTime').value
  const endTime = document.getElementById('endTime').value
  const pointsNumber = document.getElementById('pointsNumber').value

  $.ajax({
    url: apiUrl,
    method: 'get',
    dataType: 'json',
    data: {
      unitId: unitId,
      startDate: startDate,
      startTime: startTime,
      endTime: endTime,
      pointsNumber: pointsNumber,
    },
    success: function (response) {
      clearDatasets()
      if (1) {
        config.options.scales.x.min = Date.parse(startDate + 'T' + startTime)
        config.options.scales.x.max = Date.parse(startDate + 'T' + endTime)
      }

      let lastLimitId = null
      for (let i = 0; i < response.length; i++) {
        const newData = response[i]
        if (newData.y == null) {
          try {
            datasets[lastLimitId].data.push(newData)
          } catch (error) {}
          continue
        }

        let newLimitId = null
        for (let i = 0; i < limitValues.length; i++) {
          if (newData.y > limitValues[i]) {
            newLimitId = i
            break
          }
        }
        if (newLimitId == null) {
          newLimitId = limitValues.length
        }

        if (newLimitId !== lastLimitId) {
          const lastData = response[i - 1]
          try {
            datasets[lastLimitId].data.push({ x: lastData.x, y: null })
            datasets[newLimitId].data.push({ x: lastData.x, y: lastData.y })
          } catch (error) {}

          lastLimitId = newLimitId
        }
        datasets[newLimitId].data.push(newData)
      }
      myChart.update()
    },
    error: function (response) {
      console.log('ajax error')
      clearDatasets()
      myChart.update()
    },
  })
}
