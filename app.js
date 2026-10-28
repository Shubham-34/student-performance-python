/* Student Performance System - small vanilla JS for the interactive parts. */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---- dark / light theme (remembered) ---- */
  var saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  if (!saved && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) saved = "dark";
  setTheme(saved || "light");
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    var b = document.getElementById("themeToggle");
    if (b) b.textContent = t === "dark" ? "☀️" : "🌙";
  }
  var toggle = document.getElementById("themeToggle");
  if (toggle) {
    setTheme(root.getAttribute("data-theme"));
    toggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  /* ---- avatars: initials + colour from the name ---- */
  document.querySelectorAll(".avatar[data-name]").forEach(function (el) {
    var name = el.getAttribute("data-name").trim();
    var parts = name.split(/\s+/);
    el.textContent = ((parts[0] || "?")[0] + (parts.length > 1 ? parts[parts.length - 1][0] : "")).toUpperCase();
    var h = 0;
    for (var i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) % 360;
    el.style.background = "linear-gradient(135deg, hsl(" + h + ",70%,52%), hsl(" + ((h + 40) % 360) + ",70%,45%))";
  });

  /* ---- animated numbers ---- */
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var target = parseFloat(el.getAttribute("data-count")) || 0;
    var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var start = null, dur = 900;
    function frame(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(dec) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  });

  /* ---- grow bars / columns after load ---- */
  requestAnimationFrame(function () {
    setTimeout(function () {
      document.querySelectorAll("[data-width]").forEach(function (el) {
        el.style.width = Math.max(0, Math.min(100, parseFloat(el.getAttribute("data-width")))) + "%";
      });
      document.querySelectorAll("[data-height]").forEach(function (el) {
        el.style.height = Math.max(2, Math.min(100, parseFloat(el.getAttribute("data-height")))) + "%";
      });
    }, 80);
  });

  /* ---- donut chart from data-values="pass,risk,fail" ---- */
  document.querySelectorAll(".donut[data-values]").forEach(function (svg) {
    var vals = svg.getAttribute("data-values").split(",").map(Number);
    var colors = ["var(--ok)", "#f59e0b", "var(--bad)"];
    var total = vals.reduce(function (a, b) { return a + b; }, 0);
    var NS = "http://www.w3.org/2000/svg";
    function circle(cls) {
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", "21"); c.setAttribute("cy", "21"); c.setAttribute("r", "15.9155");
      if (cls) c.setAttribute("class", cls);
      svg.appendChild(c);
      return c;
    }
    circle("track");
    if (!total) return;
    var offset = 0;
    vals.forEach(function (v, i) {
      if (!v) return;
      var pct = (v / total) * 100;
      var c = circle();
      c.style.stroke = colors[i];
      c.setAttribute("stroke-dasharray", "0 100");
      c.setAttribute("stroke-dashoffset", String(-offset));
      setTimeout(function () { c.setAttribute("stroke-dasharray", Math.max(pct - 0.8, 0.2) + " " + (100 - pct + 0.8)); }, 100);
      offset += pct;
    });
  });

  /* ---- toasts ---- */
  document.querySelectorAll(".toast").forEach(function (t) {
    function close() { t.classList.add("leaving"); setTimeout(function () { t.remove(); }, 320); }
    t.addEventListener("click", close);
    setTimeout(close, 4500);
  });

  /* ---- live search / filter / sort on the students table ---- */
  var table = document.getElementById("studentTable");
  if (table) {
    var q = document.getElementById("liveSearch");
    var dept = document.getElementById("liveDept");
    var shown = document.getElementById("shownCount");
    var empty = document.getElementById("noMatch");
    var tbody = table.tBodies[0];

    function applyFilter() {
      var text = q ? q.value.trim().toLowerCase() : "";
      var d = dept ? dept.value : "";
      var n = 0;
      Array.prototype.forEach.call(tbody.rows, function (row) {
        var ok = (!text || row.dataset.name.indexOf(text) > -1 || row.dataset.roll.indexOf(text) > -1) &&
                 (!d || row.dataset.dept === d);
        row.hidden = !ok;
        if (ok) n++;
      });
      if (shown) shown.textContent = n;
      if (empty) empty.hidden = n !== 0;
      table.parentNode.hidden = n === 0;
    }
    if (q) q.addEventListener("input", applyFilter);
    if (dept) dept.addEventListener("change", applyFilter);
    var filterForm = document.getElementById("filterForm");
    if (filterForm) filterForm.addEventListener("submit", function (e) { e.preventDefault(); applyFilter(); });
    var reset = document.getElementById("resetFilters");
    if (reset) reset.addEventListener("click", function (e) {
      e.preventDefault(); if (q) q.value = ""; if (dept) dept.value = ""; applyFilter();
    });
    applyFilter();

    table.querySelectorAll("th[data-sort]").forEach(function (th, idx) {
      th.addEventListener("click", function () {
        var col = Array.prototype.indexOf.call(th.parentNode.children, th);
        var numeric = th.getAttribute("data-sort") === "num";
        var dir = th.classList.contains("sorted-asc") ? -1 : 1;
        table.querySelectorAll("th").forEach(function (h) { h.classList.remove("sorted-asc", "sorted-desc"); });
        th.classList.add(dir === 1 ? "sorted-asc" : "sorted-desc");
        var rows = Array.prototype.slice.call(tbody.rows);
        rows.sort(function (a, b) {
          var av = a.cells[col].getAttribute("data-value") || a.cells[col].textContent.trim();
          var bv = b.cells[col].getAttribute("data-value") || b.cells[col].textContent.trim();
          if (numeric) return (parseFloat(av) - parseFloat(bv)) * dir;
          return av.localeCompare(bv, undefined, { sensitivity: "base" }) * dir;
        });
        rows.forEach(function (r) { tbody.appendChild(r); });
      });
    });

    tbody.addEventListener("click", function (e) {
      if (e.target.closest("a, button, form")) return;
      var row = e.target.closest("tr[data-href]");
      if (row) window.location = row.getAttribute("data-href");
    });
  }

  /* ---- confirmation dialog for dangerous forms ---- */
  var dlg = document.getElementById("confirmDialog");
  if (dlg && dlg.showModal) {
    var pending = null;
    document.querySelectorAll("form[data-confirm]").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        pending = f;
        document.getElementById("confirmTitle").textContent = f.getAttribute("data-confirm-title") || "Are you sure?";
        document.getElementById("confirmText").textContent = f.getAttribute("data-confirm");
        dlg.showModal();
      });
    });
    document.getElementById("confirmYes").addEventListener("click", function () {
      dlg.close();
      if (pending) pending.submit();
    });
    document.getElementById("confirmNo").addEventListener("click", function () { dlg.close(); pending = null; });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  } else {
    document.querySelectorAll("form[data-confirm]").forEach(function (f) {
      f.addEventListener("submit", function (e) { if (!confirm(f.getAttribute("data-confirm"))) e.preventDefault(); });
    });
  }

  /* ---- mark form: slider <-> number, subject chips ---- */
  var range = document.getElementById("scoreRange");
  var num = document.getElementById("scoreNumber");
  if (range && num) {
    range.addEventListener("input", function () { num.value = range.value; });
    num.addEventListener("input", function () { if (num.value !== "") range.value = num.value; });
  }
  var subj = document.getElementById("subjectInput");
  document.querySelectorAll(".chip[data-subject]").forEach(function (c) {
    c.addEventListener("click", function () {
      if (subj) { subj.value = c.getAttribute("data-subject"); (num || subj).focus(); }
    });
  });
})();
