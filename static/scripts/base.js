// Debounce helper
function debounce(fn, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
    };
}

fetch('/api/game-titles')
.then(response => response.json())
.then(titles => {
    const input = document.getElementById("search-input");

    const awesomplete = new Awesomplete(input, {
        list: [],  // We'll override filtering
        minChars: 1,
        maxItems: 12,
        autoFirst: true,
        filter: function(text, input) {
            return text.toLowerCase().includes(input.toLowerCase());
        },
        sort: false // Disable sorting if you want to keep original order
    });

    // Debounced input listener
    input.addEventListener("input", debounce(function () {
        const val = this.value.toLowerCase();
        if (val.length > 0) {
            awesomplete.list = titles.filter(title => title.toLowerCase().includes(val));
        } else {
            awesomplete.list = [];
        }
    }, 150)); // 150ms debounce delay

    input.addEventListener("awesomplete-selectcomplete", function(event) {
        const selected = event.text.value;
        window.location.href = `/game/${encodeURIComponent(selected)}`;
    });
})
.catch(err => {
    console.error("Failed to load game titles:", err);
});

function toggleSidebar() {
    const sidebar = document.getElementById("mySidebar");
    if (sidebar.style.display === "block") {
        sidebar.style.display = "none";
    } else {
        sidebar.style.display = "block";
    }
}