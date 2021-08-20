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
        position: 'bottom',
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

let delayedUpdateTimerId = null
$('#start-date').change(function (e) {
  updatePlotWithDelay()
})

function updatePlotWithDelay () {
  clearTimeout(delayedUpdateTimerId)
  delayedUpdateTimerId = setTimeout(function () {
    updatePlot()
  }, 500)
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
      let timesList = Array(limitValues.length + 2).fill(0)
      let lastLimitId = null
      let lastLimitStartTime = null
      for (let i = 0; i < response.length; i++) {
        const newData = response[i]

        let newLimitId = null
        if (newData.y == null) {
          newLimitId = limitValues.length + 1
        } else {
          for (let i = 0; i < limitValues.length; i++) {
            if (newData.y > limitValues[i]) {
              newLimitId = i
              break
            }
          }
          if (newLimitId == null) {
            newLimitId = limitValues.length
          }
        }

        if (newLimitId !== lastLimitId) {
          const lastLimitEndTime = Date.parse(newData.x)
          if (lastLimitId) {
            timesList[lastLimitId] += lastLimitEndTime - lastLimitStartTime
          }
          lastLimitId = newLimitId
          lastLimitStartTime = lastLimitEndTime
        }
      }
      const startTime = Date.parse(response[0].x)
      const endTime = Date.parse(response[response.length - 1].x)
      timesList[lastLimitId] += endTime - lastLimitStartTime

      document.getElementById('time-total').
        textContent = getTime(endTime - startTime)
      document.getElementById('time-work').
        textContent = getTime(timesList[0])
      document.getElementById('time-no_load').
        textContent = getTime(timesList[1])
      document.getElementById('time-stop').
        textContent = getTime(timesList[2])
      document.getElementById('time-unknown').
        textContent = getTime(timesList[3])

      dataset.data = timesList
      myChart.update()
    },
    error: function (response) {
      console.log('ajax error')
      dataset.data = []
      document.getElementById('time-total').
        textContent = '00:00'
      document.getElementById('time-work').
        textContent = '00:00'
      document.getElementById('time-no_load').
        textContent = '00:00'
      document.getElementById('time-stop').
        textContent = '00:00'
      document.getElementById('time-unknown').
        textContent = '00:00'
      myChart.update()
    },
  })
}

function getTime (timestamp) {
  return new Date(timestamp).toISOString().substring(11, 16)
}
