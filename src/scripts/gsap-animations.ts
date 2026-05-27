import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// ─── MOUSE PARALLAX (Hero) ───────────────────────────────────────────────────
const heroWrap = document.querySelector<HTMLElement>('.hero-chat-wrap');
const tag1 = document.querySelector<HTMLElement>('.float-tag-1');
const tag2 = document.querySelector<HTMLElement>('.float-tag-2');
const orb1 = document.querySelector<HTMLElement>('.orb-1');
const orb2 = document.querySelector<HTMLElement>('.orb-2');

if (heroWrap) {
  document.addEventListener('mousemove', (e) => {
    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;
    const dx = (e.clientX - cx) / cx; // -1 → 1
    const dy = (e.clientY - cy) / cy;

    gsap.to(heroWrap, {
      rotateY: dx * 6,
      rotateX: -dy * 4,
      duration: 0.9,
      ease: 'power2.out',
    });

    if (tag1) gsap.to(tag1, { x: dx * -14, y: dy * -10, duration: 1.1, ease: 'power2.out' });
    if (tag2) gsap.to(tag2, { x: dx * 18,  y: dy * 12,  duration: 1.3, ease: 'power2.out' });
    if (orb1) gsap.to(orb1, { x: dx * 30,  y: dy * 20,  duration: 1.8, ease: 'power1.out' });
    if (orb2) gsap.to(orb2, { x: dx * -20, y: dy * -14, duration: 2.0, ease: 'power1.out' });
  }, { passive: true });

  // Reset on mouse leave
  document.addEventListener('mouseleave', () => {
    gsap.to([heroWrap, tag1, tag2, orb1, orb2], {
      rotateY: 0, rotateX: 0, x: 0, y: 0,
      duration: 1.2, ease: 'power2.out'
    });
  });
}

// ─── HERO TEXT ENTRANCE ──────────────────────────────────────────────────────
const heroCopy = document.querySelector('.hero-copy');
const heroVisual = document.querySelector('.hero-visual');

if (heroCopy) {
  gsap.from(heroCopy, {
    opacity: 0, y: 40, duration: 1, ease: 'power3.out', delay: 0.1
  });
}
if (heroVisual && heroWrap) {
  gsap.from(heroWrap, {
    opacity: 0, y: 60, scale: 0.95, duration: 1.1, ease: 'power3.out', delay: 0.35
  });
}

// ─── SCROLL REVEALS — STAGGERED BATCH ───────────────────────────────────────
// Section headers
ScrollTrigger.batch('.pain-header, .pricing-header, .how-header, .testimonials-header, .proof-left', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 36, duration: 0.85, ease: 'power3.out', stagger: 0.12
  }),
  start: 'top 88%',
  once: true,
});

// Pain cards
ScrollTrigger.batch('.pain-card', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 48, duration: 0.75, ease: 'power3.out', stagger: 0.14
  }),
  start: 'top 88%',
  once: true,
});

// ROI items
ScrollTrigger.batch('.roi-item', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 44, duration: 0.75, ease: 'power3.out', stagger: 0.14
  }),
  start: 'top 88%',
  once: true,
});

// Pricing plans
ScrollTrigger.batch('.plan', {
  onEnter: (els) => gsap.fromTo(els,
    { opacity: 0, y: 50, scale: 0.97 },
    { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out', stagger: 0.15, clearProps: 'all' }
  ),
  start: 'top 92%',
  once: true,
});

// Steps (how it works)
ScrollTrigger.batch('.step', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, x: -40, duration: 0.8, ease: 'power3.out', stagger: 0.18
  }),
  start: 'top 88%',
  once: true,
});

// Testimonials
ScrollTrigger.batch('.testimonial-card', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 40, scale: 0.96, duration: 0.75, ease: 'power3.out', stagger: 0.12
  }),
  start: 'top 90%',
  once: true,
});

// Metric cards
ScrollTrigger.batch('.metric-card', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 36, duration: 0.7, ease: 'power3.out', stagger: 0.13
  }),
  start: 'top 88%',
  once: true,
});

// ROI math block
ScrollTrigger.batch('.roi-math', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 30, scale: 0.98, duration: 0.8, ease: 'power3.out'
  }),
  start: 'top 88%',
  once: true,
});

// ─── EYEBROW LABELS ──────────────────────────────────────────────────────────
ScrollTrigger.batch('.eyebrow', {
  onEnter: (els) => gsap.from(els, {
    opacity: 0, y: 14, duration: 0.55, ease: 'power2.out', stagger: 0.08
  }),
  start: 'top 90%',
  once: true,
});

// ─── SCROLL PROGRESS INDICATOR (optional UX polish) ─────────────────────────
const progressBar = document.createElement('div');
progressBar.style.cssText = 'position:fixed;top:0;left:0;height:2px;background:var(--nx-accent,#6c63ff);z-index:9999;width:0;pointer-events:none;';
document.body.appendChild(progressBar);

ScrollTrigger.create({
  start: 0,
  end: 'max',
  onUpdate: (self) => {
    progressBar.style.width = (self.progress * 100) + '%';
  }
});
