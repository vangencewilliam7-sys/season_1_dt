# IT Project Manager - Demo Test Suite (Swagger Edition)

Use these cases to demonstrate the **Unified Digital Twin**'s ability to handle complex IT project management scenarios.

---

## 🟢 Easy: Operational Basics

### 1. The Quick Load Check
*   **Prompt:** "Can I assign the 'Bug-404' ticket to Developer Sarah? She currently has 1 active ticket."
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-01",
  "domain": "IT",
  "role": "Project Manager",
  "message": "Can I assign the 'Bug-404' ticket to Developer Sarah? She currently has 1 active ticket."
}
```

### 2. The Skill Search
*   **Prompt:** "Who on the team has the 'Security' tag?"
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-02",
  "domain": "IT",
  "role": "Project Manager",
  "message": "Who on the team has the 'Security' tag?"
}
```

---

## 🟡 Medium: Conflict Resolution

### 3. The Overload Reroute
*   **Prompt:** "Developer Sarah is at 95% capacity. A new P1 Security Patch just came in. Should she handle it?"
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-03",
  "domain": "IT",
  "role": "Project Manager",
  "message": "Developer Sarah is at 95% capacity. A new P1 Security Patch just came in. Should she handle it?"
}
```

### 4. The Mentorship Bridge
*   **Prompt:** "Sarah is busy with a migration, but we need a Security fix. John is free but is a Junior. What should we do?"
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-04",
  "domain": "IT",
  "role": "Project Manager",
  "message": "Sarah is busy with a migration, but we need a Security fix. John is free but is a Junior. What should we do?"
}
```

---

## 🔴 Hard: Crisis & Strategy

### 5. The Zero-Day Trade-off
*   **Prompt:** "A Zero-Day vulnerability was found, but we are 4 hours away from our major Release 2.0. The only person who can fix it is the Lead Dev. Should we release or fix?"
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-05",
  "domain": "IT",
  "role": "Project Manager",
  "message": "A Zero-Day vulnerability was found, but we are 4 hours away from our major Release 2.0. The only person who can fix it is the Lead Dev. Should we release or fix?"
}
```

### 6. The Technical Debt Trap
*   **Prompt:** "The last three sprints had minor production bugs. Stakeholders want the 'New Dashboard' now, but devs want to refactor. Decision?"
*   **Swagger JSON:**
```json
{
  "expert_id": "it-manager-001",
  "session_id": "demo-it-06",
  "domain": "IT",
  "role": "Project Manager",
  "message": "The last three sprints had minor production bugs. Stakeholders want the 'New Dashboard' now, but devs want to refactor. Decision?"
}
```
