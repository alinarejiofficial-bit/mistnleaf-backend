(function () {
  const header = document.getElementById("site-header");
  const menuBtn = document.getElementById("mobile-menu-btn");
  const mobileNav = document.getElementById("mobile-nav");

  if (header) {
    window.addEventListener(
      "scroll",
      function () {
        if (window.scrollY > 12) {
          header.classList.add("is-scrolled");
        } else {
          header.classList.remove("is-scrolled");
        }
      },
      { passive: true }
    );
  }

  if (menuBtn && mobileNav) {
    menuBtn.addEventListener("click", function () {
      const willOpen = mobileNav.hasAttribute("hidden");
      if (willOpen) {
        mobileNav.removeAttribute("hidden");
      } else {
        mobileNav.setAttribute("hidden", "");
      }
      menuBtn.setAttribute("aria-expanded", willOpen ? "true" : "false");
      menuBtn.textContent = willOpen ? "Close" : "Menu";
    });
  }
})();
