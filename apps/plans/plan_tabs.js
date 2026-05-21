/**
 * Plan Admin — Tab Navigation
 * Turns Django admin fieldsets into clickable tabs.
 * The inline (Variations) is appended as a second tab automatically.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#content-main form");
    if (!form) return;

    // Gather fieldset sections (each represents one tab)
    const fieldsets = Array.from(form.querySelectorAll("fieldset"));
    // Gather the inline group(s) — treat each as a tab
    const inlineGroups = Array.from(form.querySelectorAll(".inline-group"));

    if (fieldsets.length === 0 && inlineGroups.length === 0) return;

    // Build tab bar container
    const tabBar = document.createElement("div");
    tabBar.className = "plan-tab-bar";
    tabBar.style.cssText =
      "display:flex;gap:4px;margin-bottom:0;border-bottom:2px solid #1a73e8;";

    const panels = [];

    function makeTab(label, panel) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = label;
      btn.style.cssText =
        "padding:8px 18px;border:none;background:#f0f4ff;color:#1a3a6b;" +
        "font-size:13px;font-weight:600;cursor:pointer;border-radius:4px 4px 0 0;" +
        "letter-spacing:0.03em;transition:background 0.15s;";
      btn.addEventListener("click", function () {
        panels.forEach(function (p) {
          p.style.display = "none";
        });
        tabBtns.forEach(function (b) {
          b.style.background = "#f0f4ff";
          b.style.color = "#1a3a6b";
          b.style.borderBottom = "2px solid transparent";
        });
        panel.style.display = "";
        btn.style.background = "#fff";
        btn.style.color = "#1a73e8";
        btn.style.borderBottom = "2px solid #fff";
        btn.style.marginBottom = "-2px";
      });
      return btn;
    }

    const tabBtns = [];

    // Wrap all fieldsets into one "General" panel
    if (fieldsets.length) {
      const generalPanel = document.createElement("div");
      generalPanel.className = "plan-tab-panel";
      generalPanel.style.cssText =
        "padding:16px;border:1px solid #e0e0e0;border-top:none;background:#fff;";
      const firstFieldset = fieldsets[0];
      firstFieldset.parentNode.insertBefore(generalPanel, firstFieldset);
      fieldsets.forEach(function (fs) {
        generalPanel.appendChild(fs);
      });
      panels.push(generalPanel);
      const btn = makeTab("⚙ General", generalPanel);
      tabBtns.push(btn);
      tabBar.appendChild(btn);
    }

    // Each inline group becomes a "Variations" tab
    inlineGroups.forEach(function (ig, i) {
      const label =
        ig.querySelector("h2")?.textContent.trim() || "Variations " + (i + 1);
      const panel = document.createElement("div");
      panel.className = "plan-tab-panel";
      panel.style.cssText =
        "padding:16px;border:1px solid #e0e0e0;border-top:none;background:#fff;";
      ig.parentNode.insertBefore(panel, ig);
      panel.appendChild(ig);
      panel.style.display = "none";
      panels.push(panel);
      const btn = makeTab("📦 " + label, panel);
      tabBtns.push(btn);
      tabBar.appendChild(btn);
    });

    // Insert tab bar before the first panel
    if (panels.length) {
      panels[0].parentNode.insertBefore(tabBar, panels[0]);
      // Activate first tab
      tabBtns[0] && tabBtns[0].click();
    }
  });
})();
