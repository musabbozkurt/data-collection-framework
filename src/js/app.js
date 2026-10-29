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

    // Command forms: pick an existing database/collection or choose "new" to type a name; dates open the calendar
    var NEW_CHOICE = '__new__';

    function syncPicker(select, dbInput) {
        var input = select.nextElementSibling;
        var isCollection = select.dataset.pick === 'collection';
        var db = dbInput ? dbInput.value : '';
        Array.prototype.forEach.call(select.options, function (option) {
            var show = option.value === NEW_CHOICE || !isCollection || option.dataset.db === db;
            option.hidden = option.disabled = !show;
        });
        if (select.selectedOptions[0].disabled) {
            select.value = NEW_CHOICE;
        }
        var isNew = select.value === NEW_CHOICE;
        if (!isNew) {
            input.value = select.value;
        }
        input.hidden = !isNew;
    }

    function chooseInitial(select) {
        var input = select.nextElementSibling;
        var exists = Array.prototype.some.call(select.options, function (option) {
            return option.value === input.value && option.value !== NEW_CHOICE;
        });
        if (input.value !== '' && exists) {
            select.value = input.value;
        } else if (input.value !== '') {
            select.value = NEW_CHOICE;
        } else if (select.options.length > 1) {
            select.selectedIndex = 0;
        }
    }

    function firstCollectionOf(select, db) {
        var match = Array.prototype.find.call(select.options, function (option) {
            return option.dataset.db === db;
        });
        return match ? match.value : NEW_CHOICE;
    }

    function initPickers(form) {
        var dbInput = form.querySelector('input[name="database"]');
        var pickers = Array.prototype.slice.call(form.querySelectorAll('select[data-pick]'));
        var collections = pickers.filter(function (picker) {
            return picker.dataset.pick === 'collection';
        });
        pickers.forEach(function (select) {
            chooseInitial(select);
            select.addEventListener('change', function () {
                if (select.value === NEW_CHOICE) {
                    select.nextElementSibling.value = '';
                    select.nextElementSibling.focus();
                }
                syncPicker(select, dbInput);
                if (select.dataset.pick === 'database') {
                    collections.forEach(function (collection) {
                        collection.value = firstCollectionOf(collection, dbInput?.value);
                        if (collection.value === NEW_CHOICE) {
                            collection.nextElementSibling.value = '';
                        }
                        syncPicker(collection, dbInput);
                    });
                }
            });
        });
        pickers.forEach(function (select) {
            if (select.dataset.pick === 'collection' && select.nextElementSibling.value === '') {
                select.value = firstCollectionOf(select, dbInput?.value);
            }
            syncPicker(select, dbInput);
        });
    }

    function initCalendar(field) {
        if (field.value === '') {
            var later = new Date(Date.now() + 3600000);
            later.setMinutes(later.getMinutes() - later.getTimezoneOffset());
            field.value = later.toISOString().slice(0, 16);
        }
        field.addEventListener('click', function () {
            if (field.showPicker) {
                try {
                    field.showPicker();
                } catch (error) {
                    // the browser only opens it on a direct user action
                }
            }
        });
    }

    forms.forEach(function (form) {
        initPickers(form);
        form.querySelectorAll('input[type="datetime-local"]').forEach(initCalendar);
    });

    // Store Data: collections follow the database; "new" choices reveal a text field
    var storeDb = document.querySelector('[data-store-db]');
    var storeCollection = document.querySelector('[data-store-collection]');
    if (storeDb && storeCollection) {
        var newDb = document.querySelector('[data-store-new-db]');
        var newCollection = document.querySelector('[data-store-new-collection]');
        var syncStore = function () {
            var isNewDb = storeDb.value === 'new';
            var first = null;
            Array.prototype.forEach.call(storeCollection.options, function (option) {
                var match = option.value === 'new' || (!isNewDb && option.dataset.db === storeDb.value);
                option.hidden = option.disabled = !match;
                first = first || (match ? option : null);
            });
            if (isNewDb || storeCollection.selectedOptions[0].disabled) {
                (isNewDb ? storeCollection.querySelector('option[value="new"]') : first).selected = true;
            }
            newDb.hidden = !isNewDb;
            newDb.required = isNewDb;
            newCollection.hidden = storeCollection.value !== 'new';
            newCollection.required = storeCollection.value === 'new';
        };
        storeDb.addEventListener('change', syncStore);
        storeCollection.addEventListener('change', syncStore);
        syncStore();
    }

    // Analytics / Cross Validation: the collection list follows the chosen database
    var sourceDb = document.querySelector('[data-source-db]');
    var sourceCollection = document.querySelector('[data-source-collection]');
    if (sourceDb && sourceCollection) {
        var syncCollections = function () {
            var firstMatch = null;
            Array.prototype.forEach.call(sourceCollection.options, function (option) {
                var match = option.dataset.db === sourceDb.value;
                option.hidden = option.disabled = !match;
                firstMatch = firstMatch || (match ? option : null);
            });
            var current = sourceCollection.selectedOptions[0];
            if (firstMatch && current?.disabled !== false) {
                firstMatch.selected = true;
            }
        };
        sourceDb.addEventListener('change', syncCollections);
        syncCollections();
        // Analytics / Cross Validation / Terms: reload so the lists of analyses and fields match the newly selected collection
        if (sourceDb.form?.dataset.refresh !== undefined) {
            [sourceDb, sourceCollection].forEach(function (select) {
                select.addEventListener('change', function () {
                    // a refresh only reloads the lists; it must not start the run
                    sourceDb.form.querySelectorAll('[data-run-only]').forEach(function (field) {
                        field.disabled = true;
                    });
                    sourceDb.form.submit();
                });
            });
        }
    }

    // Store Data: "select all" for the file list
    var storeAll = document.getElementById('store-all');
    if (storeAll) {
        var fileChecks = Array.prototype.slice.call(document.querySelectorAll('.file-check'));
        storeAll.addEventListener('change', function () {
            fileChecks.forEach(function (c) {
                c.checked = storeAll.checked;
            });
        });
    }

    // Discover Profiles: "select all" and a live count, limited to the per-run maximum
    var selectAll = document.getElementById('select-all');
    var checks = Array.prototype.slice.call(document.querySelectorAll('.profile-check'));
    if (selectAll && checks.length) {
        var LIMIT = 5;
        var counter = document.getElementById('selected-count');
        var refresh = function () {
            var count = checks.filter(function (c) {
                return c.checked;
            }).length;
            counter.textContent = count + ' selected' + (count > LIMIT ? ' (max ' + LIMIT + ')' : '');
        };
        selectAll.addEventListener('change', function () {
            checks.forEach(function (c, i) {
                c.checked = selectAll.checked && i < LIMIT;
            });
            refresh();
        });
        checks.forEach(function (c) {
            c.addEventListener('change', refresh);
        });
    }
}());
