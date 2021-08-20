const lineChartDatasets = []
for (let i = 0; i <= limitValues.length; i++) {
  lineChartDatasets.push({
    borderColor: plotColors[i],
    label: labels[i],
    data: [],
    fill: true,
    stepped: 'middle',
  })
}

const lineChartConfig = {
  type: 'line',
  data: {
    datasets: lineChartDatasets,
  },
  options: {
    plugins: {
      title: {
        text: 'График измерений',
        display: false,
      },
      legend: {
        display: true,
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

const lineChartCanvas = document.getElementById('line-chart').getContext('2d')
const lineChart = new Chart(lineChartCanvas, lineChartConfig)

$(document).ready(function () {
  updateLineChart()
})

let delayedLineChartUpdateTimerId = null
$('#start-date').change(function (e) {
  updateLineChartWithDelay()
})
$('#start-time').change(function (e) {
  updateLineChartWithDelay()
})
$('#end-time').change(function (e) {
  updateLineChartWithDelay()
})
$('#points-number').change(function (e) {
  updateLineChart()
})

let autoUpdateTimerId = null
$('#auto-update-button').click(function (e) {
  if (e.target.checked) {
    autoUpdateTimerId = setTimeout(function run () {
      if ($('#output-type-line').is(':checked')) {
        updateLineChart()
      }
      autoUpdateTimerId = setTimeout(run, 1000)
    }, 1000)
  } else {
    clearTimeout(autoUpdateTimerId)
  }
})

function updateLineChartWithDelay () {
  clearTimeout(delayedLineChartUpdateTimerId)
  delayedLineChartUpdateTimerId = setTimeout(function () {
    updateLineChart()
  }, 500)
}

function clearLineChartDatasets () {
  for (let i = 0; i < lineChartDatasets.length; i++) {
    lineChartDatasets[i].data = []
  }
}

function updateLineChart () {
  const startDate = document.getElementById('start-date').value
  const startTime = document.getElementById('start-time').value
  const endTime = document.getElementById('end-time').value
  const pointsNumber = document.getElementById('points-number').value

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
      clearLineChartDatasets()
      if (1) {
        lineChartConfig.options.scales.x.min = Date.parse(
          startDate + 'T' + startTime)
        lineChartConfig.options.scales.x.max = Date.parse(
          startDate + 'T' + endTime)
      }

      let lastLimitId = null
      for (let i = 0; i < response.length; i++) {
        const newData = response[i]
        if (newData.y == null) {
          try {
            lineChartDatasets[lastLimitId].data.push(newData)
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
            lineChartDatasets[lastLimitId].data.push({ x: lastData.x, y: null })
            lineChartDatasets[newLimitId].data.push(
              { x: lastData.x, y: lastData.y })
          } catch (error) {}

          lastLimitId = newLimitId
        }
        lineChartDatasets[newLimitId].data.push(newData)
      }
      lineChart.update()
    },
    error: function (response) {
      console.log('ajax error')
      clearLineChartDatasets()
      lineChart.update()
    },
  })
}
