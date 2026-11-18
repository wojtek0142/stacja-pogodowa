const refresh_badge = document.getElementById("last_update");
const last_refresh = Number(refresh_badge.getAttribute("data-measured-at"));

function calculate_time_diff(){
    const time_now = Date.now();
    const diff = Math.floor((time_now - last_refresh)/ 60000);
    refresh_badge.textContent = `Od ostatniej aktualizacji: ${diff} min`;
}
calculate_time_diff();
setInterval(calculate_time_diff, 10000);

const range_buttons = document.querySelectorAll("range");
range_buttons.forEach(button => {
    button.addEventListener('click', async () => {
        const query_param = button.getAttribute("data-range") 
        try {
            const response = await fetch(`/api/readings/?days=${query_param}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            }
            });
            if (response.ok) {
                const data = await response.json();
                data.forEach(obiekt => {
                    console.log(obiekt);
                });

            } else {
                throw new Error(`Błąd HTTP: ${response.status}`);
            }
        } catch (error) {
            alert('Wystąpił błąd podczas pobierania danych.')
        }
    });
});

const xValues = [100,200,300,400,500,600,700,800,900,1000];

const myChart = new Chart("myChart", {
  type: "line",
  data: {
    labels: xValues,
    datasets: [{
      data: [860,1140,1060,1060,1070,1110,1330,2210,7830,2478],
      borderColor: "red",
      fill: false
    },{
      data: [1600,1700,1700,1900,2000,2700,4000,5000,6000,7000],
      borderColor: "green",
      fill: false
    },]
  },
  options: {
    plugins: {
      legend: {display: false}
    }
  }
});