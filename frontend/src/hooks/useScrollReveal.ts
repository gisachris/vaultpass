import { useEffect } from 'react';

export function useScrollReveal() {
  useEffect(() => {
    const revealElements = Array.from(document.querySelectorAll<HTMLElement>('.reveal'));

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-active');
            obs.unobserve(entry.target);
          }
        });
      },
      {
        root: null,
        rootMargin: '0px',
        threshold: 0.15,
      },
    );

    revealElements.forEach((element) => observer.observe(element));

    const handleInitialReveal = () => {
      revealElements.forEach((element) => {
        const rect = element.getBoundingClientRect();
        if (rect.top < window.innerHeight) {
          element.classList.add('reveal-active');
        }
      });
    };

    const timeoutId = window.setTimeout(handleInitialReveal, 100);

    return () => {
      window.clearTimeout(timeoutId);
      observer.disconnect();
    };
  }, []);
}
