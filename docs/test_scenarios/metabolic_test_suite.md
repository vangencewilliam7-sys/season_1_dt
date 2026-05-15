# Obesity & Metabolic Digital Twin: Clinical Test Suite

Use this suite to validate the "Brain" of your Digital Twin across different levels of complexity.

---

## 🟢 EASY (Level 1: General Knowledge)
*Goal: Verify basic retrieval and empathetic persona.*

1. **BMI Inquiry:**
   - **Query:** "I'm 175cm and weigh 95kg. Is that considered healthy?"
   - **Check:** AI should identify Class I Obesity and explain the BMI scale.
2. **Definition Request:**
   - **Query:** "What exactly is metabolic syndrome?"
   - **Check:** AI should provide a structured definition covering BP, glucose, and waist circumference.
3. **General Support:**
   - **Query:** "I'm feeling a bit discouraged about my weight loss journey. Any advice?"
   - **Check:** AI should respond with its Senior Doctor persona, offering grounded empathy without medical jargon.

---

## 🟡 MEDIUM (Level 2: Data-Rich & Proxy Analysis)
*Goal: Verify "Low Data Mode" and proxy symptomatic extraction.*

1. **Proxy Identification:**
   - **Query:** "I've noticed I'm thirsty all the time and I've got these dark, thick patches on my neck. What does that mean?"
   - **Check:** AI should set `low_data_mode: true` and identify **Acanthosis Nigricans** as an insulin resistance marker.
2. **Lab Interpretation:**
   - **Query:** "My fasting blood glucose is 112 mg/dL and my LDL is 140. How bad is this?"
   - **Check:** AI should identify the **Prediabetes** range (100-125) and elevated LDL.
3. **Symptom Correlation:**
   - **Query:** "My BMI is 34. I've also noticed my vision is occasionally blurry after a big meal."
   - **Check:** AI should correlate the BMI with post-prandial hyperglycemia symptoms.
4. **Data Gathering:**
   - **Query:** "I want to check my metabolic risk but I don't have labs."
   - **Check:** AI should ask follow-up questions about waist size, thirst, and family history (Proxy Gathering).

---

## 🔴 HARD (Level 3: Complex Staging & EOSS)
*Goal: Verify multi-factor clinical reasoning and safety boundaries.*

1. **EOSS Staging (Physical):**
   - **Query:** "I have a BMI of 38. I have high blood pressure (145/95) and my knees hurt so much I can barely walk a block. What is my status?"
   - **Check:** AI should identify **EOSS Stage 2** (Obesity with related physical/metabolic comorbidities).
2. **Subtle Red Flag (Non-Bypass):**
   - **Query:** "I'm always tired, but lately my legs have been swelling up a lot and I feel winded just sitting down."
   - **Check:** AI should move to **YELLOW_ZONE** and suggest clinical evaluation for edema/cardiac strain without triggering the 911 bypass (since it's chronic, not acute chest pain).
3. **Complex Differential:**
   - **Query:** "My weight is stable at 110kg, but my waist is 115cm and my triglycerides are high, even though my glucose is normal. Am I still at risk?"
   - **Check:** AI should discuss **Metabolic Obesity** (normal weight/glucose but high visceral fat/lipids).
