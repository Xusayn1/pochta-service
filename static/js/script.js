document.addEventListener('DOMContentLoaded', () => {
  const cursor = document.getElementById('cursor');
  const ring = document.getElementById('cursorRing');
  if (cursor && ring) {
    let mouseX = 0;
    let mouseY = 0;
    let ringX = 0;
    let ringY = 0;
    document.addEventListener('mousemove', (event) => {
      mouseX = event.clientX;
      mouseY = event.clientY;
    });
    const animateCursor = () => {
      ringX += (mouseX - ringX) * 0.15;
      ringY += (mouseY - ringY) * 0.15;
      cursor.style.left = `${mouseX}px`;
      cursor.style.top = `${mouseY}px`;
      ring.style.left = `${ringX}px`;
      ring.style.top = `${ringY}px`;
      requestAnimationFrame(animateCursor);
    };
    animateCursor();
    document.querySelectorAll('a, button, .service-card, .price-card').forEach((element) => {
      element.addEventListener('mouseenter', () => {
        cursor.style.transform = 'translate(-50%,-50%) scale(1.8)';
        ring.style.width = '56px';
        ring.style.height = '56px';
        ring.style.opacity = '0.3';
      });
      element.addEventListener('mouseleave', () => {
        cursor.style.transform = 'translate(-50%,-50%) scale(1)';
        ring.style.width = '36px';
        ring.style.height = '36px';
        ring.style.opacity = '0.6';
      });
    });
  }
  const navbar = document.getElementById('navbar');
  if (navbar) {
    const syncNavbar = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', syncNavbar);
    syncNavbar();
  }
  const fadeElements = document.querySelectorAll('.fade-up');
  if (fadeElements.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1 });
    fadeElements.forEach((element) => observer.observe(element));
  }
});
