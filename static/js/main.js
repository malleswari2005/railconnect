// RailConnect Modern Client Script
document.addEventListener('DOMContentLoaded', function () {
  // Common Station Alternate Spellings & Aliases
  const STATION_ALIASES = {
    'VIJAYWADA': 'BZA',
    'VIJAYAWADA': 'BZA',
    'BEZWADA': 'BZA',
    'TIRUPATHI': 'TPTY',
    'TIRUPATI': 'TPTY',
    'VIZAG': 'VSKP',
    'VISAKHAPATNAM': 'VSKP',
    'VISHAKHAPATNAM': 'VSKP',
    'VISAKHA': 'VSKP',
    'BANGLORE': 'SBC',
    'BANGALORE': 'SBC',
    'BENGALURU': 'SBC',
    'CHENNAI': 'MAS',
    'MADRAS': 'MAS',
    'HYDERABAD': 'SC',
    'SECUNDERABAD': 'SC',
    'KURNOOL': 'KRNT',
    'CUDDAPAH': 'HX',
    'KADAPA': 'HX'
  };

  // Station dataset cache
  let stationCache = [];

  // Pre-fetch all stations for fast client-side filtering and partial matching
  fetch('/trains/api/stations/?all=1')
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (Array.isArray(data)) {
        stationCache = data;
      }
    })
    .catch(function () {});

  // Station Code Resolver
  function resolveStationCode(rawText) {
    if (!rawText) return '';
    const trimmed = rawText.trim();
    if (!trimmed) return '';

    // 1. Check for (CODE) pattern e.g. "Vijayawada Jn (BZA)"
    const codeMatch = trimmed.match(/\(([A-Za-z0-9]{2,10})\)/);
    if (codeMatch) {
      return codeMatch[1].toUpperCase();
    }

    const upper = trimmed.toUpperCase();

    // 2. Exact code match in cache or uppercase short string
    const exactCode = stationCache.find(function (s) { return s.code.toUpperCase() === upper; });
    if (exactCode) return exactCode.code;

    // 3. Alias map lookup (direct or alphanumeric normalized)
    const cleanKey = upper.replace(/[^A-Z0-9]/g, '');
    if (STATION_ALIASES[cleanKey]) {
      return STATION_ALIASES[cleanKey];
    }
    const words = upper.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
      if (STATION_ALIASES[words[i]]) {
        return STATION_ALIASES[words[i]];
      }
    }

    // 4. Exact name or city match in cache
    const exactNameOrCity = stationCache.find(function (s) {
      return s.name.toUpperCase() === upper || s.city.toUpperCase() === upper;
    });
    if (exactNameOrCity) return exactNameOrCity.code;

    // 5. Starts-with match in name, city, or code
    const prefixMatch = stationCache.find(function (s) {
      return s.code.toUpperCase().startsWith(upper) ||
             s.name.toUpperCase().startsWith(upper) ||
             s.city.toUpperCase().startsWith(upper);
    });
    if (prefixMatch) return prefixMatch.code;

    // 6. Substring match in name or city
    const subMatch = stationCache.find(function (s) {
      return s.name.toUpperCase().includes(upper) || s.city.toUpperCase().includes(upper);
    });
    if (subMatch) return subMatch.code;

    // 7. Suffix-stripped match ("Jn", "Junction", "City", "Central")
    const stem = upper.replace(/\b(JN|JUNCTION|CITY|CANTT|CENTRAL|ROAD|TERMINUS)\b/g, '').trim();
    if (stem && stem !== upper) {
      if (STATION_ALIASES[stem]) return STATION_ALIASES[stem];
      const stemMatch = stationCache.find(function (s) {
        return s.name.toUpperCase().includes(stem) || s.city.toUpperCase().includes(stem);
      });
      if (stemMatch) return stemMatch.code;
    }

    // Fallback: return raw input for server-side suggestion handling
    return trimmed;
  }

  // Station Autocomplete Initialization
  const autocompleteInputs = document.querySelectorAll('.rc-station-autocomplete');
  autocompleteInputs.forEach(function (input) {
    const hiddenId = input.getAttribute('data-target-hidden');
    const menuId = input.getAttribute('data-menu');
    const hiddenInput = hiddenId ? document.getElementById(hiddenId) : null;
    const menu = menuId ? document.getElementById(menuId) : null;

    if (!hiddenInput || !menu) return;

    let activeIndex = -1;
    let currentItems = [];

    function renderDropdown(items) {
      menu.innerHTML = '';
      currentItems = items;
      activeIndex = -1;

      if (!items || items.length === 0) {
        menu.classList.remove('show');
        return;
      }

      items.forEach(function (st, idx) {
        const itemEl = document.createElement('div');
        itemEl.className = 'rc-autocomplete-item';
        itemEl.setAttribute('data-index', idx);
        itemEl.innerHTML = `
          <div class="station-info">
            <span class="station-name">${st.name}</span>
            <span class="station-city">${st.city}</span>
          </div>
          <span class="station-code-badge">${st.code}</span>
        `;

        itemEl.addEventListener('mousedown', function (e) {
          e.preventDefault(); // Prevent input blur before click finishes
          selectStation(st);
        });

        menu.appendChild(itemEl);
      });

      menu.classList.add('show');
    }

    function selectStation(st) {
      input.value = `${st.name} (${st.code})`;
      hiddenInput.value = st.code;
      menu.classList.remove('show');
      currentItems = [];
      activeIndex = -1;
    }

    function filterStations(term) {
      const q = term.trim().toUpperCase();
      if (!q) {
        renderDropdown(stationCache.slice(0, 10));
        return;
      }

      const matchingCodes = new Set();
      for (const [alias, code] of Object.entries(STATION_ALIASES)) {
        if (alias.includes(q) || q.includes(alias)) {
          matchingCodes.add(code);
        }
      }

      const filtered = stationCache.filter(function (s) {
        return s.code.toUpperCase().includes(q) ||
               s.name.toUpperCase().includes(q) ||
               s.city.toUpperCase().includes(q) ||
               matchingCodes.has(s.code);
      }).slice(0, 10);

      if (filtered.length > 0) {
        renderDropdown(filtered);
      } else {
        // Fallback to fetch API if cache is not yet ready
        fetch(`/trains/api/stations/?term=${encodeURIComponent(term)}`)
          .then(function (res) { return res.json(); })
          .then(function (data) {
            renderDropdown(data.slice(0, 10));
          })
          .catch(function () {
            menu.classList.remove('show');
          });
      }
    }

    // Input events
    input.addEventListener('focus', function () {
      filterStations(input.value);
    });

    input.addEventListener('input', function () {
      filterStations(input.value);
      // Auto-sync hidden input on typing
      hiddenInput.value = resolveStationCode(input.value);
    });

    input.addEventListener('blur', function () {
      setTimeout(function () {
        menu.classList.remove('show');
      }, 200);

      // On blur, resolve to station code
      if (input.value.trim()) {
        const resolved = resolveStationCode(input.value);
        if (resolved) {
          hiddenInput.value = resolved;
        }
      }
    });

    // Keyboard navigation
    input.addEventListener('keydown', function (e) {
      if (!menu.classList.contains('show') || currentItems.length === 0) return;

      const items = menu.querySelectorAll('.rc-autocomplete-item');

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        updateActiveItem(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        updateActiveItem(items);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeIndex >= 0 && activeIndex < currentItems.length) {
          selectStation(currentItems[activeIndex]);
        } else if (currentItems.length > 0) {
          selectStation(currentItems[0]);
        }
      } else if (e.key === 'Escape') {
        menu.classList.remove('show');
      }
    });

    function updateActiveItem(items) {
      items.forEach(function (el, idx) {
        if (idx === activeIndex) {
          el.classList.add('active');
          el.scrollIntoView({ block: 'nearest' });
        } else {
          el.classList.remove('active');
        }
      });
    }
  });

  // Ensure submitted value is ALWAYS the station code even on partial typing
  const searchForms = document.querySelectorAll('.rc-search-form');
  searchForms.forEach(function (form) {
    form.addEventListener('submit', function () {
      const formInputs = form.querySelectorAll('.rc-station-autocomplete');
      formInputs.forEach(function (inp) {
        const targetHiddenId = inp.getAttribute('data-target-hidden');
        if (targetHiddenId) {
          const hiddenEl = document.getElementById(targetHiddenId);
          if (hiddenEl && inp.value.trim()) {
            const resolved = resolveStationCode(inp.value);
            hiddenEl.value = resolved || inp.value.trim();
          }
        }
      });
    });
  });

  // Close menus on outside click
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.rc-autocomplete-wrapper')) {
      document.querySelectorAll('.rc-autocomplete-menu').forEach(function (m) {
        m.classList.remove('show');
      });
    }
  });

  // 1. Station Swap Button Handler
  const swapBtn = document.getElementById('rcSwapStationsBtn');
  if (swapBtn) {
    swapBtn.addEventListener('click', function () {
      const fromInput = document.getElementById('fromStationInput') || document.getElementById('fromStation');
      const toInput = document.getElementById('toStationInput') || document.getElementById('toStation');
      const fromHidden = document.getElementById('fromStation');
      const toHidden = document.getElementById('toStation');

      if (fromInput && toInput) {
        const tempText = fromInput.value;
        fromInput.value = toInput.value;
        toInput.value = tempText;

        if (fromHidden && toHidden) {
          const tempCode = fromHidden.value;
          fromHidden.value = toHidden.value;
          toHidden.value = tempCode;
        }

        // Smooth rotation animation
        swapBtn.style.transition = 'transform 0.3s ease';
        swapBtn.style.transform = 'rotate(180deg)';
        setTimeout(function () {
          swapBtn.style.transform = 'rotate(0deg)';
        }, 300);
      }
    });
  }

  // 2. Prevent Multiple Form Submissions with Loading Spinner
  const forms = document.querySelectorAll('form.prevent-double-submit');
  forms.forEach(function (form) {
    form.addEventListener('submit', function () {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';
      }
    });
  });

  // 3. Auto-Dismiss Alert Toasts after 6 seconds
  const toastAlerts = document.querySelectorAll('.rc-toast:not(.rc-toast-permanent)');
  toastAlerts.forEach(function (toast) {
    setTimeout(function () {
      toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(function () { toast.remove(); }, 400);
    }, 6000);
  });

  // 4. Initialize Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (el) {
    return new bootstrap.Tooltip(el);
  });
});
