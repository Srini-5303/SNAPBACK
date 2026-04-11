---
marp: true
theme: default
paginate: true
html: true
style: |
  :root {
    --color-bg: #0A0A0F;
    --color-accent: #00E5CC;
    --color-text: #F8F8F2;
    --color-muted: #8B8B9E;
    --color-surface: #14141F;
    --color-red: #FF4757;
    --color-yellow: #FFBE0B;
  }
  section {
    background: var(--color-bg);
    color: var(--color-text);
    font-family: 'Segoe UI', sans-serif;
    padding: 56px 72px;
  }
  h1 { color: var(--color-accent); font-size: 2.6rem; margin-bottom: 0.2em; }
  h2 { color: var(--color-accent); font-size: 1.8rem; margin-bottom: 0.4em; }
  h3 { color: var(--color-text); font-size: 1.1rem; font-weight: 600; margin-bottom: 0.2em; }
  p, li { color: #C8C8D8; font-size: 1rem; line-height: 1.7; }
  strong { color: var(--color-accent); }
  .accent { color: var(--color-accent); }
  hr { border-color: #1C1C2E; margin: 1.2em 0; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #14141F; color: var(--color-accent); padding: 10px 16px; text-align: left; font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; }
  td { padding: 10px 16px; border-bottom: 1px solid #1C1C2E; color: #C8C8D8; font-size: 0.95rem; }
  section::after { color: #4A4A6A; font-size: 0.75rem; }
---

<!-- Slide 1: Title -->

# SNAPBACK

### **S**port-specific **N**euromuscular **A**nalysis and **P**ersonalized **B**lueprint for **A**thletic **C**omebac**K**

---

<!-- Slide 2: Problem Statement -->

## The Problem

<br>

Athletes returning to sport after a long break face a silent barrier — **they don't know what they've lost**.

<br>

- Mobility quietly declines during time away from sport
- Jumping straight back into training **dramatically increases injury risk**
- Generic recovery plans ignore individual deficits and sport-specific demands
- There is **no accessible, data-driven tool** to baseline movement before return

<br>

**Most athletes feel ready long before their body actually is.**

---

<!-- Slide 3: How It Works -->

## Three Steps Back to the Game

**① Choose Your Sport**
Select from basketball, football, tennis, golf and more. Each sport has a unique mobility blueprint — the exact joint ranges it demands.

**② Analyse Your Movement**
Stand in front of your camera. Our CV engine tracks 33 body landmarks in real time, measuring range of motion across 8 key joints — elbows, knees, hips and shoulders.

**③ Get Your Plan**
Receive a week-by-week exercise programme targeting _your specific deficits_ — not a generic warm-up, but a precision rehab plan matched to your sport.

---

<!-- Slide 4: The Technology -->

## Real-Time Mobility Analysis

<br>

A single webcam. No wearables. No clinic visit.

<br>

- **MediaPipe** detects 33 skeletal landmarks at 30 fps
- Joint angles computed live — elbow, knee, hip, shoulder (left & right)
- **EMA smoothing** removes jitter; session min/max tracks your true ROM

---

<!-- Slide 5: The Outcome -->

## From Deficit to Sport-Ready

<br>

SNAPBACK turns a 30-second scan into a recovery roadmap:

**The result:** a prioritised, sport-specific exercise plan — delivered instantly.
_Not "get fit". Get back._

---

<!-- Slide 6: Demo Screenshot -->

<img src="assets/cv-screenshot.png" />

---

![h:480 center](assets/demo-screenshot.png)

---

![h:480 center](assets/plan-screenshot.png)

---

<!-- Slide 8: Thank You -->

# Thank You
