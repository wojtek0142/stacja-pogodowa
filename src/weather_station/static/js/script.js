let dane_testowe = [
  {
    "temperature": 21.5,
    "humidity": 45.2,
    "measured_at": "2026-11-23T17:30:00"
  },
  {
    "temperature": 21.7,
    "humidity": 44.8,
    "measured_at": "2026-11-23T16:30:00"
  },
  {
    "temperature": 22.1,
    "humidity": 43.5,
    "measured_at": "2026-11-23T15:30:00"
  },
  {
    "temperature": 22.4,
    "humidity": 42.9,
    "measured_at": "2026-11-23T14:30:00"
  },
  {
    "temperature": 22.0,
    "humidity": 44.1,
    "measured_at": "2026-11-23T13:30:00"
  },
  {
    "temperature": 21.8,
    "humidity": 45.0,
    "measured_at": "2026-11-23T12:30:00"
  },
  {
    "temperature": 21.3,
    "humidity": 46.2,
    "measured_at": "2026-11-23T11:30:00"
  },
  {
    "temperature": 20.9,
    "humidity": 47.5,
    "measured_at": "2026-11-23T10:30:00"
  },
  {
    "temperature": 20.5,
    "humidity": 48.1,
    "measured_at": "2026-11-23T09:30:00"
  },
  {
    "temperature": 20.2,
    "humidity": 49.3,
    "measured_at": "2026-11-23T08:30:00"
  },
  {
    "temperature": 19.8,
    "humidity": 50.2,
    "measured_at": "2026-11-23T07:30:00"
  },
  {
    "temperature": 19.5,
    "humidity": 51.0,
    "measured_at": "2026-11-23T06:30:00"
  },
  {
    "temperature": 19.2,
    "humidity": 52.4,
    "measured_at": "2026-11-23T05:30:00"
  },
  {
    "temperature": 19.0,
    "humidity": 53.1,
    "measured_at": "2026-11-23T04:30:00"
  },
  {
    "temperature": 18.8,
    "humidity": 54.0,
    "measured_at": "2026-11-23T03:30:00"
  },
  {
    "temperature": 18.5,
    "humidity": 55.2,
    "measured_at": "2026-11-23T02:30:00"
  },
  {
    "temperature": 18.7,
    "humidity": 54.8,
    "measured_at": "2026-11-23T01:30:00"
  },
  {
    "temperature": 19.1,
    "humidity": 53.5,
    "measured_at": "2026-11-23T00:30:00"
  },
  {
    "temperature": 19.4,
    "humidity": 52.1,
    "measured_at": "2026-11-22T23:30:00"
  },
  {
    "temperature": 19.8,
    "humidity": 51.3,
    "measured_at": "2026-11-22T22:30:00"
  }
]
const refresh_badge = document.getElementById("last_update");
const last_refresh = Number(refresh_badge.getAttribute("data-measured-at"));

function calculate_time_diff(){
    const time_now = Date.now();
    const diff = Math.floor((time_now - last_refresh)/ 60000);
    refresh_badge.textContent = `Od ostatniej aktualizacji: ${diff} min`;
}

calculate_time_diff();
setInterval(calculate_time_diff, 10000);
document.addEventListener('DOMContentLoaded', () => {
    getChartData(1);
});


const ctx = document.getElementById('myChart');
const myChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: dane_testowe.map(item => item.measured_at),
    datasets: [{
      data: dane_testowe.map(item => item.temperature),
      borderColor: "red",
      fill: false
    },]
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
            tooltipFormat
        },
        title: {
            display: true,
            text: 'Data'
        }
    },
    y: {
      title: {
        display: true,
        text: "temperatura"
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
            let temperature = data.map(item => item.temperature);
            let humidity = data.map(item => item.humidity);
            let dates = data.map(item=>item.measured_at);

            
        } else {
            throw new Error(`Błąd HTTP: ${response.status}`);
        }
    } catch (error) {
        alert('Wystąpił błąd podczas pobierania danych.')
    }
}


const range_buttons = document.querySelectorAll(".range");
range_buttons.forEach(button => {
    button.addEventListener('click', () => {
        const query_param = button.getAttribute("data-range")
        getChartData(query_param)
    });
});


