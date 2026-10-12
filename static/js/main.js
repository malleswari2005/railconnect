// RailConnect Modern Client Script
document.addEventListener('DOMContentLoaded', function () {
  // 1. Station Swap Button Handler
  const swapBtn = document.getElementById('rcSwapStationsBtn');
  if (swapBtn) {
    swapBtn.addEventListener('click', function () {
      const fromInput = document.getElementById('fromStation');
      const toInput = document.getElementById('toStation');
      if (fromInput && toInput) {
        const temp = fromInput.value;
        fromInput.value = toInput.value;
        toInput.value = temp;

        // Smooth rotation animation
        swapBtn.style.transition = 'transform 0.3s ease';
        swapBtn.style.transform = 'rotate(180deg)';
        setTimeout(() => {
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
        const originalText = submitBtn.innerText;
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
      setTimeout(() => toast.remove(), 400);
    }, 6000);
  });

  // 4. Initialize Tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (el) {
    return new bootstrap.Tooltip(el);
  });
});
