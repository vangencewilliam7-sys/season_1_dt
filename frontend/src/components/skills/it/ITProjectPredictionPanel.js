'use client';
import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function ITProjectPredictionPanel() {
  const [metrics, setMetrics] = useState({
    velocity_delta: -5.0,
    requirement_churn: 0.15,
    dependency_lag_days: 2,
    qa_failure_rate: 0.1,
    team_burnout_risk: 0.2
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
        project_id: "550e8400-e29b-41d4-a716-446655440000",
        ...metrics
      };

      const reqBody = {
        skill_name: 'SKL_IT_PROJECT_PREDICTION',
        payload: payloadObj,
        metadata: {
          workflow_id: "00000000-0000-0000-0000-000000000000",
          expert_id: "11111111-1111-1111-1111-111111111111"
        }
      };

      const res = await fetch(`${API_BASE}/skills/execute/SKL_IT_PROJECT_PREDICTION`, {
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
    width: '100%', padding: '10px', borderRadius: 8,
    border: '1px solid var(--border)', background: 'var(--bg-elevated)',
    color: 'var(--text-primary)', fontSize: 13, marginBottom: 12
  };
  const labelStyle = { fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 6 };

  const getRiskColor = (prob) => {
    if (prob > 60) return '#ef4444';
    if (prob > 30) return '#f59e0b';
    return '#10b981';
  };

  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', padding: '24px', marginTop: 16
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <h4 style={{ margin: '0 0 4px 0', fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            🛡️ IT Pre-Mortem Prediction Engine
          </h4>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Simulate future project failure points and generate strategic mitigations.
          </p>
        </div>
        <div style={{ 
          background: 'var(--bg-elevated)', padding: '6px 12px', borderRadius: 20, 
          fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', border: '1px solid var(--border)' 
        }}>
          VERSION 2.1 (PREDICTIVE)
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Left Column: Metrics Input */}
        <div style={{ padding: '20px', background: 'rgba(0,0,0,0.02)', borderRadius: 16, border: '1px solid var(--border)' }}>
          <h5 style={{ margin: '0 0 16px 0', fontSize: '0.9rem', color: 'var(--text-primary)' }}>Execution Metrics</h5>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={labelStyle}>Velocity Delta (%)</label>
              <input type="number" style={inputStyle} value={metrics.velocity_delta} onChange={e => handleUpdateMetric('velocity_delta', parseFloat(e.target.value))} />
            </div>
            <div>
              <label style={labelStyle}>Req. Churn (%)</label>
              <input type="number" step="0.05" style={inputStyle} value={metrics.requirement_churn} onChange={e => handleUpdateMetric('requirement_churn', parseFloat(e.target.value))} />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={labelStyle}>Dependency Lag (Days)</label>
              <input type="number" style={inputStyle} value={metrics.dependency_lag_days} onChange={e => handleUpdateMetric('dependency_lag_days', parseInt(e.target.value))} />
            </div>
            <div>
              <label style={labelStyle}>QA Fail Rate (%)</label>
              <input type="number" step="0.05" style={inputStyle} value={metrics.qa_failure_rate} onChange={e => handleUpdateMetric('qa_failure_rate', parseFloat(e.target.value))} />
            </div>
          </div>

          <label style={labelStyle}>Team Burnout Risk (0-1)</label>
          <input type="range" min="0" max="1" step="0.1" style={{ width: '100%', marginBottom: 20 }} value={metrics.team_burnout_risk} onChange={e => handleUpdateMetric('team_burnout_risk', parseFloat(e.target.value))} />

          <button
            onClick={handleExecute}
            disabled={loading}
            style={{
              width: '100%', background: 'linear-gradient(135deg, #4f46e5 0%, #3730a3 100%)',
              color: '#fff', border: 'none', padding: '12px', borderRadius: 10,
              fontWeight: 700, fontSize: 13, cursor: loading ? 'wait' : 'pointer',
              boxShadow: '0 4px 12px rgba(79, 70, 229, 0.2)'
            }}
          >
            {loading ? '⏳ Simulating Project Trajectory...' : '🚀 Run Pre-Mortem Analysis'}
          </button>
        </div>

        {/* Right Column: Prediction Results */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {!result && !loading && (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '2px dashed var(--border)', borderRadius: 16, color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: 40 }}>
              Adjust project metrics and run the simulation to see future failure predictions.
            </div>
          )}

          {loading && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
              <div className="pulse-loader" style={{ width: 60, height: 60, background: 'rgba(79, 70, 229, 0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ width: 30, height: 30, border: '3px solid #4f46e5', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
              </div>
              <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>Analyzing Critical Path...</span>
              <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
            </div>
          )}

          {result && result.status === 'SUCCESS' && (
            <>
              {/* Risk Gauge */}
              <div style={{ 
                padding: '24px', borderRadius: 16, background: 'var(--bg-elevated)',
                border: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 20
              }}>
                <div style={{ 
                  width: 80, height: 80, borderRadius: '50%', border: `8px solid ${getRiskColor(result.data.failure_probability)}22`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative'
                }}>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: getRiskColor(result.data.failure_probability) }}>
                    {result.data.failure_probability}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', marginBottom: 4 }}>PROJECT FAILURE RISK</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {result.data.failure_probability > 60 ? 'CRITICAL RISK' : result.data.failure_probability > 30 ? 'MODERATE RISK' : 'HEALTHY PROJECT'}
                  </div>
                </div>
              </div>

              {/* Strategic Briefing Card */}
              <div style={{ 
                padding: '24px', borderRadius: 16, 
                background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)',
                color: '#fff', border: '1px solid rgba(79, 70, 229, 0.3)',
                boxShadow: '0 8px 24px rgba(0,0,0,0.1)'
              }}>
                <div style={{ fontSize: 11, color: '#a5b4fc', fontWeight: 800, marginBottom: 12, letterSpacing: '0.05em' }}>
                  🎯 STRATEGIC MITIGATION (PRE-MORTEM)
                </div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: 12, lineHeight: 1.3 }}>
                  {result.data.next_best_action}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#e0e7ff', lineHeight: 1.5, opacity: 0.9 }}>
                  {result.data.rationale}
                </div>
              </div>

              {/* Root Cause Detail */}
              <div style={{ 
                padding: '16px', borderRadius: 12, border: '1px solid var(--border)',
                background: 'rgba(0,0,0,0.01)', fontSize: '0.85rem'
              }}>
                <span style={{ fontWeight: 700, color: 'var(--text-secondary)' }}>Root Cause:</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: 8 }}>{result.data.root_cause}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
