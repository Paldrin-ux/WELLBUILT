/* ═══════════════════════════════════════════
   WELL-BUILT V2 – ADMIN JS
═══════════════════════════════════════════ */

// ── DATE ──────────────────────────────────
const dateEl = document.getElementById('adminDate');
if (dateEl) {
  const now = new Date();
  dateEl.textContent = now.toLocaleDateString('en-US', { weekday:'short', month:'long', day:'numeric', year:'numeric' });
}

// ── SIDEBAR TOGGLE (mobile) ───────────────
const sidebar    = document.getElementById('sidebar');
const topbarMenu = document.getElementById('topbarMenu');
const sidebarToggle = document.getElementById('sidebarToggle');

if (topbarMenu && sidebar) {
  topbarMenu.addEventListener('click', () => sidebar.classList.toggle('open'));
}
if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
}

// ── FLASH AUTO-DISMISS ────────────────────
document.querySelectorAll('.admin-flash').forEach(flash => {
  setTimeout(() => flash.remove(), 5000);
});

// ── CONFIRM DELETES ───────────────────────
document.querySelectorAll('[data-confirm]').forEach(btn => {
  btn.addEventListener('click', e => {
    if (!confirm(btn.dataset.confirm)) e.preventDefault();
  });
});
