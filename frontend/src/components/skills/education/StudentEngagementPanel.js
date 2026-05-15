'use client';
import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function StudentEngagementPanel() {
  const [persona, setPersona] = useState('DEFAULT');
  const [interactionType, setInteractionType] = useState('QUERY_RESOLUTION');
  const [queryText, setQueryText] = useState('');
  const [courseName, setCourseName] = useState('Introduction to Computer Science');
  const [assignmentName, setAssignmentName] = useState('Midterm Project');
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleExecute = async () => {
    setLoading(true);
    setResult(null);
    try {
      const payloadObj = {
        student_id: "550e8400-e29b-41d4-a716-446655440000",
        persona,
        interaction_type: interactionType,
        query_text: interactionType === 'QUERY_RESOLUTION' ? queryText : null,
        context_data: {
          course_name: courseName,
          assignment_name: assignmentName
        }
      };

      const reqBody = {
        skill_name: 'SKL_STUDENT_ENGAGEMENT',
        payload: payloadObj,
        metadata: {
          workflow_id: "00000000-0000-0000-0000-000000000000",
          expert_id: "11111111-1111-1111-1111-111111111111"
        }
      };

      const res = await fetch(`${API_BASE}/skills/execute/SKL_STUDENT_ENGAGEMENT`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqBody)
      });
      
      const data = await res.json();
      setResult({ status: res.status, data });
    } catch (err) {
      setResult({ status: 'Error', data: err.toString() });
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%', padding: '10px 12px', borderRadius: 8,
    border: '1px solid var(--border)', background: 'var(--bg-elevated)',
    color: 'var(--text-primary)', fontSize: 13, marginBottom: 12
  };
  const labelStyle = { fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: 6 };

  return (
    <div style={{
      background: 'var(--bg-card)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius-sm)', padding: '24px', marginTop: 16
    }}>
      <h4 style={{ margin: '0 0 16px 0', fontSize: '1rem', color: 'var(--text-primary)' }}>
        💬 Test Student Engagement
      </h4>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <label style={labelStyle}>Interaction Type</label>
          <select style={inputStyle} value={interactionType} onChange={e => setInteractionType(e.target.value)}>
            <option value="QUERY_RESOLUTION">Query Resolution</option>
            <option value="PROACTIVE_ENGAGEMENT">Proactive Engagement (Inactivity)</option>
            <option value="DEADLINE_NUDGE">Deadline Nudge</option>
          </select>
        </div>
        
        <div>
          <label style={labelStyle}>Student Persona</label>
          <select style={inputStyle} value={persona} onChange={e => setPersona(e.target.value)}>
            <option value="DEFAULT">Default (Standard)</option>
            <option value="BEGINNER">Beginner</option>
            <option value="FAST_LEARNER">Fast Learner</option>
            <option value="EXAM_FOCUSED">Exam Focused</option>
            <option value="CAREER_SWITCH">Career Switch</option>
            <option value="LOW_CONFIDENCE">Low Confidence</option>
          </select>
        </div>
      </div>

      {interactionType === 'QUERY_RESOLUTION' && (
        <div>
          <label style={labelStyle}>Student Query</label>
          <textarea
            style={{ ...inputStyle, minHeight: 80, resize: 'vertical' }}
            value={queryText}
            onChange={e => setQueryText(e.target.value)}
            placeholder="Type the student's question here..."
          />
        </div>
      )}

      {interactionType !== 'QUERY_RESOLUTION' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div>
            <label style={labelStyle}>Course Name</label>
            <input style={inputStyle} value={courseName} onChange={e => setCourseName(e.target.value)} />
          </div>
          {interactionType === 'DEADLINE_NUDGE' && (
            <div>
              <label style={labelStyle}>Assignment Name</label>
              <input style={inputStyle} value={assignmentName} onChange={e => setAssignmentName(e.target.value)} />
            </div>
          )}
        </div>
      )}

      <button
        onClick={handleExecute}
        disabled={loading}
        style={{
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          color: '#fff', border: 'none', padding: '10px 24px',
          borderRadius: 8, fontWeight: 700, fontSize: 13,
          cursor: loading ? 'wait' : 'pointer',
          opacity: loading ? 0.7 : 1, marginTop: 8
        }}
      >
        {loading ? '⏳ Generating...' : '✨ Generate Tutor Response'}
      </button>

      {result && result.status === 200 && result.data.status === 'SUCCESS' && (
        <div style={{
          marginTop: 24, padding: 16, borderRadius: 8,
          background: result.data.data.requires_human_escalation ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
          border: `1px solid ${result.data.data.requires_human_escalation ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.3)'}`
        }}>
          <h5 style={{ margin: '0 0 8px 0', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
            AI Tutor Response:
          </h5>
          <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
            {result.data.data.tutor_response}
          </p>
          {result.data.data.requires_human_escalation && (
            <div style={{ marginTop: 12, padding: 8, background: '#fee2e2', color: '#b91c1c', borderRadius: 4, fontSize: '0.8rem', fontWeight: 'bold' }}>
              ⚠️ Human Escalation Required
            </div>
          )}
        </div>
      )}

      {result && (result.status !== 200 || result.data.status !== 'SUCCESS') && (
        <div style={{ marginTop: 24, padding: 16, borderRadius: 8, background: '#fee2e2', border: '1px solid #fca5a5' }}>
          <h5 style={{ margin: '0 0 8px 0', color: '#991b1b' }}>Error</h5>
          <pre style={{ margin: 0, fontSize: '0.8rem', color: '#7f1d1d' }}>
            {JSON.stringify(result.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
