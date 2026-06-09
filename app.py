@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap');

/* ═══════════════════════════════════════════
   Design Tokens
   ═══════════════════════════════════════════ */
:root {
  /* Brand Colors */
  --brand-yellow: #F5A623;
  --brand-red: #C0392B;
  --brand-red-dark: #96281B;

  /* Surface Colors */
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-card: rgba(30, 30, 30, 0.7);
  --bg-glass: rgba(255, 255, 255, 0.04);

  /* Text Colors */
  --text-primary: #FFFFFF;
  --text-secondary: #B0B0B0;
  --text-muted: #6B6B6B;

  /* Gradients */
  --gradient-hero: linear-gradient(135deg, #0D0D0D 0%, #1A0A00 50%, #0D0D0D 100%);
  --gradient-cta: linear-gradient(135deg, #F5A623 0%, #E8961C 50%, #C0392B 100%);
  --gradient-cta-hover: linear-gradient(135deg, #FFB833 0%, #F5A623 50%, #E74C3C 100%);
  --gradient-glow: radial-gradient(ellipse at center, rgba(245, 166, 35, 0.15) 0%, transparent 70%);

  /* Borders */
  --border-subtle: 1px solid rgba(255, 255, 255, 0.06);
  --border-accent: 1px solid rgba(245, 166, 35, 0.3);

  /* Shadows */
  --shadow-soft: 0 4px 24px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 60px rgba(245, 166, 35, 0.2);
  --shadow-cta: 0 8px 32px rgba(245, 166, 35, 0.3);

  /* Spacing */
  --section-padding: 100px 0;

  /* Radius */
  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;

  /* Transitions */
  --transition-fast: 0.2s ease;
  --transition-smooth: 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --transition-bounce: 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ═══════════════════════════════════════════
   Reset & Base
   ═══════════════════════════════════════════ */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  font-size: 16px;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.7;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

img {
  max-width: 100%;
  display: block;
}

a {
  text-decoration: none;
  color: inherit;
}

/* ═══════════════════════════════════════════
   Utility Classes
   ═══════════════════════════════════════════ */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  text-align: center;
  margin-bottom: 16px;
  line-height: 1.2;
}

.section-subtitle {
  text-align: center;
  color: var(--text-secondary);
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto 60px;
}

.highlight {
  color: var(--brand-yellow);
}

.highlight-red {
  color: var(--brand-red);
}

/* ═══════════════════════════════════════════
   Animations
   ═══════════════════════════════════════════ */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes shimmer {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 20px rgba(245, 166, 35, 0.2); }
  50% { box-shadow: 0 0 40px rgba(245, 166, 35, 0.4); }
}

.animate-on-scroll {
  opacity: 0;
  transform: translateY(40px);
  transition: all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.animate-on-scroll.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ═══════════════════════════════════════════
   Navbar
   ═══════════════════════════════════════════ */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 16px 0;
  background: rgba(13, 13, 13, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: var(--border-subtle);
  transition: var(--transition-smooth);
}

.navbar.scrolled {
  padding: 10px 0;
  background: rgba(13, 13, 13, 0.95);
}

.navbar .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-logo {
  height: 50px;
  width: auto;
  border-radius: var(--radius-sm);
}

.navbar-cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  background: var(--gradient-cta);
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.9rem;
  border-radius: 50px;
  transition: var(--transition-smooth);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.navbar-cta:hover {
  background: var(--gradient-cta-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-cta);
}

/* ═══════════════════════════════════════════
   Hero Section
   ═══════════════════════════════════════════ */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: var(--gradient-hero);
  padding-top: 80px;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 800px;
  height: 800px;
  background: var(--gradient-glow);
  border-radius: 50%;
  pointer-events: none;
  animation: pulse 6s ease-in-out infinite;
}

.hero::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(to top, var(--bg-primary), transparent);
  pointer-events: none;
}

.hero .container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-content {
  animation: fadeInUp 1s ease forwards;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: var(--bg-glass);
  border: var(--border-accent);
  border-radius: 50px;
  font-size: 0.85rem;
  color: var(--brand-yellow);
  font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.hero-badge::before {
  content: '🔥';
}

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 24px;
}

.hero-title span {
  display: block;
  background: var(--gradient-cta);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.15rem;
  color: var(--text-secondary);
  margin-bottom: 36px;
  max-width: 500px;
  line-height: 1.8;
}

.hero-price {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 32px;
}

.hero-price .old-price {
  font-size: 1.2rem;
  color: var(--text-muted);
  text-decoration: line-through;
}

.hero-price .current-price {
  font-size: 2.5rem;
  font-weight: 900;
  color: var(--brand-yellow);
}

.hero-price .current-price small {
  font-size: 1rem;
  font-weight: 600;
}

.hero-cta-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 18px 48px;
  background: var(--gradient-cta);
  color: var(--text-primary);
  font-weight: 800;
  font-size: 1.1rem;
  border-radius: 50px;
  border: none;
  cursor: pointer;
  transition: var(--transition-smooth);
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
  animation: glow 3s ease-in-out infinite;
}

.btn-primary::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: 0.5s;
}

.btn-primary:hover::after {
  left: 100%;
}

.btn-primary:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 40px rgba(245, 166, 35, 0.4);
}

.hero-guarantee {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.hero-guarantee svg {
  width: 16px;
  height: 16px;
  fill: #27AE60;
}

.hero-image-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: fadeIn 1.2s ease 0.3s forwards;
  opacity: 0;
}

.hero-image-wrapper::before {
  content: '';
  position: absolute;
  width: 110%;
  height: 110%;
  background: radial-gradient(circle, rgba(245, 166, 35, 0.1) 0%, transparent 60%);
  border-radius: 50%;
}

.hero-image {
  width: 100%;
  max-width: 480px;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-soft);
  animation: float 6s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

/* ═══════════════════════════════════════════
   Benefits Section
   ═══════════════════════════════════════════ */
.benefits {
  padding: var(--section-padding);
  position: relative;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.benefit-card {
  background: var(--bg-card);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 40px 32px;
  text-align: center;
  transition: var(--transition-smooth);
  position: relative;
  overflow: hidden;
}

.benefit-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-cta);
  transform: scaleX(0);
  transition: var(--transition-smooth);
}

.benefit-card:hover {
  transform: translateY(-8px);
  border-color: rgba(245, 166, 35, 0.2);
  box-shadow: var(--shadow-glow);
}

.benefit-card:hover::before {
  transform: scaleX(1);
}

.benefit-icon {
  font-size: 3rem;
  margin-bottom: 20px;
  display: block;
}

.benefit-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 12px;
}

.benefit-text {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.7;
}

/* ═══════════════════════════════════════════
   What You'll Learn Section
   ═══════════════════════════════════════════ */
.learn {
  padding: var(--section-padding);
  background: var(--bg-secondary);
  position: relative;
}

.learn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  background: var(--gradient-glow);
  border-radius: 50%;
  pointer-events: none;
}

.learn-list {
  max-width: 700px;
  margin: 0 auto;
  list-style: none;
  position: relative;
  z-index: 1;
}

.learn-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 24px;
  background: var(--bg-glass);
  border: var(--border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  transition: var(--transition-smooth);
}

.learn-item:hover {
  border-color: rgba(245, 166, 35, 0.2);
  background: rgba(245, 166, 35, 0.05);
  transform: translateX(8px);
}

.learn-item-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: var(--gradient-cta);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary);
}

.learn-item-content h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.learn-item-content p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* ═══════════════════════════════════════════
   Social Proof / Instagram
   ═══════════════════════════════════════════ */
.social-proof {
  padding: var(--section-padding);
}

.social-card {
  max-width: 600px;
  margin: 0 auto;
  background: var(--bg-card);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 48px;
  text-align: center;
}

.social-card .instagram-handle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--brand-yellow);
  margin-top: 16px;
  transition: var(--transition-smooth);
}

.social-card .instagram-handle:hover {
  transform: scale(1.05);
  color: var(--brand-red);
}

.social-card p {
  color: var(--text-secondary);
  margin-bottom: 8px;
  font-size: 1.05rem;
}

/* ═══════════════════════════════════════════
   Final CTA Section
   ═══════════════════════════════════════════ */
.final-cta {
  padding: 120px 0;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.final-cta::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(245, 166, 35, 0.08) 0%, transparent 60%);
  pointer-events: none;
}

.final-cta .container {
  position: relative;
  z-index: 1;
}

.final-cta-box {
  background: var(--bg-card);
  border: var(--border-accent);
  border-radius: var(--radius-xl);
  padding: 60px 48px;
  max-width: 700px;
  margin: 0 auto;
  backdrop-filter: blur(10px);
}

.final-cta .section-title {
  margin-bottom: 16px;
}

.final-cta-price {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin: 32px 0;
}

.final-cta-price .label {
  font-size: 1rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
}

.final-cta-price .price {
  font-size: 3.5rem;
  font-weight: 900;
  color: var(--brand-yellow);
}

.final-cta-price .price small {
  font-size: 1.2rem;
  font-weight: 600;
}

.final-cta .btn-primary {
  margin-bottom: 16px;
}

.final-cta-features {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 32px;
  flex-wrap: wrap;
}

.final-cta-feature {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.final-cta-feature span {
  color: #27AE60;
  font-size: 1.2rem;
}

/* ═══════════════════════════════════════════
   Footer
   ═══════════════════════════════════════════ */
.footer {
  padding: 40px 0;
  border-top: var(--border-subtle);
  text-align: center;
}

.footer p {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.footer a {
  color: var(--brand-yellow);
  transition: var(--transition-fast);
}

.footer a:hover {
  color: var(--brand-red);
}

/* ═══════════════════════════════════════════
   Responsive
   ═══════════════════════════════════════════ */
@media (max-width: 968px) {
  .hero .container {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .hero-content {
    order: 1;
  }

  .hero-image-wrapper {
    order: 0;
  }

  .hero-description {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-cta-group {
    align-items: center;
  }

  .hero-price {
    justify-content: center;
  }

  .benefits-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin: 0 auto;
  }

  .hero-image {
    max-width: 350px;
  }
}

@media (max-width: 600px) {
  :root {
    --section-padding: 60px 0;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-price .current-price {
    font-size: 2rem;
  }

  .btn-primary {
    padding: 16px 36px;
    font-size: 1rem;
  }

  .final-cta-box {
    padding: 40px 24px;
  }

  .final-cta-price .price {
    font-size: 2.5rem;
  }

  .final-cta-features {
    gap: 16px;
  }

  .learn-item {
    flex-direction: column;
    text-align: center;
    align-items: center;
  }
}
