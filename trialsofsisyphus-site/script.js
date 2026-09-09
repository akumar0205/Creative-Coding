const glow = document.querySelector('.cursor-glow');
window.addEventListener('pointermove', (event) => {
  glow.style.left = `${event.clientX}px`;
  glow.style.top = `${event.clientY}px`;
});

const filters = document.querySelectorAll('.filter');
const projects = document.querySelectorAll('.project');
filters.forEach((filter) => {
  filter.addEventListener('click', () => {
    filters.forEach((item) => item.classList.remove('is-active'));
    filter.classList.add('is-active');
    const type = filter.dataset.filter;
    projects.forEach((project) => {
      project.classList.toggle('is-hidden', type !== 'all' && project.dataset.type !== type);
    });
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.animate(
        [{ opacity: 0, transform: 'translateY(18px)' }, { opacity: 1, transform: 'translateY(0)' }],
        { duration: 650, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards' },
      );
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.08 });
projects.forEach((project) => observer.observe(project));

const lightbox = document.querySelector('.lightbox');
const lightboxImage = document.querySelector('.lightbox-image');
const lightboxMeta = document.querySelector('.lightbox-meta');
const lightboxTitle = document.querySelector('#lightbox-title');
const lightboxClose = document.querySelector('.lightbox-close');

const closeLightbox = () => {
  lightbox.classList.remove('is-open');
  lightbox.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('no-scroll');
};

projects.forEach((project) => {
  project.setAttribute('tabindex', '0');
  project.setAttribute('role', 'button');
  const openLightbox = () => {
    const image = project.querySelector('img');
    const title = project.querySelector('h3');
    const meta = project.querySelector('.project-info span');
    if (!image || !title) return;
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightboxTitle.textContent = title.textContent;
    lightboxMeta.textContent = meta?.textContent || '';
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.classList.add('no-scroll');
    lightboxClose.focus();
  };
  project.addEventListener('click', openLightbox);
  project.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openLightbox();
    }
  });
});

lightboxClose.addEventListener('click', closeLightbox);
lightbox.addEventListener('click', (event) => {
  if (event.target === lightbox) closeLightbox();
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && lightbox.classList.contains('is-open')) closeLightbox();
});
