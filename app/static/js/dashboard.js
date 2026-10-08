/**
 * EduPulse AI - Client-Side Interactive Engine
 * Aligned with Module 6: Event-Driven Programming & Asynchronous REST API
 */

document.addEventListener("DOMContentLoaded", () => {
    // 2. Initialize Interactive Predictor if on predictor page
    if (document.getElementById("predictorForm")) {
        initInteractivePredictor();
    }

    // 3. Initialize Dashboard Charts if canvas elements exist
    initDashboardCharts();
});

/* --- Interactive Live Predictor Engine --- */
let radarChartInstance = null;
let debounceTimer = null;

function initInteractivePredictor() {
    const sliders = [
        "attendance",
        "study_hours_weekly",
        "midterm_score",
        "assignment_score",
        "lab_score"
    ];

    // Bind slider input events
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        const bubble = document.getElementById(`${id}_val`);
        if (slider && bubble) {
            slider.addEventListener("input", (e) => {
                bubble.textContent = e.target.value;
                triggerPredictionDebounced();
            });
        }
    });

    // Initial run
    runLivePrediction();
}

function triggerPredictionDebounced() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        runLivePrediction();
    }, 180);
}

async function runLivePrediction() {
    const payload = {
        attendance: parseFloat(document.getElementById("attendance")?.value || 75),
        study_hours_weekly: parseFloat(document.getElementById("study_hours_weekly")?.value || 15),
        midterm_score: parseFloat(document.getElementById("midterm_score")?.value || 65),
        assignment_score: parseFloat(document.getElementById("assignment_score")?.value || 70),
        lab_score: parseFloat(document.getElementById("lab_score")?.value || 75)
    };

    try {
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.status === "success") {
            updatePredictorUI(data.prediction);
        }
    } catch (err) {
        console.error("Live inference error:", err);
    }
}

function updatePredictorUI(pred, rec) {
    // 1. Grade Badge
    const gradeBadge = document.getElementById("resGrade");
    if (gradeBadge) gradeBadge.textContent = pred.predicted_grade;

    // 2. GPA & Confidence
    const gpaVal = document.getElementById("resGPA");
    if (gpaVal) gpaVal.textContent = pred.predicted_gpa.toFixed(2);

    const confVal = document.getElementById("resConf");
    const confBar = document.getElementById("resConfBar");
    if (confVal) confVal.textContent = `${pred.confidence_pct}%`;
    if (confBar) confBar.style.width = `${pred.confidence_pct}%`;

    // 3. Risk Level Pill
    const riskPill = document.getElementById("resRisk");
    if (riskPill) {
        riskPill.textContent = pred.risk_level;
        riskPill.className = "badge " + (
            pred.risk_level === "Low Risk" ? "badge-low-risk" :
            pred.risk_level === "Moderate Risk" ? "badge-moderate-risk" : "badge-high-risk"
        );
    }

    // 4. Update Radar Chart
    updateRadarChart(pred.radar_scores);
}

function updateRadarChart(scores) {
    const ctx = document.getElementById("radarChart");
    if (!ctx || typeof Chart === "undefined") return;

    const labels = Object.keys(scores);
    const values = Object.values(scores);

    if (radarChartInstance) {
        radarChartInstance.data.datasets[0].data = values;
        radarChartInstance.update();
        return;
    }

    radarChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "Student Capability Profile",
                data: values,
                backgroundColor: "rgba(99, 102, 241, 0.25)",
                borderColor: "#6366f1",
                pointBackgroundColor: "#06b6d4",
                pointBorderColor: "#fff",
                pointHoverBackgroundColor: "#fff",
                pointHoverBorderColor: "#06b6d4",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: "rgba(255, 255, 255, 0.1)" },
                    grid: { color: "rgba(255, 255, 255, 0.1)" },
                    pointLabels: { color: "#9ca3af", font: { size: 11, family: "Inter" } },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

/* --- Dashboard Cohort Charts --- */
function initDashboardCharts() {
    if (typeof Chart === "undefined") return;

    // Grade Distribution Doughnut Chart
    const gradeCanvas = document.getElementById("gradeChart");
    if (gradeCanvas) {
        const labels = JSON.parse(gradeCanvas.dataset.labels || "[]");
        const counts = JSON.parse(gradeCanvas.dataset.counts || "[]");

        new Chart(gradeCanvas, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        "#10b981", "#3b82f6", "#6366f1", "#8b5cf6", "#f59e0b", "#f97316", "#ef4444"
                    ],
                    borderWidth: 2,
                    borderColor: "#111827"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { color: "#9ca3af", boxWidth: 12 } }
                },
                cutout: "68%"
            }
        });
    }

    // Risk Level Bar Chart
    const riskCanvas = document.getElementById("riskChart");
    if (riskCanvas) {
        const labels = JSON.parse(riskCanvas.dataset.labels || "[]");
        const counts = JSON.parse(riskCanvas.dataset.counts || "[]");

        new Chart(riskCanvas, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Students",
                    data: counts,
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { display: false }, ticks: { color: "#9ca3af" } },
                    y: { grid: { color: "rgba(255, 255, 255, 0.06)" }, ticks: { color: "#9ca3af" }, beginAtZero: true }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
