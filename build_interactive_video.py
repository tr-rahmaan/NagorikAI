import os
import base64

assets_dir = '/Users/tamimarahmanchoity/Desktop/CivicSphere-AI/prototype_video_assets'
files = [
    'scene1_title.mp3',
    'scene2_problem.mp3',
    'scene3_solution.mp3',
    'scene4_dalal.mp3',
    'scene5_vision.mp3',
    'scene6_impact.mp3'
]

audio_data = {}
for f in files:
    p = os.path.join(assets_dir, f)
    with open(p, 'rb') as audio_f:
        audio_data[f.replace('.mp3', '')] = "data:audio/mp3;base64," + base64.b64encode(audio_f.read()).decode('utf-8')

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CivicSphere AI — Interactive Prototype Video Presentation</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Hind+Siliguri:wght@500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-dark: #090d16;
    --card-bg: rgba(22, 30, 46, 0.75);
    --primary: #10b981;
    --primary-glow: rgba(16, 185, 129, 0.35);
    --accent: #064e3b;
    --danger: #ef4444;
    --danger-bg: rgba(239, 68, 68, 0.15);
    --warning: #f59e0b;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: rgba(255, 255, 255, 0.1);
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: var(--bg-dark);
    color: var(--text-main);
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 20px;
    overflow-x: hidden;
  }}

  /* Video Canvas Frame (16:9 ratio) */
  .video-container {{
    position: relative;
    width: 100%;
    max-width: 1100px;
    aspect-ratio: 16 / 9;
    background: radial-gradient(circle at 50% 30%, #152238 0%, #080d1a 100%);
    border-radius: 20px;
    border: 1px solid var(--border);
    box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 40px -10px var(--primary-glow);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}

  /* Stage / Scene Container */
  .stage {{
    position: relative;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
    overflow: hidden;
  }}

  .scene {{
    position: absolute;
    inset: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transform: scale(0.95) translateY(20px);
    transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    pointer-events: none;
  }}

  .scene.active {{
    opacity: 1;
    transform: scale(1) translateY(0);
    pointer-events: auto;
  }}

  /* Badges & Pills */
  .pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid var(--primary);
    border-radius: 9999px;
    color: var(--primary);
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
    animation: pulse 2.5s infinite;
  }}

  .pill.danger {{
    background: var(--danger-bg);
    border-color: var(--danger);
    color: var(--danger);
  }}

  /* Typography */
  h1 {{
    font-size: 2.8rem;
    font-weight: 800;
    text-align: center;
    line-height: 1.15;
    background: linear-gradient(135deg, #ffffff 30%, #6ee7b7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 14px;
  }}

  h2 {{
    font-size: 2.2rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 12px;
  }}

  p.subtitle {{
    font-size: 1.2rem;
    color: var(--text-muted);
    text-align: center;
    max-width: 800px;
    line-height: 1.6;
    margin-bottom: 24px;
  }}

  /* UI Cards & Mockups */
  .grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    width: 100%;
    margin-top: 15px;
  }}

  .glass-card {{
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    transition: transform 0.3s ease, border-color 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}

  .glass-card:hover {{
    transform: translateY(-4px);
    border-color: var(--primary);
  }}

  .glass-card.danger-card {{
    border-color: rgba(239, 68, 68, 0.4);
    background: rgba(30, 20, 25, 0.85);
  }}

  .card-icon {{
    font-size: 2.5rem;
    margin-bottom: 12px;
  }}

  .card-title {{
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: #ffffff;
  }}

  .card-desc {{
    font-size: 0.9rem;
    color: var(--text-muted);
    line-height: 1.45;
  }}

  /* Live UI Mockup Streamlit Box */
  .chat-mockup {{
    width: 100%;
    max-width: 850px;
    background: #0f172a;
    border-radius: 16px;
    border: 1px solid #334155;
    padding: 20px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  .chat-msg {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.5;
  }}

  .user-msg {{
    background: #1e293b;
    align-self: flex-end;
    color: #e2e8f0;
    border-bottom-right-radius: 4px;
  }}

  .bot-alert {{
    background: rgba(239, 68, 68, 0.15);
    border-left: 5px solid var(--danger);
    color: #fca5a5;
    border-radius: 8px;
    padding: 14px 18px;
    width: 100%;
  }}

  .savings-badge {{
    display: inline-block;
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid var(--primary);
    color: #6ee7b7;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 8px;
    margin-top: 8px;
    font-size: 0.9rem;
  }}

  /* Vision inspector UI */
  .vision-box {{
    display: flex;
    gap: 25px;
    width: 100%;
    max-width: 850px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    align-items: center;
  }}

  .doc-preview {{
    width: 180px;
    height: 120px;
    background: #1e293b;
    border: 2px dashed #475569;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #94a3b8;
    font-size: 0.85rem;
  }}

  .doc-audits {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .audit-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.9rem;
  }}

  .audit-item.check {{ color: #6ee7b7; }}
  .audit-item.warn {{ color: #fcd34d; }}

  /* Video Bottom Controls & Timeline Bar */
  .controls-bar {{
    background: rgba(10, 15, 26, 0.85);
    backdrop-filter: blur(10px);
    border-top: 1px solid var(--border);
    padding: 16px 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    z-index: 50;
  }}

  .play-btn {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--primary);
    border: none;
    color: #064e3b;
    font-size: 1.2rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.2s, background 0.2s;
  }}

  .play-btn:hover {{
    transform: scale(1.08);
    background: #34d399;
  }}

  .progress-wrap {{
    flex: 1;
    height: 6px;
    background: #334155;
    border-radius: 9999px;
    position: relative;
    cursor: pointer;
  }}

  .progress-fill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, #10b981, #3b82f6);
    border-radius: 9999px;
    transition: width 0.1s linear;
  }}

  .time-display {{
    font-size: 0.85rem;
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }}

  .scene-nav {{
    display: flex;
    gap: 8px;
  }}

  .nav-dot {{
    padding: 6px 12px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }}

  .nav-dot.active {{
    background: var(--primary);
    color: #064e3b;
    border-color: var(--primary);
  }}

  .record-helper {{
    margin-top: 20px;
    font-size: 0.95rem;
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    padding: 12px 20px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 15px;
  }}

  .key-shortcut {{
    background: #334155;
    color: #f8fafc;
    padding: 3px 8px;
    border-radius: 6px;
    font-family: monospace;
    font-weight: 700;
  }}

  @keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }}
    70% {{ box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
  }}
</style>
</head>
<body>

<!-- 16:9 Video Player Presentation Frame -->
<div class="video-container" id="videoFrame">
  <div class="stage">

    <!-- SCENE 1: Title & Overview -->
    <div class="scene active" id="scene-0">
      <div class="pill">🇧🇩 International AI Builders Congress 2026</div>
      <h1>CivicSphere AI</h1>
      <p class="subtitle" style="color: #6ee7b7; font-weight: 600; font-size: 1.35rem;">GovCopilot & Dalal-Free Citizen Assistant</p>
      <div class="grid-3" style="max-width: 850px;">
        <div class="glass-card">
          <div class="card-icon">🪪</div>
          <div class="card-title">NID Corrections</div>
          <div class="card-desc">Category A, B, C classifications with official fees & affidavits</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">🛂</div>
          <div class="card-title">e-Passport Issuance</div>
          <div class="card-desc">Accurate 5 & 10 yr fee matrices (৳৪,০২৫) with police verification rules</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">🌾</div>
          <div class="card-title">Land Mutation</div>
          <div class="card-desc">Statutory cap of ৳১,১৭০ strictly enforced, preventing extortion</div>
        </div>
      </div>
    </div>

    <!-- SCENE 2: Problem Statement -->
    <div class="scene" id="scene-1">
      <div class="pill danger">🚨 The Systemic Crisis in Bangladesh</div>
      <h2 style="color: #fca5a5;">The Middleman (Dalal) Exploitation Trap</h2>
      <p class="subtitle">Confusing paperwork and fear of rejection subject 170M citizens to an illegal corruption tax.</p>
      <div class="grid-3" style="max-width: 900px;">
        <div class="glass-card danger-card">
          <div class="card-icon">💸</div>
          <div class="card-title" style="color: #ef4444;">৳৫,০০০ – ৳৩০,০০০</div>
          <div class="card-desc">Exorbitant fees charged by brokers outside AC Land and Passport offices for free or nominal services.</div>
        </div>
        <div class="glass-card danger-card">
          <div class="card-icon">❌</div>
          <div class="card-title" style="color: #f87171;">Frequent Rejections</div>
          <div class="card-desc">Single missing attestation or blurry seal wastes months of citizen travel and lost wages.</div>
        </div>
        <div class="glass-card danger-card">
          <div class="card-icon">🗣️</div>
          <div class="card-title" style="color: #fca5a5;">Literacy Barriers</div>
          <div class="card-desc">Complex gazettes and unassisted online portals exclude non-technical, rural citizens.</div>
        </div>
      </div>
    </div>

    <!-- SCENE 3: Solution & Grounded RAG Architecture -->
    <div class="scene" id="scene-2">
      <div class="pill">⚙️ System Architecture & Grounding</div>
      <h2>AI Grounded Strictly in Government Truth</h2>
      <p class="subtitle">Zero hallucination guarantee using high-speed hybrid vector retrieval.</p>
      <div class="grid-3" style="max-width: 900px;">
        <div class="glass-card">
          <div class="card-icon">📚</div>
          <div class="card-title">Verified Circulars</div>
          <div class="card-desc">Direct ingestion of NID Wing, Passport Dept, and Land Ministry gazettes.</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">⚡</div>
          <div class="card-title">Hybrid BM25 + Vector</div>
          <div class="card-desc">Bengali morphological stemming with sub-second retrieval latency (&lt;800ms).</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">🛡️</div>
          <div class="card-title">Zero Hallucinations</div>
          <div class="card-desc">Strict refusal patterns for out-of-scope queries; official hotline citations only.</div>
        </div>
      </div>
    </div>

    <!-- SCENE 4: Live UI Walkthrough — Dalal-Free Guardrail -->
    <div class="scene" id="scene-3">
      <div class="pill danger">🛡️ Live Streamlit Feature Demo</div>
      <h2>Proactive Dalal-Free Anti-Corruption Guardrail</h2>
      <div class="chat-mockup">
        <div class="chat-msg user-msg">
          <span>🗣️ <strong>নাগরিক:</strong> "পাসপোর্টের জন্য দালাল ৮,০০০ টাকা চাচ্ছে, এটা কি ঠিক?"</span>
        </div>
        <div class="bot-alert">
          <strong style="font-size: 1.05rem; display: flex; align-items: center; gap: 8px;">
            ⚠️ দালাল প্রতিরোধ ও দুর্নীতি সতর্কতা (Dalal Alert)
          </strong>
          <p style="margin-top: 6px; font-size: 0.9rem; line-height: 1.4;">
            দালাল বা কাউকে সরকারি ফির বেশি টাকা দেওয়া সম্পূর্ণ বেআইনি! সাধারণ ৪৮ পাতা ১০ বছর মেয়াদি পাসপোর্টের সরকারি ফি মাত্র <strong>৳৪,০২৫</strong> (ভ্যাটসহ)।
          </p>
          <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
            <div class="savings-badge">💰 আপনি বাঁচাচ্ছেন: ৳৩,৯৭৫ টাকা</div>
            <span style="font-size: 0.85rem; color: #fca5a5;">📞 দুদকের হেল্পলাইন: <strong>১০৬</strong></span>
          </div>
        </div>
      </div>
    </div>

    <!-- SCENE 5: Document Vision Pre-Flight Inspector -->
    <div class="scene" id="scene-4">
      <div class="pill">👁️ Multimodal AI Vision Audit</div>
      <h2>Pre-Flight Document Inspector</h2>
      <p class="subtitle">Catches application flaws before citizens commute to government counters.</p>
      <div class="vision-box">
        <div class="doc-preview">
          <span style="font-size: 2rem;">📄</span>
          <span>NID / Slip Photo</span>
        </div>
        <div class="doc-audits">
          <div class="audit-item check">
            <span>✅</span> <strong>Document Clarity:</strong> High resolution, text fully legible and well-lit
          </div>
          <div class="audit-item check">
            <span>✅</span> <strong>Name Consistency:</strong> Bengali spelling matches digital record
          </div>
          <div class="audit-item warn">
            <span>⚠️</span> <strong>Attestation Check:</strong> First-class gazetted officer seal required for Category C
          </div>
          <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 5px;">
            🔒 <em>100% Ephemeral Processing: Zero PII or photos are persisted on disk or database.</em>
          </div>
        </div>
      </div>
    </div>

    <!-- SCENE 6: Impact & Conclusion -->
    <div class="scene" id="scene-5">
      <div class="pill">🌟 National Impact & Readiness</div>
      <h1>Empowering 170 Million Citizens</h1>
      <p class="subtitle">A transparent, accessible, and Dalal-Free digital Bangladesh.</p>
      <div class="grid-3" style="max-width: 900px;">
        <div class="glass-card">
          <div class="card-icon">🎙️</div>
          <div class="card-title">Bengali Voice In/Out</div>
          <div class="card-desc">Web Speech API (bn-BD) and gTTS audio playback for low-literacy citizens.</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">📞</div>
          <div class="card-title">1-Click Hotlines</div>
          <div class="card-desc">Direct links to 106 (ACC), 105 (NID), 16445 (Passport), and 16122 (Land).</div>
        </div>
        <div class="glass-card">
          <div class="card-icon">🚀</div>
          <div class="card-title">Ready for Congress</div>
          <div class="card-desc">Complete working MVP with automated test suite, UI, and live fallbacks.</div>
        </div>
      </div>
    </div>

  </div>

  <!-- Bottom Player Bar -->
  <div class="controls-bar">
    <button class="play-btn" id="playBtn" onclick="togglePlay()">▶</button>
    <div class="progress-wrap" id="progressWrap" onclick="seekVideo(event)">
      <div class="progress-fill" id="progressBar"></div>
    </div>
    <div class="time-display" id="timeDisplay">0:00 / 1:20</div>
    <div class="scene-nav">
      <button class="nav-dot active" onclick="goToScene(0)">1. Title</button>
      <button class="nav-dot" onclick="goToScene(1)">2. Crisis</button>
      <button class="nav-dot" onclick="goToScene(2)">3. RAG</button>
      <button class="nav-dot" onclick="goToScene(3)">4. Guardrail</button>
      <button class="nav-dot" onclick="goToScene(4)">5. Vision</button>
      <button class="nav-dot" onclick="goToScene(5)">6. Impact</button>
    </div>
  </div>
</div>

<div class="record-helper">
  <span>💡 <strong>To export as MP4 / YouTube Demo:</strong> Press <span class="key-shortcut">Cmd + Shift + 5</span> on your Mac, select the video frame above, click <strong>Play ▶</strong>, and record the exact audio-synced prototype video!</span>
</div>

<script>
  // Base64 Embedded Voiceover Narration Tracks
  const audioTracks = {{
    0: new Audio("{audio_data['scene1_title']}"),
    1: new Audio("{audio_data['scene2_problem']}"),
    2: new Audio("{audio_data['scene3_solution']}"),
    3: new Audio("{audio_data['scene4_dalal']}"),
    4: new Audio("{audio_data['scene5_vision']}"),
    5: new Audio("{audio_data['scene6_impact']}")
  }};

  // Scene durations in seconds (matched to audio lengths)
  const sceneDurations = [10, 15, 12, 14, 13, 16];
  const totalDuration = sceneDurations.reduce((a, b) => a + b, 0);

  let currentScene = 0;
  let isPlaying = false;
  let sceneTimer = null;
  let animFrame = null;
  let startTime = 0;
  let elapsedBeforePause = 0;

  function updateDisplayTime(seconds) {{
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60).toString().padStart(2, '0');
    const totMins = Math.floor(totalDuration / 60);
    const totSecs = Math.floor(totalDuration % 60).toString().padStart(2, '0');
    document.getElementById('timeDisplay').innerText = `${{mins}}:${{secs}} / ${{totMins}}:${{totSecs}}`;
  }}

  function goToScene(index) {{
    // Stop all audio
    Object.values(audioTracks).forEach(a => {{
      a.pause();
      a.currentTime = 0;
    }});

    // Update scene visibility
    document.querySelectorAll('.scene').forEach((s, idx) => {{
      s.classList.toggle('active', idx === index);
    }});
    document.querySelectorAll('.nav-dot').forEach((d, idx) => {{
      d.classList.toggle('active', idx === index);
    }});

    currentScene = index;
    if (isPlaying) {{
      playCurrentScene();
    }}
  }}

  function playCurrentScene() {{
    const currentAudio = audioTracks[currentScene];
    if (currentAudio) {{
      currentAudio.currentTime = 0;
      currentAudio.play().catch(e => console.log('Audio autoplay prevented:', e));
    }}

    clearTimeout(sceneTimer);
    sceneTimer = setTimeout(() => {{
      if (currentScene < 5) {{
        goToScene(currentScene + 1);
      }} else {{
        pauseVideo();
        goToScene(0);
      }}
    }}, sceneDurations[currentScene] * 1000);
  }}

  function togglePlay() {{
    if (isPlaying) {{
      pauseVideo();
    }} else {{
      playVideo();
    }}
  }}

  function playVideo() {{
    isPlaying = true;
    document.getElementById('playBtn').innerText = '❚❚';
    playCurrentScene();
    startTime = performance.now() - (elapsedBeforePause * 1000);
    tick();
  }}

  function pauseVideo() {{
    isPlaying = false;
    document.getElementById('playBtn').innerText = '▶';
    clearTimeout(sceneTimer);
    cancelAnimationFrame(animFrame);
    if (audioTracks[currentScene]) {{
      audioTracks[currentScene].pause();
    }}
  }}

  function tick() {{
    if (!isPlaying) return;
    const now = performance.now();
    const elapsed = Math.min(totalDuration, (now - startTime) / 1000);
    elapsedBeforePause = elapsed;
    const percent = (elapsed / totalDuration) * 100;
    document.getElementById('progressBar').style.width = percent + '%';
    updateDisplayTime(elapsed);

    if (elapsed < totalDuration) {{
      animFrame = requestAnimationFrame(tick);
    }}
  }}

  function seekVideo(e) {{
    const rect = document.getElementById('progressWrap').getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const targetTime = ratio * totalDuration;

    let accum = 0;
    for (let i = 0; i < sceneDurations.length; i++) {{
      if (targetTime <= accum + sceneDurations[i] || i === sceneDurations.length - 1) {{
        goToScene(i);
        elapsedBeforePause = targetTime;
        startTime = performance.now() - (targetTime * 1000);
        document.getElementById('progressBar').style.width = (ratio * 100) + '%';
        updateDisplayTime(targetTime);
        break;
      }}
      accum += sceneDurations[i];
    }}
  }}

  updateDisplayTime(0);
</script>

</body>
</html>
"""

dest_path = '/Users/tamimarahmanchoity/Desktop/CivicSphere-AI/prototype_video_player.html'

with open(dest_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Interactive Video HTML built and saved to:', dest_path)
