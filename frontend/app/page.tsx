"use client";

import { useMemo, useState } from "react";
import {
  Activity, ArrowDownRight, ArrowRight, ArrowUpRight, BrainCircuit, CalendarDays,
  Check, ChevronDown, CircleHelp, Clock3, CloudSun, HeartPulse, Leaf, Menu,
  MessageCircle, Moon, Play, RefreshCw, ShieldCheck, Sparkles, Sprout, Target,
  Waves, Wind, X
} from "lucide-react";

type FormState = {
  mood: number; energy: number; stress: number; sleep_hours: number;
  free_minutes: number; meetings_today: number; hour: number;
  steps_so_far: number; hrv_ms: number | null; outdoor_ok: boolean;
};
type Recommendation = {
  activity_id: string; category: string; duration_min: number;
  reasons: string[]; support_message?: string | null; demo?: boolean;
};
const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
const initial: FormState = {
  mood: 3, energy: 3, stress: 3, sleep_hours: 7,
  free_minutes: 15, meetings_today: 3, hour: 14,
  steps_so_far: 3200, hrv_ms: null, outdoor_ok: true,
};
const activities: Record<string, { name: string; detail: string; icon: typeof Wind }> = {
  breathing: { name: "Guided breathing", detail: "A short reset to settle a busy mind.", icon: Wind },
  movement: { name: "Gentle movement", detail: "Release tension with easy movement.", icon: Activity },
  mindfulness: { name: "Mindful pause", detail: "Step back and bring attention to the present.", icon: Waves },
  social: { name: "Social connection", detail: "Reconnect with someone who matters.", icon: MessageCircle },
  nature: { name: "A moment outdoors", detail: "A change of scene and a little fresh air.", icon: Leaf },
  creative: { name: "Creative reset", detail: "Make something without an outcome in mind.", icon: Sparkles },
};
function demoRecommendation(f: FormState): Recommendation {
  const category = f.stress >= 4 ? "breathing" : f.energy <= 2 ? "mindfulness" : f.meetings_today >= 5 ? "movement" : "nature";
  const duration = Math.min(f.free_minutes, category === "nature" ? 10 : 5);
  return {
    activity_id: category, category, duration_min: Math.max(2, duration),
    reasons: [
      f.stress >= 4 ? "Your stress check-in is elevated." : "A short pause can fit into your current day.",
      f.energy <= 2 ? "The suggestion keeps physical intensity low." : "The activity fits your available time.",
      "This is a local demo suggestion, not a model-generated result."
    ], demo: true
  };
}
function Metric({ label, value, suffix, icon: Icon, tone = "sage" }: { label: string; value: string; suffix?: string; icon: typeof Activity; tone?: string }) {
  return <div className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={18}/></div><div><span className="metric-label">{label}</span><div className="metric-value">{value}<small>{suffix}</small></div></div></div>;
}

export default function Home() {
  const [form, setForm] = useState<FormState>(initial);
  const [result, setResult] = useState<Recommendation | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [feedback, setFeedback] = useState<"completed" | "skipped" | null>(null);
  const [active, setActive] = useState("overview");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [history, setHistory] = useState<number[]>([62, 68, 64, 73, 70, 78, 74]);

  const update = (key: keyof FormState, value: number | boolean | null) => setForm(old => ({ ...old, [key]: value }));
  const completion = useMemo(() => history[history.length - 1], [history]);

  async function recommend() {
    setBusy(true); setNotice(""); setFeedback(null);
    const requestId = `rw-${Date.now()}`;
    if (!API_URL) {
      await new Promise(resolve => setTimeout(resolve, 550));
      setResult(demoRecommendation(form));
      setNotice("Demo mode · connect the API to use the live recommendation engine.");
      setBusy(false);
      return;
    }
    try {
      const response = await fetch(`${API_URL}/recommend`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, request_id: requestId, user_id: "demo-user", prefs: {} })
      });
      if (!response.ok) throw new Error(`Recommendation request failed (${response.status})`);
      const data = await response.json();
      setResult({ ...data, request_id: requestId });
      setNotice("Live recommendation · served by the Recoverwell API.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Could not reach the API.");
      setResult(null);
    } finally { setBusy(false); }
  }

  async function sendFeedback(value: "completed" | "skipped") {
    if (!result) return;
    setFeedback(value);
    setHistory(old => [...old.slice(-6), Math.min(95, Math.max(35, old[old.length - 1] + (value === "completed" ? 3 : -2)))]);
    if (!API_URL || result.demo) {
      setNotice("Feedback recorded in this demo session only.");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/feedback`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: (result as Recommendation & { request_id?: string }).request_id, activity_id: result.activity_id, completed: value === "completed" })
      });
      if (!response.ok) throw new Error("Feedback could not be saved.");
      setNotice("Thanks — your feedback was sent to the recommendation engine.");
    } catch { setNotice("Feedback could not reach the API. It is shown locally for this session."); }
  }

  const current = result ? (activities[result.category] ?? activities.mindfulness) : null;
  const CurrentIcon = current?.icon ?? Sparkles;

  return <main className="app-shell">
    <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
      <div className="brand"><div className="brand-mark"><Sprout size={22}/></div><span>recoverwell<span className="brand-dot">.</span></span><button className="mobile-close" onClick={() => setMobileMenu(false)} aria-label="Close menu"><X size={18}/></button></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav className="nav-list">
        {[["overview","Overview",Activity],["checkin","Daily check-in",HeartPulse],["intelligence","Intelligence lab",BrainCircuit],["insights","Insights",Target]].map(([id,label,Icon]: any) =>
          <button key={id} className={`nav-item ${active === id ? "active" : ""}`} onClick={() => { setActive(id); setMobileMenu(false); document.getElementById(id === "overview" ? "overview" : id)?.scrollIntoView({ behavior: "smooth" }); }}><Icon size={18}/><span>{label}</span>{id === "checkin" && <span className="nav-indicator"/>}</button>
        )}
      </nav>
      <div className="sidebar-bottom">
        <div className="privacy-note"><ShieldCheck size={17}/><div><strong>Safety comes first</strong><span>Hard constraints are never learned by the model.</span></div></div>
        <div className="profile"><div className="avatar">RW</div><div><strong>Demo workspace</strong><span>Personal research</span></div><ChevronDown size={16}/></div>
      </div>
    </aside>

    <section className="main-area">
      <header className="topbar">
        <button className="mobile-menu" onClick={() => setMobileMenu(true)} aria-label="Open menu"><Menu size={20}/></button>
        <div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div>
        <div className="topbar-right"><span className={`connection ${API_URL ? "connected" : ""}`}><i/>{API_URL ? "API configured" : "Demo environment"}</span><button className="icon-button" aria-label="Help"><CircleHelp size={18}/></button><div className="avatar small">RW</div></div>
      </header>

      <div className="content" id="overview">
        <section className="welcome-row">
          <div><div className="eyebrow"><span className="eyebrow-line"/> YOUR RECOVERY, IN CONTEXT</div><h1>Make room to <em>reset.</em></h1><p className="welcome-copy">A little recovery, thoughtfully timed around your day.</p></div>
          <div className="date-chip"><CalendarDays size={16}/> Thursday, November 26</div>
        </section>

        <section className="hero-card">
          <div className="hero-orb orb-one"/><div className="hero-orb orb-two"/>
          <div className="hero-copy"><span className="hero-kicker"><Sparkles size={14}/> YOUR DAILY MOMENT</span><h2>Wellbeing isn't<br/>one-size-fits-all.</h2><p>Recoverwell brings your check-in, schedule and preferences together to suggest a small, realistic reset.</p><button className="hero-button" onClick={() => document.getElementById("checkin")?.scrollIntoView({ behavior: "smooth" })}>Start your check-in <ArrowRight size={16}/></button></div>
          <div className="hero-art" aria-hidden="true"><div className="sun-disc"/><div className="hill hill-back"/><div className="hill hill-front"/><div className="hero-plant"><span/><span/><span/></div><div className="floating-leaf"><Leaf size={24}/></div></div>
          <div className="hero-caption"><span>01 / 04</span><span>PAUSE · NOTICE · RESET</span></div>
        </section>

        <section className="metrics-grid">
          <Metric label="Today's check-in" value="Not yet" suffix=" pending" icon={HeartPulse}/>
          <Metric label="Recovery window" value={String(form.free_minutes)} suffix=" min" icon={Clock3} tone="peach"/>
          <Metric label="Weekly consistency" value="4" suffix=" / 7 days" icon={Sprout} tone="blue"/>
          <Metric label="Feedback signal" value={String(completion)} suffix="%" icon={Activity} tone="lavender"/>
        </section>

        <div className="section-heading"><div><span className="eyebrow">PERSONALIZED SUPPORT</span><h2>Your next best reset</h2></div><span className="soft-tag"><Waves size={14}/> Context-aware</span></div>
        <section className="recommendation-layout">
          <div className="recommend-card">
            {result ? <><div className="recommend-top"><span className="recommend-label"><Sparkles size={14}/> RECOMMENDED FOR THIS MOMENT</span><span className="match-pill">Suggested</span></div><div className="activity-main"><div className="activity-icon"><CurrentIcon size={25}/></div><div><h3>{current?.name ?? result.category}</h3><p>{current?.detail ?? "A small recovery activity, selected for your context."}</p></div></div><div className="duration-row"><span><Clock3 size={15}/> {result.duration_min} minutes</span><span><ShieldCheck size={15}/> Safety screened</span></div><div className="why-box"><strong>Why this suggestion?</strong>{result.reasons.map((reason,i)=><div className="reason" key={i}><Check size={14}/>{reason}</div>)}</div>{result.support_message && <div className="support-box">{result.support_message}</div>}<div className="feedback-row"><span>Did you try it?</span><button className={feedback === "completed" ? "feedback-selected" : ""} onClick={() => sendFeedback("completed")}><Check size={15}/> Completed</button><button className={feedback === "skipped" ? "feedback-selected" : ""} onClick={() => sendFeedback("skipped")}>Not now</button></div></> :
              <div className="empty-recommend"><div className="empty-icon"><Sparkles size={24}/></div><span className="recommend-label">YOUR PERSONALIZED RESET</span><h3>Your next reset starts<br/>with a check-in.</h3><p>Share a little about how you're feeling. We'll use your context to find a recovery activity that fits.</p><button className="primary-button" onClick={() => document.getElementById("checkin")?.scrollIntoView({ behavior: "smooth" })}>Complete daily check-in <ArrowRight size={16}/></button></div>}
          </div>
          <div className="side-insight"><div className="insight-head"><div className="insight-icon"><CloudSun size={19}/></div><span>THE IDEA</span></div><h3>Small moments<br/>add up.</h3><p>Recovery works best when it fits real life — your energy, your calendar and what feels right today.</p><div className="insight-divider"/><div className="insight-stat"><span>MODEL APPROACH</span><strong>Rules first, learning next</strong><small>Explainable by design</small></div><div className="insight-stat"><span>SAFETY PRINCIPLE</span><strong>Constraints before ranking</strong><small>Never optimized away</small></div></div>
        </section>

        <section className="checkin-section" id="checkin">
          <div className="section-heading"><div><span className="eyebrow">TAKE A MOMENT</span><h2>How are you arriving today?</h2><p>These signals help shape a suggestion that respects your current capacity.</p></div><span className="step-count">01 <i>/</i> 03</span></div>
          <div className="checkin-card">
            <div className="checkin-grid">
              <div className="form-column">
                <div className="field-block"><div className="field-title"><label>How is your mood?</label><strong>{form.mood}/5</strong></div><div className="range-labels"><span>Low</span><span>Good</span></div><input type="range" min="1" max="5" value={form.mood} onChange={e=>update("mood",Number(e.target.value))}/></div>
                <div className="field-block"><div className="field-title"><label>How is your energy?</label><strong>{form.energy}/5</strong></div><div className="range-labels"><span>Drained</span><span>Full</span></div><input type="range" min="1" max="5" value={form.energy} onChange={e=>update("energy",Number(e.target.value))}/></div>
                <div className="field-block"><div className="field-title"><label>How stressed do you feel?</label><strong>{form.stress}/5</strong></div><div className="range-labels"><span>Calm</span><span>Very stressed</span></div><input type="range" min="1" max="5" value={form.stress} onChange={e=>update("stress",Number(e.target.value))}/></div>
              </div>
              <div className="form-column">
                <div className="field-block"><div className="field-title"><label htmlFor="sleep">Sleep last night</label></div><div className="input-with-unit"><Moon size={17}/><input id="sleep" type="number" min="0" max="24" step=".5" value={form.sleep_hours} onChange={e=>update("sleep_hours",Number(e.target.value))}/><span>hours</span></div></div>
                <div className="field-block"><div className="field-title"><label htmlFor="free">Time until your next commitment</label></div><div className="input-with-unit"><Clock3 size={17}/><input id="free" type="number" min="1" max="240" value={form.free_minutes} onChange={e=>update("free_minutes",Number(e.target.value))}/><span>minutes</span></div></div>
                <div className="field-block"><div className="field-title"><label htmlFor="meetings">Meetings or commitments today</label></div><div className="input-with-unit"><CalendarDays size={17}/><input id="meetings" type="number" min="0" max="20" value={form.meetings_today} onChange={e=>update("meetings_today",Number(e.target.value))}/><span>events</span></div></div>
                <label className="toggle-row"><span><strong>Outdoor activities are okay</strong><small>Include options outside</small></span><input type="checkbox" checked={form.outdoor_ok} onChange={e=>update("outdoor_ok",e.target.checked)}/><i/></label>
              </div>
            </div>
            <div className="checkin-footer"><div><ShieldCheck size={16}/><span>Your check-in stays within this demo unless you connect a backend.</span></div><button className="primary-button" onClick={recommend} disabled={busy}>{busy ? <><RefreshCw size={16} className="spin"/> Finding a fit…</> : <>Find my reset <ArrowRight size={16}/></>}</button></div>
            {notice && <p className="notice" role="status">{notice}</p>}
          </div>
        </section>

        <section className="insights-section" id="insights">
          <div className="section-heading"><div><span className="eyebrow">LEARNING OVER TIME</span><h2>Signals, not scores.</h2><p>Illustrative product analytics — not measured clinical outcomes.</p></div><button className="text-button" onClick={() => setHistory(old => [...old.slice(-6), Math.round(45 + Math.random()*45)])}>Simulate a week <ArrowRight size={15}/></button></div>
          <div className="insights-grid">
            <div className="chart-card"><div className="chart-top"><div><span>ILLUSTRATIVE TREND</span><h3>Completion signal</h3></div><span className="trend-pill"><ArrowUpRight size={14}/> +12%</span></div><div className="chart-value">{completion}<small>/ 100</small></div><div className="chart-wrap"><svg viewBox="0 0 560 145" role="img" aria-label="Illustrative completion signal trend"><defs><linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#6e9b7d" stopOpacity=".28"/><stop offset="100%" stopColor="#6e9b7d" stopOpacity="0"/></linearGradient></defs><path d={`M ${history.map((v,i)=>`${i*90} ${125-v*1.25}`).join(" L ")} L ${(history.length-1)*90} 145 L 0 145 Z`} fill="url(#area)"/><polyline points={history.map((v,i)=>`${i*90},${125-v*1.25}`).join(" ")} fill="none" stroke="#58836a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>{history.map((v,i)=><circle key={i} cx={i*90} cy={125-v*1.25} r="4" fill="#fff" stroke="#58836a" strokeWidth="2"/>)}</svg></div><div className="chart-days"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span><span>SUN</span></div></div>
            <div className="principle-card"><div className="principle-icon"><BrainCircuit size={21}/></div><span>THE LEARNING LOOP</span><h3>Context → Suggestion → Feedback → Better fit.</h3><p>Recoverwell starts with transparent rules. As reliable feedback accumulates, an adaptive model can learn where those rules need to improve.</p><div className="loop-row"><span>01 Context</span><ArrowRight size={13}/><span>02 Rank</span><ArrowRight size={13}/><span>03 Learn</span></div></div>
          </div>
        </section>

        <section className="lab-section" id="intelligence">
          <div className="section-heading"><div><span className="eyebrow">UNDER THE HOOD</span><h2>The intelligence lab</h2><p>Four strategies. One safety layer. Transparent evaluation.</p></div><span className="soft-tag"><BrainCircuit size={14}/> Research preview</span></div>
          <div className="policy-grid">
            {[["Random","Baseline","A simple reference point.", "neutral"],["Rules","Explainable","A transparent cold-start policy.", "sage"],["LinUCB","Adaptive","Learns from contextual feedback.", "blue"],["Hybrid","Combined","Rules as prior, learning as correction.", "peach"]].map(([name,type,desc,tone])=><div className="policy-card" key={name}><div className={`policy-dot ${tone}`}/><span>{type}</span><h3>{name}</h3><p>{desc}</p><div className="policy-foot">{name === "Hybrid" ? "RULES + BANDIT" : name === "LinUCB" ? "CONTEXTUAL BANDIT" : name === "Rules" ? "HEURISTIC BASELINE" : "RANDOM BASELINE"}</div></div>)}
          </div>
        </section>

        <footer className="footer"><div className="footer-brand"><Sprout size={17}/> recoverwell<span>.</span></div><p>Built for thoughtful recovery. Designed to be explainable.</p><span>Research prototype · Not a medical device</span></footer>
      </div>
    </section>
  </main>;
}