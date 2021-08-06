const config = {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                data: [],
                stepped: 'middle',
                fill: true,
                borderColor: 'rgb(0,0,255)',
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

const ctx = document.getElementById('chart').getContext('2d')
const myChart = new Chart(ctx, config)

$('#update_plot_button').click(function (e) {
    updatePlotData()
})

$(document).ready(function () {
    updatePlotData()
})

function updatePlotData() {
    $.ajax({
        url: api_url,
        method: 'get',
        dataType: 'json',
        data: {
            unit_id: unit_id,
            start_date: document.getElementById('start_date').value,
            start_time: document.getElementById('start_time').value,
            end_time: document.getElementById('end_time').value,
            points_number: document.getElementById('points_number').value
        },
        success: function (response) {
            const values = []
            const times = []
            for (let i = 0; i < response.length; i++) {
                values[i] = response[i].value
                times[i] = response[i].time
            }
            config.data.labels = times
            config.data.datasets[0].data = values
            myChart.update()
        },
        error: function (response) {
            console.log('ajax error')
        }
    })
}
