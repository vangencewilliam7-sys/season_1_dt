# Frontend Architecture: Season 1 Digital Twin

This document details the frontend architecture, page structure, components, and design system of the Season 1 Digital Twin application.

## 1. High-Level Architecture
The frontend is built as a modern Single Page Application (SPA) utilizing Server-Side Rendering (SSR) capabilities where applicable, powered by **Next.js**. It communicates with a backend API (FastAPI) and internal Next.js API routes for data fetching and real-time updates.

### Tech Stack
- **Framework:** Next.js 14.2.5 (App Router paradigm)
- **Library:** React 18
- **Language:** JavaScript (ES6+)
- **Styling:** Vanilla CSS (`globals.css`) combined with component-level inline styles.
- **Icons:** `lucide-react` + Custom SVG icon components.
- **Data Fetching:** Client-side `fetch` hooks (e.g., `useEffect`, `useState`) and Next.js route handlers (`/api/*`).

### Directory Structure
```text
frontend/
├── src/
│   ├── app/            # Next.js App Router (Pages, Layouts, API routes)
│   ├── components/     # Reusable UI and Layout components
│   ├── lib/            # Utility functions and library wrappers
│   └── styles/         # Additional styles
├── public/             # Static assets
├── next.config.js      # Next.js configuration
└── package.json        # Dependencies & scripts
```

---

## 2. Page Structure (Total: 9 Pages)
The application utilizes the Next.js App Router. Each route is defined by a `page.js` file inside the corresponding directory within `src/app/`.

1. **Root / Dashboard (`/`)** 
   - *File:* `src/app/page.js`
   - *Description:* The main dashboard displaying pipeline status, system health (connecting to `localhost:8000/health`), and high-level ingestion statistics.
2. **Dashboard (`/dashboard`)**
   - *File:* `src/app/dashboard/page.js`
   - *Description:* Dedicated dashboard view (likely an expanded version or secondary entry to the root dashboard).
3. **Sign In (`/auth/signin`)**
   - *File:* `src/app/auth/signin/page.js`
   - *Description:* User authentication login page.
4. **Sign Up (`/auth/signup`)**
   - *File:* `src/app/auth/signup/page.js`
   - *Description:* User registration page.
5. **Chat (`/chat`)**
   - *File:* `src/app/chat/page.js`
   - *Description:* The runtime chat interface for interacting with the Expert Persona.
6. **Glass Box (`/glass-box`)**
   - *File:* `src/app/glass-box/page.js`
   - *Description:* Shadow Mode / review interface allowing transparency into the AI's reasoning and execution logic.
7. **Knowledge Hub (`/knowledge-hub`)**
   - *File:* `src/app/knowledge-hub/page.js`
   - *Description:* Interface for document ingestion, Universal Structure Builder, and RAG index management.
8. **Persona (`/persona`)**
   - *File:* `src/app/persona/page.js`
   - *Description:* Interface for configuring, viewing, and manifesting the AI Expert Persona.
9. **Skills (`/skills`)**
   - *File:* `src/app/skills/page.js`
   - *Description:* Management layer for Digital Twin functional skills, including Guardrails and Sandbox environments.

---

## 3. Components
The component architecture is modular, separating layout elements, UI primitives, and domain-specific functionality.

### Layout Components
- **`Sidebar.js`**: Global navigation sidebar managing the active route state and providing navigation links across the app.

### Domain-Specific Components (Skills)
- **`SkillSandbox.js`**: An interactive testing environment for individual skills.
- **`GuardrailEditor.js`**: An interface for defining and editing security/execution boundaries for skills.
- **`ExecutionLogViewer.js`**: Real-time or historical log viewer to trace skill execution.

### UI / Asset Components
- **`SparkleIcons.js`**: Contains custom SVG icons (e.g., `KnowledgeIcon`, `BrainIcon`, `PersonaIcon`, `WarningIcon`) aligned with the application's aesthetic.
- **`DocLogos.js`**: SVG logos and document-related graphical assets.

---

## 4. Frontend Design System
The application employs a **Premium Monochromatic Blue Theme** to evoke trust, clarity, and an advanced technological feel (fitting for a medical/specialist AI twin). It completely avoids generic utility frameworks (like Tailwind) in favor of high-performance Vanilla CSS and inline React styles.

### Core Aesthetic Principles
- **Color Palette:**
  - *Base Backgrounds:* Soft off-whites and cool grays (`#F4F7FB`, `#FFFFFF`).
  - *Primary Accents:* Deep oceanic blue (`#03045E`), bright cyan (`#00B4D8`), teal (`#0077B6`), and soft light blue (`#CAF0F8`).
  - *Status Accents:* Amber (`#F59E0B`) for partial/warnings, Green (`#10B981`) for success, Red (`#EF4444`) for errors/offline.
- **Typography:** Modern, legible sans-serif fonts. The primary font family is **Plus Jakarta Sans**, falling back to `Inter` and system defaults.
- **Layout Methodology:** Extensive use of CSS Flexbox and CSS Grid (e.g., `gridTemplateColumns: 'repeat(4, 1fr)'`) injected via React inline styling.

### Design Variables (`globals.css`)
Key CSS custom properties ensure design consistency:
```css
:root {
  --bg-base: #F4F7FB;
  --bg-surface: #FFFFFF;
  --accent-primary: #0077B6;
  --text-primary: #03045E;
  --text-secondary: #475569;
  --radius-sm: 12px;
  --radius-md: 18px;
  --radius-lg: 24px;
}
```

### Micro-Interactions & Styling Classes
The design feels dynamic and alive through carefully crafted CSS classes:
- **Glassmorphism (`.glass`)**: Translucent backgrounds with `backdrop-filter: blur(16px)` and subtle borders.
- **Glow Effects**: `.glow-teal`, `.glow-blue` utilizing `box-shadow` to create depth and highlight active elements.
- **Animations**:
  - `.fade-up`: Smooth entrance animation shifting elements up (`translateY(16px)` to `0`) while fading in.
  - `.pulse-glow`: Continuous pulsing shadow effect to draw user attention to critical elements.
  - `.blink`: Intermittent opacity animation, often used for live status indicators.
- **Badges**: Reusable pill-shaped indicators (`.badge`, `.badge-blue`, `.badge-amber`, etc.) used heavily in the Pipeline Status trackers.
