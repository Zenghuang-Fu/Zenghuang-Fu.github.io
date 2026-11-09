document.querySelectorAll(".mobile-nav a").forEach((link) => {
  link.addEventListener("click", () => link.closest("details").removeAttribute("open"));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const menu = document.querySelector(".mobile-nav[open]");
    if (menu) {
      menu.removeAttribute("open");
      menu.querySelector("summary").focus();
    }
  }
});
if ("IntersectionObserver" in window) {
  const links = document.querySelectorAll(".desktop-nav a, .mobile-nav-panel a");
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((link) => {
          if (link.hash === "#" + entry.target.id) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      }
    },
    { rootMargin: "-10% 0px -65% 0px" }
  );
  document.querySelectorAll("main > section[id]").forEach((section) => observer.observe(section));
}
