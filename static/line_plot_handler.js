const config = {
    type: 'line',
    data: {
        datasets: [
            {
                data: [],
                stepped: 'middle',
                fill: true,
                borderColor: 'rgb(0,0,255)',
            },
            {
                data: [],
                stepped: 'middle',
                fill: true,
                borderColor: 'rgb(255,128,0)',
            },
            {
                data: [],
                stepped: 'middle',
                fill: true,
                borderColor: 'rgb(255,0,0)',
            }
        ]
    },
    options: {
        plugins: {
            title: {
                text: 'График измерений',
                display: true
            },
            legend: {
                display: false
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Время',
                    font: {
                        size: 16
                    }
                },
                type: 'time',
                time: {
                    displayFormats: {
                        millisecond: 'HH:mm:ss',
                        second: 'HH:mm:ss',
                        minute: 'HH:mm',
                        hour: 'HH'
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Ток, А',
                    font: {
                        size: 16
                    }
                }
            }
        },
        elements: {
            point: {
                radius: 0
            },
            line: {
                borderWidth: 1
            }
        },
        interaction: {
            mode: false
        },
        animation: false
    }
}

let ctx = document.getElementById('chart').getContext('2d')
let myChart = new Chart(ctx, config)

$(document).ready(function () {
    updatePlotData()
})

$('#update_plot').click(function (e) {
    updatePlotData()
})

let timerId
$('#auto_update').click(function (e) {
    if (e.target.checked) {
        timerId = setTimeout(function run() {
            updatePlotData()
            timerId = setTimeout(run, 1000)
        }, 1000)
    } else {
        clearTimeout(timerId)
    }
})

function updatePlotData() {
    const start_time = document.getElementById('start_time').value
    const end_time = document.getElementById('end_time').value
    const start_date = document.getElementById('start_date').value
    const points_number = document.getElementById('points_number').value

    $.ajax({
        url: api_url,
        method: 'get',
        dataType: 'json',
        data: {
            unit_id: unit_id,
            start_date: start_date,
            start_time: start_time,
            end_time: end_time,
            points_number: points_number
        },
        success: function (response) {
            console.log(response)
            config.data.datasets[0].data = response
            myChart.update()
        },
        error: function (response) {
            console.log('ajax error')
        }
    })
}
