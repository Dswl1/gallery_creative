document.addEventListener("DOMContentLoaded", () => {

  /* SECTION REVEAL */
  const sections = document.querySelectorAll(".reveal");

  const sectionObserver = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("reveal-show");
          sectionObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  sections.forEach(el => sectionObserver.observe(el));

  /* ITEM STAGGER */
  const items = document.querySelectorAll(".reveal-item");

  const itemObserver = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("item-show");
          itemObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );

  // ambil per section
  document.querySelectorAll(".reveal").forEach(section => {
    const items = section.querySelectorAll(".reveal-item");

    items.forEach((el, i) => {
      el.style.transitionDelay = `${i * 80}ms`; // lebih cepet & smooth
      itemObserver.observe(el);
    });
  });


});
