// -----------------------------
// Function to download PDF report
// -----------------------------
function generateReport(createdAt) {
    if (!createdAt) {
        alert("Record date missing!");
        return;
    }

    const link = document.createElement("a");
    link.href = `/generate-report?created_at=${encodeURIComponent(createdAt)}`;
    link.download = `report_${createdAt.replace(/[: ]/g, "-")}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#detection-form");
    const resultDiv = document.querySelector("#result");
    const resultContainer = document.querySelector("#result-container");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            // 1. Show a loading message
            resultContainer.style.display = "block";
            resultDiv.innerHTML = "<p style='color: #370d06;'>Analyzing Singlish text... please wait.</p>";

            const formData = new FormData(form);

            try {
                const response = await fetch("/detect", {
                    method: "POST",
                    body: formData,
                    credentials: "include"
                });

                if (!response.ok) throw new Error("Server error");

                const data = await response.json();
                let html = "";

                // Text Analysis Section
                if (data.text_probs) {
                    html += `<h3><i class="fa-solid fa-file-lines"></i> Text Analysis:</h3>`;
                    html += `<p><b>Input:</b> ${data.input_text || "N/A"}</p>`;
                    html += `<p>Fake Probability: <span style="color:red">${data.text_probs.fake.toFixed(2)}</span></p>`;
                    html += `<p>Real Probability: <span style="color:green">${data.text_probs.real.toFixed(2)}</span></p>`;
                    html += `<p><b>Confidence:</b> ${(data.text_confidence * 100).toFixed(1)}%</p>`;
                }

                // Image/OCR Analysis Section
                if (data.image_probs) {
                    html += `<hr><h3><i class="fa-solid fa-image"></i> Image Analysis:</h3>`;
                    html += `<p><b>OCR Text:</b> ${data.ocr_text || "None detected"}</p>`;
                    html += `<p>Fake: ${data.image_probs.fake.toFixed(2)}</p>`;
                    html += `<p>Real: ${data.image_probs.real.toFixed(2)}</p>`;
                    html += `<p><b>Confidence:</b> ${(data.image_confidence * 100).toFixed(1)}%</p>`;
                }

                // Final Decision Section
                if (data.final_decision) {
                    const color = data.final_decision.label === "Fake" ? "red" : "green";
                    html += `<div style="margin-top:20px; border-top: 2px solid #370d06; padding-top:10px;">`;
                    html += `<h3>Final Verdict: <span style="color:${color}">${data.final_decision.label}</span></h3>`;
                    html += `<p><b>Reason:</b> ${data.final_decision.reason}</p>`;
                    html += `<p><b>Final Confidence:</b> ${(data.final_decision.confidence * 100).toFixed(1)}%</p>`;
                    html += `</div>`;
                }

                resultDiv.innerHTML = html;

            } catch (err) {
                console.error(err);
                resultDiv.innerHTML = "<p style='color:red'>⚠️ Error detecting. Please check your connection or try again!</p>";
            }
        });
    }
});