(function () {
    'use strict';

    // Group buttons show their tab; command buttons show their form.
    function show(buttons, panels, id, attribute) {
        buttons.forEach(function (b) {
            b.classList.toggle('active', b.dataset[attribute] === id);
        });
        panels.forEach(function (p) {
            p.hidden = p.dataset[attribute] !== id;
        });
    }

    var tabButtons = Array.prototype.slice.call(document.querySelectorAll('[data-tab]'));
    var tabs = Array.prototype.slice.call(document.querySelectorAll('.tab'));
    tabButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            show(tabButtons, tabs, button.dataset.tab, 'tab');
        });
    });

    var commandButtons = Array.prototype.slice.call(document.querySelectorAll('[data-command]'));
    var forms = Array.prototype.slice.call(document.querySelectorAll('.command-form'));
    commandButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            show(commandButtons, forms, button.dataset.command, 'command');
        });
    });

    // Open the group requested by other pages, e.g. index.php?tab=tab1
    var requestedTab = new URLSearchParams(window.location.search).get('tab');
    if (requestedTab && document.querySelector('.tab[data-tab="' + requestedTab + '"]')) {
        show(tabButtons, tabs, requestedTab, 'tab');
    }

    // Re-open the command that was just submitted.
    var active = document.body.dataset.active;
    var activeForm = active && document.querySelector('.command-form[data-command="' + active + '"]');
    if (activeForm) {
        show(tabButtons, tabs, activeForm.closest('.tab').dataset.tab, 'tab');
        show(commandButtons, forms, active, 'command');
    }

    // Copy a document's JSON without toggling its dropdown.
    document.addEventListener('click', function (event) {
        var button = event.target.closest('.json-copy');
        if (!button) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        var text = button.dataset.json;
        var done = function () {
            button.textContent = 'Copied!';
            setTimeout(function () {
                button.textContent = 'Copy';
            }, 1500);
        };
        var fail = function () {
            button.textContent = 'Copy failed';
            setTimeout(function () {
                button.textContent = 'Copy';
            }, 1500);
        };
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(done, fail);
        } else {
            fail();
        }
    });

    // Light/dark theme, remembered in localStorage.
    var themeButton = document.getElementById('theme-toggle');
    if (themeButton) {
        var root = document.documentElement;
        themeButton.addEventListener('click', function () {
            root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', root.dataset.theme);
        });
    }
}());
