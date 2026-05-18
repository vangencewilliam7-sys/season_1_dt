/**
 * demo_seed.js — Isolated Demo Data Layer
 * =========================================
 * All hardcoded data for the mentor demo.
 */

export const DEMO_TRANSCRIPT = [
  {
    id: 'msg_001',
    role: 'user',
    content: 'Hi doctor, I have been feeling extremely tired lately and no matter how much water I drink, I am always thirsty.',
    sender: 'patient',
    created_at: '2026-05-18T09:12:00Z',
    source_case_id: null,
  },
  {
    id: 'msg_002',
    role: 'assistant',
    content: 'I am sorry to hear you are feeling that way. Constant thirst and fatigue can sometimes point to metabolic issues or pre-diabetes. To help me understand better, have you noticed any changes in your weight recently, or perhaps your belt feeling tighter?',
    sender: 'twin',
    confidence: 0.91,
    rationale: 'Retrieved MasterCase: Metabolic Obesity Pathway v2.1. Unexplained fatigue + polydipsia triggers structured symptomatic proxy collection for central adiposity and insulin resistance.',
    source_case_id: 'CASE_HC_001',
    created_at: '2026-05-18T09:12:18Z',
  },
  {
    id: 'msg_003',
    role: 'user',
    content: 'Yes, I actually had to loosen my belt by two notches over the last few months, even though the scale hasn\'t changed much.',
    sender: 'patient',
    created_at: '2026-05-18T09:13:05Z',
    source_case_id: null,
  },
  {
    id: 'msg_004',
    role: 'assistant',
    content: 'Thank you for sharing that. The combination of excessive thirst, chronic fatigue, and an increase in waist size are strong clinical indicators of potential Metabolic Syndrome and Central Obesity. We really need to get some formal lab work done to check your blood glucose levels.',
    sender: 'twin',
    confidence: 0.88,
    rationale: 'Retrieved MasterCase: EOSS Stage 2 Clinical Decision v1.0. Waist circumference increase + thirst/fatigue → YELLOW_ZONE triage. Triggers lab panel recommendation for HbA1c and fasting glucose.',
    source_case_id: 'CASE_HC_002',
    created_at: '2026-05-18T09:13:22Z',
  },
  {
    id: 'msg_005',
    role: 'user',
    content: 'I don\'t really have time to go to a clinic right now. Can you just tell me what diet to follow or what medicine to take to fix this?',
    sender: 'patient',
    created_at: '2026-05-18T09:14:01Z',
    source_case_id: null,
  },
  {
    id: 'msg_006',
    role: 'assistant',
    content: 'I completely understand that finding time is difficult, but your symptoms are concerning and cannot be safely managed with a blind guess online. I strongly urge you to book a formal consultation with a physician so we can order an HbA1c test and a lipid panel. It is critical we get accurate data to protect your long-term health.',
    sender: 'twin',
    confidence: 0.89,
    rationale: 'Guardrail triggered: Cannot prescribe diet or medication without a formal lab diagnosis and human physician sign-off. Emphasizing the necessity of a physical consultation to the patient.',
    source_case_id: 'CASE_HC_003',
    created_at: '2026-05-18T09:14:45Z',
  },
  {
    id: 'msg_007',
    role: 'user',
    content: 'Are you sure it\'s that serious? I just thought I was working too hard.',
    sender: 'patient',
    created_at: '2026-05-18T09:15:10Z',
    source_case_id: null,
  },
  {
    id: 'msg_008',
    role: 'assistant',
    content: 'While overworking can certainly cause fatigue, the extreme thirst and waist expansion point directly to metabolic changes that stress alone cannot explain. Catching this early makes it highly treatable, but ignoring it can lead to severe complications. Please, let\'s get this checked. Would you like me to help you schedule a quick 15-minute consultation?',
    sender: 'twin',
    confidence: 0.85,
    rationale: 'Patient expressing hesitation. Applying empathetic persistence protocol to secure a clinical consultation for suspected Metabolic Syndrome.',
    source_case_id: 'CASE_HC_001',
    created_at: '2026-05-18T09:15:28Z',
  },
  {
    id: 'msg_009',
    role: 'assistant',
    content: 'I want to step in here and agree completely with the Digital Twin. The symptoms you are describing need clinical attention. I am opening up a priority slot for you tomorrow morning at 9 AM so we can run these labs. Please book it. — Dr. Venkatesh',
    sender: 'human_expert',
    confidence: 1.0,
    rationale: 'Direct Expert Override — Dr. Venkatesh intervening to secure the appointment after observing patient hesitation in the transcript.',
    source_case_id: null,
    is_expert_override: true,
    created_at: '2026-05-18T09:16:02Z',
  },
];

export const DEMO_LOGIC_VAULT = {
  CASE_HC_001: {
    id: 'CASE_HC_001',
    title: 'Hypertensive Patient Initial Triage',
    version: 'v1.3',
    domain: 'Healthcare',
    workflow: 'Patient Consultation',
    triage_decision: 'YELLOW_ZONE',
    confidence_trigger: 0.70,
    rule: `When a patient presents with:
• Systolic BP ≥ 140 mmHg OR Diastolic BP ≥ 90 mmHg
• AND any 2 of: fatigue, morning headaches, chest tightness

→ INITIATE: Structured symptomatic proxy collection (5-question cascade)
→ DEFER dietary prescriptions to human physician
→ FLAG: If BP ≥ 160/100, escalate immediately to RED_ZONE`,
    approved_by: 'Dr. R. Venkatesh, MD (Cardiology)',
    approved_date: '2026-03-14',
    times_used: 47,
    last_updated: '2026-04-02',
  },
  CASE_HC_002: {
    id: 'CASE_HC_002',
    title: 'Metabolic Obesity Pathway',
    version: 'v2.1',
    domain: 'Healthcare',
    workflow: 'Patient Consultation',
    triage_decision: 'YELLOW_ZONE',
    confidence_trigger: 0.75,
    rule: `When waist circumference exceeds 38 inches (male) or 35 inches (female):
• AND BMI ≥ 30 (Obese Class I or higher)
• AND co-morbidity present (hypertension, fatigue, or dyslipidaemia)

→ INITIATE: EOSS (Edmonton Obesity Staging System) Stage 2 screening
→ COLLECT: Height, weight for BMI calculation
→ RECOMMEND: HbA1c + fasting glucose if not tested in > 12 months
→ DO NOT prescribe: specific diet or medication (physician role)`,
    approved_by: 'Dr. S. Priya, MD (Endocrinology)',
    approved_date: '2026-02-28',
    times_used: 31,
    last_updated: '2026-04-18',
  },
  CASE_HC_003: {
    id: 'CASE_HC_003',
    title: 'EOSS Stage 2 Clinical Decision',
    version: 'v1.0',
    domain: 'Healthcare',
    workflow: 'Diagnostic Analysis',
    triage_decision: 'YELLOW_ZONE',
    confidence_trigger: 0.80,
    rule: `EOSS Stage 2 classification when ALL of the following:
• BMI ≥ 30 (calculated)
• Waist circumference in obese range
• ≥1 metabolic comorbidity (hypertension, impaired glucose, dyslipidaemia)

→ TRIAGE: YELLOW_ZONE (elevated clinical priority, non-emergency)
→ RECOMMEND LAB PANEL:
  - Fasting blood glucose
  - HbA1c
  - Lipid panel (TC, LDL, HDL, TG)
  - Formal BP measurement (clinical setting)
→ FLAG for physician review before treatment prescription
→ Confidence ≥ 0.90 required for prescriptive dietary guidance`,
    approved_by: 'Dr. R. Venkatesh, MD (Cardiology)',
    approved_date: '2026-04-01',
    times_used: 19,
    last_updated: '2026-04-01',
  },
};

export const DEMO_STATS = {
  bot_handled_pct: 89,
  total_turns: 9,
  turns_handled_by_bot: 8,
  expert_corrections: 1,
  session_duration_min: 4,
  triage_accuracy: 'YELLOW_ZONE — Confirmed Correct',
  avg_confidence: 0.86,
  guardrails_triggered: 1,
  patient_name: 'Arun K., 42M',
  session_date: '2026-05-18',
  session_id: 'DEMO-SESSION-001',
};

export const DEMO_PATIENT = {
  name: 'Arun K.',
  age: 42,
  gender: 'Male',
  bmi: 30.3,
  weight_kg: 96,
  height_cm: 177.8,
  bp: '142/92 mmHg',
  waist_inches: 40,
  last_hba1c: 'Not tested (> 2 years)',
  triage_zone: 'YELLOW_ZONE',
};
