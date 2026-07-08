document.addEventListener("DOMContentLoaded", () => {
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    revealEls.forEach(el => observer.observe(el));
  }

  const navbar = document.getElementById("navbar");
  if (navbar) {
    window.addEventListener("scroll", () => {
      navbar.classList.toggle("scrolled", window.scrollY > 60);
    });
  }

  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-link");

  if (sections.length && navLinks.length) {
    const linkObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach(link => {
            link.classList.toggle("active", link.getAttribute("href") === `#${id}`);
          });
        }
      });
    }, { threshold: 0.4 });

    sections.forEach(s => linkObserver.observe(s));
  }

  const menuBtn = document.getElementById("menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });

    mobileMenu.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => mobileMenu.classList.add("hidden"));
    });
  }

  window.openLightbox = (url, alt) => {
    const lb = document.getElementById("lightbox");
    const img = document.getElementById("lightbox-img");
    if (!lb || !img) return;
    img.src = url;
    img.alt = alt;
    lb.classList.remove("hidden");
    lb.classList.add("open");
    document.body.style.overflow = "hidden";
  };

  window.closeLightbox = () => {
    const lb = document.getElementById("lightbox");
    if (!lb) return;
    lb.classList.add("hidden");
    lb.classList.remove("open");
    document.body.style.overflow = "";
  };

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeLightbox();
  });

  window.filterMaquinas = (cat) => {
    const items = document.querySelectorAll(".maquina-item");
    const tabs = document.querySelectorAll(".maquina-tab");

    tabs.forEach(tab => {
      const isActive = tab.id === `tab-${cat}`;
      tab.classList.toggle("bg-gym-red", isActive);
      tab.classList.toggle("border-gym-red", isActive);
      tab.classList.toggle("text-white", isActive);
      tab.classList.toggle("border-white/20", !isActive);
      tab.classList.toggle("text-white/60", !isActive);
    });

    items.forEach(item => {
      const show = cat === "todas" || item.dataset.cat === cat;
      item.style.transition = "opacity 0.3s ease, transform 0.3s ease";

      if (show) {
        item.style.display = "";
        setTimeout(() => {
          item.style.opacity = "1";
          item.style.transform = "translateY(0)";
        }, 10);
      } else {
        item.style.opacity = "0";
        item.style.transform = "translateY(10px)";
        setTimeout(() => {
          item.style.display = "none";
        }, 300);
      }
    });
  };

  if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
    const heroImage = document.querySelector("#hero img");
    if (heroImage) {
      gsap.to(heroImage, {
        yPercent: 20,
        ease: "none",
        scrollTrigger: {
          trigger: "#hero",
          start: "top top",
          end: "bottom top",
          scrub: true
        }
      });
    }
  }
});