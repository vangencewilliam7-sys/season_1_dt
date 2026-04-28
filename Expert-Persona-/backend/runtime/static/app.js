/**
 * Shadow Mode | Dashboard Logic
 * Handles real-time loading of pending extractions and expert review flow.
 */

const API_BASE = '/shadow';
let currentJobId = null;
let currentManifest = null;

// DOM Elements
const jobList = document.getElementById('job-list');
const emptyState = document.getElementById('empty-state');
const reviewContent = document.getElementById('review-content');
const rejectModalEl = document.getElementById('reject-modal');

/**
 * Initialization
 */
async function init() {
    await fetchPendingJobs();
    
    // Refresh queue every 15 seconds
    setInterval(fetchPendingJobs, 15000);
}

/**
 * Discovery Queue Management
 */
async function fetchPendingJobs() {
    try {
        const response = await fetch(`${API_BASE}/pending`);
        const jobs = await response.json();
        
        renderJobList(jobs);
    } catch (err) {
        console.error('Failed to fetch jobs:', err);
    }
}

function renderJobList(jobs) {
    if (jobs.length === 0) {
        jobList.innerHTML = `
            <div class="p-8 text-center text-slate-600 italic text-sm">
                Queue is empty
            </div>
        `;
        return;
    }

    jobList.innerHTML = jobs.map(job => `
        <div onclick="selectJob('${job.job_id}')" 
             class="job-card p-4 rounded-xl border border-slate-800 bg-slate-900/40 cursor-pointer hover:border-sky-500/30 group ${currentJobId === job.job_id ? 'active' : ''}">
            <div class="flex justify-between items-start mb-2">
                <span class="badge badge-pending">Pending Review</span>
                <span class="text-[10px] font-mono text-slate-500">${job.job_id.slice(0,8)}</span>
            </div>
            <h4 class="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">Expert: ${job.expert_id.split('_').pop().toUpperCase()}</h4>
            <p class="text-[10px] text-slate-500 mt-1">${job.compilation_issues.length} Quality Warnings</p>
        </div>
    `).join('');
}

/**
 * Selection & Rendering
 */
async function selectJob(jobId) {
    currentJobId = jobId;
    
    // Highlight active card
    document.querySelectorAll('.job-card').forEach(c => c.classList.remove('active'));
    renderJobList([]); // Re-render to show active state (simplified)
    await fetchPendingJobs(); // Real refresh

    try {
        const response = await fetch(`${API_BASE}/${jobId}/review`);
        const data = await response.json();
        
        currentManifest = data.manifest;
        renderReviewItem(data);
    } catch (err) {
        console.error('Failed to load review package:', err);
    }
}

function renderReviewItem(data) {
    const { manifest, compilation_issues } = data;
    
    emptyState.classList.add('hidden');
    reviewContent.classList.remove('hidden');

    // Header & Meta
    document.getElementById('active-expert-name').innerText = manifest.identity.name;
    document.getElementById('active-expert-role').innerText = manifest.identity.role;
    document.getElementById('doc-count').innerText = manifest.source_documents.length;
    document.getElementById('job-id-display').innerText = currentJobId;

    // Heuristics
    const container = document.getElementById('heuristics-container');
    container.innerHTML = manifest.heuristics.map((h, i) => `
        <div class="heuristic-card p-6 border border-slate-800 rounded-2xl group relative">
            <span class="absolute -left-3 top-6 w-6 h-6 bg-slate-900 border border-slate-800 rounded-md flex items-center justify-center text-[10px] font-bold text-slate-500">
                ${i+1}
            </span>
            <div class="space-y-4">
                <div>
                    <label class="text-[9px] text-slate-500 uppercase font-black mb-1 block">Trigger Scenario</label>
                    <input type="text" value="${h.trigger}" onchange="updateHeuristic(${i}, 'trigger', this.value)"
                           class="w-full bg-transparent text-sm text-white font-semibold focus:outline-none">
                </div>
                <div>
                    <label class="text-[9px] text-slate-500 uppercase font-black mb-1 block">Expert Decision</label>
                    <input type="text" value="${h.decision}" onchange="updateHeuristic(${i}, 'decision', this.value)"
                           class="w-full bg-transparent text-sm text-slate-300 focus:outline-none">
                </div>
                <div>
                    <label class="text-[9px] text-slate-500 uppercase font-black mb-1 block">Internal Reasoning</label>
                    <textarea onchange="updateHeuristic(${i}, 'reasoning', this.value)" rows="2"
                              class="w-full bg-transparent text-xs text-slate-400 italic focus:outline-none resize-none">${h.reasoning}</textarea>
                </div>
            </div>
        </div>
    `).join('');

    // Communication Style
    const tags = document.getElementById('tone-tags');
    tags.innerHTML = manifest.communication_style.tone.map(t => `
        <span class="px-3 py-1 bg-slate-800 border border-slate-700 rounded-full text-xs text-slate-300">${t}</span>
    `).join('');
    
    document.getElementById('framing-input').value = manifest.communication_style.preferred_framing;

    // Drop Zones
    const dzContainer = document.getElementById('drop-zones');
    dzContainer.innerHTML = manifest.drop_zone_triggers.map(dz => `
        <div class="flex items-center gap-3 p-3 bg-slate-900/60 rounded-xl border border-slate-800">
            <i data-lucide="shield-off" class="w-3.5 h-3.5 text-red-500/50"></i>
            <span class="text-xs text-slate-300 font-medium">${dz}</span>
        </div>
    `).join('');
    
    lucide.createIcons();
}

/**
 * Action Handlers
 */
function updateHeuristic(index, field, value) {
    if (!currentManifest) return;
    currentManifest.heuristics[index][field] = value;
    console.log('Manifest Stage:', currentManifest);
}

async function approveManifest() {
    if (!currentJobId) return;
    
    const approveBtn = document.getElementById('approve-btn');
    const originalHtml = approveBtn.innerHTML;
    
    approveBtn.disabled = true;
    approveBtn.innerHTML = `<span class="spinner"></span>`;

    try {
        const response = await fetch(`${API_BASE}/${currentJobId}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                approved_by: "HUMAN_EXPERT_ADMIN",
                notes: "Approved via Shadow Dashboard",
                modified_manifest: currentManifest
            })
        });

        if (response.ok) {
            alert('Manifest published successfully!');
            window.location.reload();
        }
    } catch (err) {
        alert('Approval failed. Check console.');
        console.error(err);
    } finally {
        approveBtn.disabled = false;
        approveBtn.innerHTML = originalHtml;
    }
}

// Modal Handlers
const rejectModal = {
    show: () => rejectModalEl.classList.remove('hidden'),
    hide: () => rejectModalEl.classList.add('hidden')
};

async function submitRejection() {
    const notes = document.getElementById('rejection-notes').value;
    if (!notes) return alert('Please provide correction notes.');

    try {
        const response = await fetch(`${API_BASE}/${currentJobId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rejected_by: "HUMAN_EXPERT_ADMIN",
                corrections: [],
                notes: notes
            })
        });

        if (response.ok) {
            alert('Rejection logged. Re-extraction scheduled.');
            window.location.reload();
        }
    } catch (err) {
        console.error(err);
    }
}

init();
