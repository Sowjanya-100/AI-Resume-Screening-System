document.addEventListener("DOMContentLoaded", function () {

    const button = document.getElementById("theme-toggle");

    function applyTheme(theme) {

        if (theme === "dark") {
            document.documentElement.classList.add("dark-theme");
            document.body.classList.add("dark-theme");

            if (button) {
                button.textContent = "☀️ Light";
                button.title = "Switch to light theme";
            }

        } else {
            document.documentElement.classList.remove("dark-theme");
            document.body.classList.remove("dark-theme");

            if (button) {
                button.textContent = "🌙 Dark";
                button.title = "Switch to dark theme";
            }
        }
    }

    // Get previously selected theme
    const savedTheme = localStorage.getItem("theme") || "light";

    applyTheme(savedTheme);

    // Theme button
    if (button) {

        button.addEventListener("click", function () {

            const currentTheme =
                document.body.classList.contains("dark-theme")
                    ? "dark"
                    : "light";

            const newTheme =
                currentTheme === "dark"
                    ? "light"
                    : "dark";

            localStorage.setItem("theme", newTheme);

            applyTheme(newTheme);
        });
    }

});