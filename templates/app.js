const BASE_API_URL = "http://127.0.0.1:8000";

window.isActivelyDisplayingAnalysis = false;
window.cachedAnalysisPayload = null;

document.addEventListener("DOMContentLoaded", () => {
    
    const loginSubmitBtn = document.getElementById("loginSubmitBtn");
    if (loginSubmitBtn) {
        loginSubmitBtn.addEventListener("click", handleLogin);
    }

    const registerSubmitBtn = document.getElementById("registerSubmitBtn");
    if (registerSubmitBtn) {
        registerSubmitBtn.addEventListener("click", handleRegister);
    }

    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            e.stopPropagation();
            handleAnalyze(e);
            return false;
        });
    }

    const otherForms = document.querySelectorAll('form:not(#uploadForm)');
    otherForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    });

    fetchHistory();
});


async function handleLogin(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const usernameInput = document.getElementById('loginUsername');
    const passwordInput = document.getElementById('loginPassword');
    if (!usernameInput || !passwordInput) return;

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
        alert("Please specify a username and password.");
        return;
    }

    try {
        console.log("Sending login request to Django...");
        const response = await fetch(`${BASE_API_URL}/api/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            console.log("Login successful! Token acquired.");
            localStorage.setItem('access_token', data.access);
            window.location.href = './dashboard.html';
        } else {
            alert(data.detail || data.error || "Authentication failed. Invalid credentials.");
        }
    } catch (err) {
        console.error("Transmission interface break:", err);
        alert("Network communication failure. Make sure your Django server is running.");
    }
}

async function handleRegister(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const emailInput = document.getElementById('regEmail');
    const usernameInput = document.getElementById('regUsername');
    const passwordInput = document.getElementById('regPassword');

    if (!emailInput || !usernameInput || !passwordInput) return;

    const email = emailInput.value.trim();
    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!email || !username || !password) {
        alert("Please complete all registration parameters.");
        return;
    }

    try {
        const response = await fetch(`${BASE_API_URL}/api/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, username, password })
        });

        if (response.ok) {
            alert("Account created successfully! Switching to login form.");
            if (typeof toggleAuthMode === "function") {
                toggleAuthMode('login');
            } else {
                window.location.reload();
            }
        } else {
            const errorData = await response.json();
            alert("Registration refused: " + (errorData.error || JSON.stringify(errorData)));
        }
    } catch (err) {
        console.error("Registration exception trace:", err);
    }
}


async function fetchHistory() {
    const token = localStorage.getItem('access_token');
    const tbody = document.getElementById('historyTableBody');
    if (!tbody || !token) return;
    
    try {
        const response = await fetch(`${BASE_API_URL}/api/history/`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            return;
        }

        const data = await response.json();
        
        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="p-4 text-center text-gray-400">No matching scan records compiled yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(item => {
            const displayScore = item.match_score !== undefined ? item.match_score : 0;
            return `
                <tr class="border-b hover:bg-gray-50 text-gray-700 transition">
                    <td class="p-3 font-medium text-gray-900">${item.filename || 'Resume.pdf'}</td>
                    <td class="p-3">${item.analyzed_at || 'Just Now'}</td>
                    <td class="p-3">
                        <span class="font-bold px-2 py-1 rounded text-sm ${displayScore >= 70 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}">
                            ${displayScore}%
                        </span>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error("Ledger database sync failure:", err);
    }
}

function renderDashboardDOM(data) {
    const resultDashboard = document.getElementById('resultDashboard');
    if (!resultDashboard) return;

    // Render Score
    const score = data.match_score !== undefined ? data.match_score : 0;
    const scoreBadge = document.getElementById('scoreBadge');
    if (scoreBadge) {
        scoreBadge.innerText = `${score}%`;
        scoreBadge.className = score >= 70 
            ? "text-4xl font-extrabold px-4 py-2 rounded-xl bg-green-100 text-green-700 inline-block"
            : "text-4xl font-extrabold px-4 py-2 rounded-xl bg-yellow-100 text-yellow-700 inline-block";
    }
    
    // Render Skills
    const skillsContainer = document.getElementById('skillsContainer');
    if (skillsContainer) {
        const safeSkills = data.skills || data.extracted_skills || [];
        skillsContainer.innerHTML = safeSkills.length > 0
            ? safeSkills.map(skill => `<span class="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-1 rounded-md border border-blue-200">${skill}</span>`).join('')
            : `<span class="text-sm text-gray-400 italic">No explicit skills parsed.</span>`;
    }

    // Render Strengths
    const strengthsList = document.getElementById('strengthsList');
    if (strengthsList) {
        let safeStrengths = [];
        if (data.feedback && Array.isArray(data.feedback.strengths)) {
            safeStrengths = data.feedback.strengths;
        } else if (Array.isArray(data.strengths)) {
            safeStrengths = data.strengths;
        }
        strengthsList.innerHTML = safeStrengths.length > 0
            ? safeStrengths.map(str => `<li>${str}</li>`).join('')
            : `<li>Core matching configurations processed successfully.</li>`;
    }
    
    // Render Gaps
    const gapsList = document.getElementById('gapsList');
    if (gapsList) {
        let safeGaps = [];
        if (data.feedback && Array.isArray(data.feedback.gaps)) {
            safeGaps = data.feedback.gaps;
        } else if (Array.isArray(data.gaps)) {
            safeGaps = data.gaps;
        }
        gapsList.innerHTML = safeGaps.length > 0
            ? safeGaps.map(gap => `<li>${gap}</li>`).join('')
            : `<li>No significant requirement gaps identified.</li>`;
    }

   
    resultDashboard.classList.remove('hidden');
    resultDashboard.classList.add('block');
}

async function handleAnalyze(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    console.log("🚀 Analysis engine running... Hard refresh blocked permanently.");

    const token = localStorage.getItem('access_token');
    if (!token) {
        alert("No token found in local storage!");
        return;
    }

    const fileInput = document.getElementById('resumeFile');
    const jobDescElem = document.getElementById('jobDesc');
    const jobDesc = jobDescElem ? jobDescElem.value.trim() : '';
    
    const submitBtn = document.getElementById('submitBtn');
    const loadingState = document.getElementById('loadingState');
    const resultDashboard = document.getElementById('resultDashboard');

    if (!fileInput || !fileInput.files[0]) {
        alert("Please choose a resume file first.");
        return;
    }
    if (!jobDesc) {
        alert("Please paste a target job description.");
        return;
    }

    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    formData.append('job_description', jobDesc);

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Processing...";
    }
    
    window.isActivelyDisplayingAnalysis = false;
    window.cachedAnalysisPayload = null;

    if (loadingState) loadingState.classList.remove('hidden');
    if (resultDashboard) {
        resultDashboard.classList.add('hidden');
        resultDashboard.classList.remove('block');
    }

    try {
        console.log("📡 Sending fetch request to Django backend...");
        const response = await fetch(`${BASE_API_URL}/api/analyze/`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        
        console.log("📡 Response received from server. Status code:", response.status);

        if (response.status === 401 || response.status === 403) {
            alert("Your login session has timed out. (LOGOUT REFRESH DISABLED FOR DEBUGGING)");
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = "Analyze Core Fit";
            }
            if (loadingState) loadingState.classList.add('hidden');
            return;
        }

        // Safe JSON extraction net
        let data;
        try {
            data = await response.json();
            console.log("📦 Parsed JSON payload data:", data);
        } catch (jsonErr) {
            console.error("🛑 Server didn't send valid JSON text:", jsonErr);
            alert("The server processed successfully but did not send clean data back.");
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = "Analyze Core Fit";
            }
            if (loadingState) loadingState.classList.add('hidden');
            return;
        }

        if (response.ok) {
            window.cachedAnalysisPayload = data;
            window.isActivelyDisplayingAnalysis = true;

            // Render out layout changes safely
            renderDashboardDOM(data);

            // Directly update local table elements
            const tbody = document.getElementById('historyTableBody');
            if (tbody) {
                if (tbody.innerHTML.includes("No matching scan records")) {
                    tbody.innerHTML = "";
                }
                const filename = data.filename || (fileInput.files[0] ? fileInput.files[0].name : 'Resume.pdf');
                const timestamp = data.analyzed_at || new Date().toISOString().replace('T', ' ').substring(0, 19);
                const score = data.match_score !== undefined ? data.match_score : 0;

                const newRowHtml = `
                    <tr class="border-b hover:bg-gray-50 text-gray-700 transition">
                        <td class="p-3 font-medium text-gray-900">${filename}</td>
                        <td class="p-3">${timestamp}</td>
                        <td class="p-3">
                            <span class="font-bold px-2 py-1 rounded text-sm ${score >= 70 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}">
                                ${score}%
                            </span>
                        </td>
                    </tr>
                `;
                tbody.insertAdjacentHTML('afterbegin', newRowHtml);
            }
            console.log("🎯 DOM elements drawn completely. Screen state locked.");

        } else {
            alert("Analysis Processing Error: " + (data.error || "The server failed to parse documents."));
        }
    } catch (err) {
        console.error("❌ Network Transmission Exception:", err);
        alert("A system network transmission exception occurred.");
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerText = "Analyze Core Fit";
        }
        if (loadingState) loadingState.classList.add('hidden');
    }
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

window.handleAnalyze = handleAnalyze;
window.fetchHistory = fetchHistory;
window.logout = logout;

