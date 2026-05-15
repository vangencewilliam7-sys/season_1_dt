# The IT Digital Twin: Workflow - The "Pre-Mortem" Prediction Engine

## Goal
To predict project delays and technical bottlenecks weeks before they occur, providing a "Project Confidence Score" based on real-time team velocity and dependency health.

## Core Capabilities
1. **Velocity vs. Volatility Analysis**: Tracks how fast the team is moving relative to how often requirements are changing.
2. **Bottleneck Heatmapping**: Identifies specific teams or modules that are slowing down the delivery pipeline (e.g., "API documentation is lagging behind frontend development").
3. **Dependency Risk Scoring**: Calculates the probability of a delay based on third-party integrations or cross-team blockers.

## The WOW Task: "Pre-Mortem Simulation"
The Twin runs a daily simulation of the project's trajectory. If the probability of a "missed deadline" exceeds 40%, it triggers a proactive briefing:
- **Findings**: Identifies the exact cause (e.g., "Database migration is 3 days behind").
- **Impact Synthesis**: Predicts the cascading delay on downstream tasks.
- **Next Best Action (NBA)**: Suggests a specific mitigation (e.g., "Shift 1 Senior Dev from the UI team to the DB team for 48 hours to unblock the pipeline").

## Implementation Strategy
- **Backend Skill**: `SKL_IT_PROJECT_PREDICTION`
- **Frontend Component**: `ITProjectPredictionPanel.js` (Featuring a "Risk Probability Gauge" and "Simulated Timeline").
- **Deep Metrics**:
    - `velocity_volatility_ratio`
    - `dependency_lag_score`
    - `requirement_churn_rate`
