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

    // Re-open the command that was just submitted.
    var active = document.body.dataset.active;
    var activeForm = active && document.querySelector('.command-form[data-command="' + active + '"]');
    if (activeForm) {
        show(tabButtons, tabs, activeForm.closest('.tab').dataset.tab, 'tab');
        show(commandButtons, forms, active, 'command');
    }
}());
