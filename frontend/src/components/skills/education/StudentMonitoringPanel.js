'use client';
import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function StudentMonitoringPanel() {
  const [metrics, setMetrics] = useState({
    login_frequency: 5,
    avg_score: 75,
    missed_deadlines: 0,
    curiosity_coefficient: 0.5,
    sentiment_trajectory: 'STABLE',
    help_seeking_delay_days: 2,
    habit_consistency: 0.8
  });
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpdateMetric = (key, val) => {
    setMetrics(prev => ({ ...prev, [key]: val }));
  };

  const handleExecute = async () => {
    setLoading(true);
    setResult(null);
    try {
      const payloadObj = {
        student_id: "550e8400-e29b-41d4-a716-446655440000",
        persona: "DEFAULT",
        ...metrics
      };

      const reqBody = {
        skill_name: 'SKL_STUDENT_MONITORING',
        payload: payloadObj,
        metadata: {
          workflow_id: "00000000-0000-0000-0000-000000000000",
          expert_id: "11111111-1111-1111-1111-111111111111"
        }
      };

      const res = await fetch(`${API_BASE}/skills/execute/SKL_STUDENT_MONITORING`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      });
      
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ status: 'ERROR', message: err.toString() });
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%', padding: '8px 10px', borderRadius: 6,
    border: '1px solid var(--border)', background: 'var(--bg-elevated)',
    color: 'var(--text-primary)', fontSize: 12, marginBottom: 8
  };
  const labelStyle = { fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 4 };

  const getTriageColor = (level) => {
    if (level === 'HIGH') return '#ef4444';
    if (level === 'MEDIUM') return '#f59e0b';
    return '#10b981';
  };

  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', padding: '24px', marginTop: 16
    }}>
      <h4 style={{ margin: '0 0 4px 0', fontSize: '1rem', color: 'var(--text-primary)' }}>
        🧠 Student Monitoring & Risk Escalation
      </h4>
      <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Analyze "Deep Intelligence" metrics to identify at-risk learners and suggest interventions.
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Input Controls */}
        <div style={{ padding: '16px', background: 'rgba(0,0,0,0.02)', borderRadius: 12 }}>
          <h5 style={{ margin: '0 0 12px 0', fontSize: '0.85rem' }}>Behavioral Inputs</h5>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={labelStyle}>Logins (7d)</label>
              <input type="number" style={inputStyle} value={metrics.login_frequency} onChange={e => handleUpdateMetric('login_frequency', parseInt(e.target.value))} />
            </div>
            <div>
              <label style={labelStyle}>Avg Score (%)</label>
              <input type="number" style={inputStyle} value={metrics.avg_score} onChange={e => handleUpdateMetric('avg_score', parseFloat(e.target.value))} />
            </div>
          </div>

          <label style={labelStyle}>Sentiment Trajectory</label>
          <select style={inputStyle} value={metrics.sentiment_trajectory} onChange={e => handleUpdateMetric('sentiment_trajectory', e.target.value)}>
            <option value="IMPROVING">Improving</option>
            <option value="STABLE">Stable</option>
            <option value="DECLINING">Declining</option>
          </select>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={labelStyle}>Curiosity (0-1)</label>
              <input type="number" step="0.1" style={inputStyle} value={metrics.curiosity_coefficient} onChange={e => handleUpdateMetric('curiosity_coefficient', parseFloat(e.target.value))} />
            </div>
            <div>
              <label style={labelStyle}>Help Delay (Days)</label>
              <input type="number" style={inputStyle} value={metrics.help_seeking_delay_days} onChange={e => handleUpdateMetric('help_seeking_delay_days', parseInt(e.target.value))} />
            </div>
          </div>

          <button
            onClick={handleExecute}
            disabled={loading}
            style={{
              width: '100%', background: 'var(--text-primary)', color: 'var(--bg-card)',
              border: 'none', padding: '10px', borderRadius: 8, fontWeight: 700,
              fontSize: 12, cursor: 'pointer', marginTop: 8
            }}
          >
            {loading ? '⏳ Analyzing Patterns...' : '🔍 Run Risk Analysis'}
          </button>
        </div>

        {/* Results / Analysis */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {!result && !loading && (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px dashed var(--border)', borderRadius: 12, color: 'var(--text-muted)', fontSize: 13 }}>
              Enter metrics and run analysis
            </div>
          )}

          {loading && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
              <div style={{ width: 40, height: 40, border: '3px solid var(--border)', borderTopColor: 'var(--text-primary)', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Calculating Triage Probability...</span>
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {result && result.status === 'SUCCESS' && (
            <>
              {/* Risk Level Badge */}
              <div style={{ 
                padding: '16px', borderRadius: 12, background: 'var(--bg-elevated)',
                borderLeft: `6px solid ${getTriageColor(result.data.triage_level)}`
              }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>TRIAGE CLASSIFICATION</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 800, color: getTriageColor(result.data.triage_level) }}>
                  {result.data.triage_level} RISK ({result.data.risk_score}/100)
                </div>
              </div>

              {/* NBA Engine Card */}
              <div style={{ 
                padding: '20px', borderRadius: 12, 
                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%)',
                border: '1px solid rgba(16, 185, 129, 0.2)'
              }}>
                <div style={{ fontSize: 11, color: '#059669', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  🎯 NEXT BEST ACTION (NBA ENGINE)
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>
                  {result.data.next_best_action}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {result.data.intervention_reasoning}
                </div>
              </div>

              {/* Synthesis */}
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '0 8px' }}>
                " {result.data.analysis} "
              </div>
            </>
          )}

          {result && result.status === 'ERROR' && (
            <div style={{ padding: 16, background: '#fee2e2', color: '#b91c1c', borderRadius: 12, fontSize: 12 }}>
              <strong>Analysis Failed:</strong> {result.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
