// Theme toggle logic
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const currentTheme = localStorage.getItem("theme") || "light";
  
    if (currentTheme === "dark") {
      document.body.classList.add("dark");
      themeToggle.textContent = "Switch to Light Theme";
    }
  
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark");
      const isDark = document.body.classList.contains("dark");
      themeToggle.textContent = isDark ? "Switch to Light Theme" : "Switch to Dark Theme";
      localStorage.setItem("theme", isDark ? "dark" : "light");
    });
  });
  