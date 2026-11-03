
const csvFile = document.getElementById("csvFile");
const fileName = document.getElementById("fileName");
const message = document.getElementById("message");

csvFile.addEventListener("change", async function () {
    const file = csvFile.files[0];

    if (!file) return;

    fileName.textContent = `Selected: ${file.name}`;
    message.textContent = "Analyzing your expenses...";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            body: formData
        });

        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(
                errorData.detail || "The API could not analyze this file."
            );
        }


        const data = await response.json();

        // Update the summary cards
        document.getElementById("totalSpent").textContent =
            formatRupees(data.total_spent);

        document.getElementById("transactionCount").textContent =
            data.transaction_count;

        document.getElementById("averagePerDay").textContent =
            formatRupees(data.avg_per_day);

        document.getElementById("daysTracked").textContent =
            `Days tracked: ${data.days_tracked}`;

        document.getElementById("spendingSummary").textContent =
            data.total_spending_summary;

        document.getElementById("highestDayAmount").textContent =
            formatRupees(data.highest_spending_amount);

        document.getElementById("highestDay").textContent =
            data.highest_spending_day;

        document.getElementById("insightText").textContent =
            data.insight;

        // Draw charts using the API response
        drawCategoryChart(data.category_spending);
        drawDailyChart(data.daily_spending);

        message.textContent = "Analysis complete!";
    } catch (error) {
        message.textContent =
            `${error.message} Check that your FastAPI server is running.`;
    }
});

function formatRupees(amount) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(amount);
}

let categoryChartInstance = null;
let dailyChartInstance = null;

function drawCategoryChart(categorySpending) {
    const categories = Object.keys(categorySpending);
    const amounts = Object.values(categorySpending);

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    categoryChartInstance = new Chart(
        document.getElementById("categoryChart"),
        {
            type: "doughnut",
            data: {
                labels: categories,
                datasets: [{
                    data: amounts,
                    backgroundColor: [
                        "#43d9a3",
                        "#6c8cff",
                        "#ffbd69",
                        "#bd93f9",
                        "#ff7b91"
                    ],
                    borderColor: "#111b2e",
                    borderWidth: 4,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                }
            }
        }
    );

    const legend = document.getElementById("categoryLegend");
    legend.replaceChildren();

    categories.forEach((category, index) => {
        const amount = amounts[index];
        const percentage = (
            amount / amounts.reduce((sum, value) => sum + value, 0) * 100
        ).toFixed(2);

        const item = document.createElement("div");
        item.className = "legend-item";

        const label = document.createElement("span");
        label.className = "legend-label";

        const dot = document.createElement("span");
        dot.className = "legend-dot";
        dot.style.backgroundColor =
            categoryChartInstance.data.datasets[0].backgroundColor[
                index % 5
            ];

        const name = document.createElement("span");
        name.textContent = category;

        label.append(dot, name);

        const value = document.createElement("span");
        value.className = "legend-value";
        value.textContent =
            `${formatRupees(amount)} · ${percentage}%`;

        item.append(label, value);
        legend.appendChild(item);
    });
}

function drawDailyChart(dailySpending) {
    const dates = Object.keys(dailySpending);
    const amounts = Object.values(dailySpending);

    if (dailyChartInstance) {
        dailyChartInstance.destroy();
    }

    dailyChartInstance = new Chart(
        document.getElementById("dailyChart"),
        {
            type: "line",
            data: {
                labels: dates,
                datasets: [{
                    label: "Daily spending",
                    data: amounts,
                    borderColor: "#43d9a3",
                    backgroundColor: "rgba(67, 217, 163, 0.12)",
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 4,
                    pointBackgroundColor: "#43d9a3",
                    pointBorderColor: "#111b2e",
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: "#91a0b7" },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: "#91a0b7",
                            callback: value => "₹" + value
                        },
                        grid: { color: "#25334a" }
                    }
                }
            }
        }
    );
}