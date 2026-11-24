const refresh_badge = document.getElementById("last_update");
const last_refresh = Number(refresh_badge.getAttribute("data-measured-at"));

function calculate_time_diff(){
    const time_now = Date.now();
    const diff = Math.floor((time_now - last_refresh)/ 60000);
    refresh_badge.textContent = `Od ostatniej aktualizacji: ${diff} min`;
}

calculate_time_diff();
setInterval(calculate_time_diff, 10000);



const ctx = document.getElementById('myChart');
const myChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Temperatura (°C)",
            borderColor: "red",
            backgroundColor: "rgba(255,0,0, 0.1)",
            data: [],
            borderColor: "red",
            fill: false,
            yAxisID: 'y1'
            },
            {
            label: "Wilgotność (%)",
            borderColor: "blue",
            backgroundColor: "rgba(0,0,255,0.1)",
            data: [],
            borderColor:"blue",
            fill: false,
            yAxisID: 'y2'
            }]
    },
    options: {
        plugins: {
            legend: {
                display: true,
            },
            title: {
                text:"Wykres temperatury i wilgotności względem czasu",
                display: true
            }
        },
        scales: {
            x: {  
                type: 'time',
                time: {
                    unit: 'hour',
                    displayFormats: {
                        hour:'HH:mm',
                        day: 'dd.MM'
                    },
                },
                title: {
                    display: true,
                    text: 'Data i godzina'
                }
            },
            y1: {
                type: 'linear',
                position: 'left',
                title: {
                    display: true,
                    text: "Temperatura"
                }
            },
            y2: {
                type: 'linear',
                position: 'right',
                title: {
                    display: true,
                    text: "Wilgotność"
                }
            }


        }
    }
});

async function getChartData(query_param=1){ 
    try {
        const response = await fetch(`/api/measurements/?days=${query_param}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        }
        });
        if (response.ok) {
            const data = await response.json();
            let temperature = data.map(row => row.temperature);
            let humidity = data.map(row => row.humidity);
            let dates = data.map(row => row.measured_at);
            myChart.data.labels = dates;
            myChart.data.datasets[0].data = temperature;
            myChart.data.datasets[1].data = humidity;
            myChart.options.scales.x.time.unit = query_param == 1 ? 'hour' : 'day'; 
            myChart.update()
            
        } else {
            throw new Error(`Błąd HTTP: ${response.status}`);
        }
    } catch (error) {
        alert('Wystąpił błąd podczas pobierania danych.')
    }
}

async function fetchAPIdata(){
    try{
        const response = await fetch("/api/external/");
        if (!response.ok){
            throw new Error(`HTTP error: ${response.status}`);
        }
        const data = await response.json();
        let odczyt = Object.entries(data);
        let tbody = document.getElementById("table-body");
        tbody.replaceChildren();
        for (let [name, readings] of odczyt){
            let tr = document.createElement("tr");
            for (let r of [name, readings.temperature ?? "-", readings.humidity ?? "-", readings.time ?? "-"]){
                let td = document.createElement("td");
                td.textContent = r;
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
    } catch (error) {
        console.error(`Wystąpił błąd podczas pobierania danych: ${error}`)
    }
}


const range_buttons = document.querySelectorAll(".range");
range_buttons.forEach(button => {
    button.addEventListener('click', () => {
        const query_param = button.getAttribute("data-range")
        getChartData(query_param)
    });
});

getChartData(1);
fetchAPIdata();