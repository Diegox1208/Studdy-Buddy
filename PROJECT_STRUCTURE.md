# Study Buddy Interface Project

## Overview
An educational platform with two distinct interfaces designed to track student progress and foster autonomous learning.

---

## 1. PROFESSOR INTERFACE: "The Coach's Dashboard"

### Goal
- Reduce training time and protocol complexity
- Act as a Diagnostic System prioritizing who needs help and why

### A. Main Screen: The "Triage" Feed
Dynamic feed using Traffic Light System:

#### 🔴 Red Alert (Wheel Spinning)
- **Trigger**: Student tried same topic 5+ times with high help, no progress
- **Display**: "Juan has tried 'Fractions' 5 times with high help and is not progressing."
- **Action Button**: "Suggest Break" or "Assign Foundational Review"

#### 🟡 Yellow Alert (Impulsivity)
- **Trigger**: Student answering in <1 second (Gaming the System)
- **Display**: "Sofia is answering in <1 second (Gaming the System)."
- **Action**: System auto-pauses session + "Send Encouragement Message"

#### 🟢 Green Notification (Flow)
- **Trigger**: Student achieves Fluency (Speed + Accuracy)
- **Display**: "Pedro has achieved Fluency in Algebra."
- **Action Button**: "Send High Performance Badge"

### B. Student Profile: Visualizing the "Invisible"

#### 1. Independence Curve (Scaffolding Fading)
- **Type**: Stacked Area Chart over time
- **Bottom Layer**: Student Effort (Solid Blue)
- **Top Layer**: AI/Teacher Help (Translucent Grey)
- **Goal**: Grey layer thins, Blue layer thickens (visual autonomy)

#### 2. Cognitive Style Tags (Mental Chronometry)
- Don't show raw latency (e.g., "300ms")
- Show interpretive tags:
  - ✅ **"Reflective"** (Good)
  - ⚠️ **"Impulsive"** (Too fast)
  - 🐌 **"Anxious"** (Too slow)

#### 3. Grit Radar (RESA)
- **Type**: Radar Chart
- **Axes**:
  - Resilience (returning after error)
  - Endurance (focus time)
  - Confidence Calibration

### C. Natural Language Generation (NLG)
- **Purpose**: Minimize training needed
- **Location**: Top of every graph
- **Example**: "Juan is answering faster (Fluency up), but he is asking for help too early. He needs to build more autonomy."

---

## 2. STUDENT INTERFACE (Ages 12-16): "The Athlete's HUD"

### Target Aesthetic
Video Game HUD or Sports Tracker (Strava/Nike Run Club style)

### A. Progress Section: Gamified Attributes

#### Brain Speed (Fluency)
- **Visual**: Progress bar
- **Fills up**: Correct + faster answers

#### XP Level (Autonomy)
- **Earn XP for**:
  - Correct answers
  - Using less help (scaffolding fading)

#### Agency Pie Chart
- **Sections**: "Assigned Tasks" vs "Chosen Tasks"
- **Challenge**: Grow the "Chosen" slice

#### Streak
- **Visual**: Flame icon 🔥
- **Lights up**: For Resilience (returning to failed problems)

### B. The "Locker" (Mailbox & Organization)

#### Visual
- Digital locker with drag & drop

#### Features
- **Camera Button**: Snap photos of Syllabus/Grades/Calendar
- **Smart Upload**: OCR scans Syllabus
- **Automation**: Auto-populates "Events" section

### C. Incoming Events: "The Timeline"

#### Visual
- Horizontal scrollable timeline (Gantt style)

#### Elements
- **"Boss Battles"**: Exams
- **"Training Sessions"**: Classes
- **Readiness Battery**: Shows preparedness based on recent practice

### D. The "Wonder Wall" (Curiosity)

#### Purpose
- Validate curiosity separate from mandatory work
- Pin interesting questions/topics not on tests

---

## 3. AI CHATBOX: "Buddy Bot"

### Design
- **Location**: Overlay bubble accessible during homework
- **Principle**: Intuitive but Strict on scaffolding

### Behavior: 6 Levels of Intervention

#### Example Interaction
**Student asks**: "What is the answer?"

**Buddy Bot Response**: 
"I can't give you the answer yet. Let's check your strategy. Have you drawn a diagram?" (Level 2 Support)

#### Confidence Check
Before revealing hint:
- **Prompt**: "How sure are you?"
- **Options**: Low / Medium / High

---

## Technical Architecture

### Frontend Stack (Recommended)
- HTML5 + CSS3 (Tailwind CSS for rapid styling)
- JavaScript (Vanilla or React)
- Chart.js / D3.js for visualizations
- Drag & Drop API for Locker

### Backend Stack
- Python (Flask/FastAPI)
- PostgreSQL for data storage
- OpenAI API for NLG summaries
- Tesseract OCR for document scanning

### Key Data Points to Track
1. Response Time (latency)
2. Help Request Frequency
3. Accuracy Rate
4. Task Completion Time
5. Scaffolding Level Used
6. Student-Initiated vs Assigned Tasks
7. Return to Failed Problems (Resilience)
8. Confidence Ratings

---

## Implementation Priority

### Phase 1: Core Professor Dashboard
1. Triage Feed with Traffic Light alerts
2. Basic Student Profile with Independence Curve
3. NLG summary generation

### Phase 2: Student Interface MVP
1. Gamified Progress Section
2. Basic Timeline view
3. Wonder Wall

### Phase 3: Advanced Features
1. Locker with OCR
2. Full Buddy Bot integration
3. Grit Radar visualization
4. Real-time notifications

### Phase 4: Refinement
1. Mobile responsive design
2. Performance optimization
3. A/B testing different UI elements
4. Accessibility compliance
