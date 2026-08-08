"use strict";

function setRatingAvailability(form) {
  const selected = form.querySelector('input[name="state"]:checked');
  const enabled = selected && selected.value === "rated";
  for (const control of form.querySelectorAll(".rating-field select, .rating-field input")) {
    control.disabled = !enabled;
    control.required = enabled;
  }
  const status =
    form.querySelector(".form-status") ||
    (form.id === "judgement-form" ? document.getElementById("study-status") : null);
  if (status) {
    status.dataset.state = enabled ? "in-progress" : "explicit-missingness";
    status.textContent = enabled
      ? "Rated response selected. Relevance and confidence are required."
      : "Explicit abstain or unable-to-assess selected. Rating controls are disabled.";
  }
}

function selectedValue(form, name) {
  const checked = form.querySelector(`[name="${name}"]:checked`);
  if (checked) return checked.value;
  const select = form.querySelector(`select[name="${name}"]`);
  return select ? select.value : "";
}

function selectValue(form, name, value) {
  const radio = form.querySelector(`[name="${name}"][value="${value}"]`);
  if (radio) radio.checked = true;
  const select = form.querySelector(`select[name="${name}"]`);
  if (select) select.value = value;
}

function setEvidenceRequirements(form) {
  const state = selectedValue(form, "state");
  if (state === "unable_to_assess") {
    selectValue(form, "evidence_sufficiency", "insufficient");
    selectValue(form, "assessment_basis", "unable_to_assess");
  }
  const sufficiency = selectedValue(form, "evidence_sufficiency");
  const basis = selectedValue(form, "assessment_basis");
  const usesSupplied = basis === "supplied_evidence" || basis === "both";
  const insufficient = sufficiency === "insufficient";
  for (const control of form.querySelectorAll(".citation-control")) {
    control.required = usesSupplied;
    control.disabled = !usesSupplied;
  }
  for (const control of form.querySelectorAll(".gap-control, .gap-note")) {
    control.required = insufficient;
    control.disabled = !insufficient;
  }
  const status = form.querySelector(".form-status");
  if (status) {
    const requirements = [];
    if (state === "rated") requirements.push("relevance and confidence");
    if (usesSupplied) requirements.push("an independent-evidence citation");
    if (insufficient) requirements.push("a gap category and qualitative note");
    status.textContent = requirements.length
      ? `Required before saving: ${requirements.join(", ")}.`
      : "Select response state, evidence sufficiency and assessment basis.";
  }
}

for (const form of document.querySelectorAll(".judgement-form")) {
  for (const control of form.querySelectorAll("input, select")) {
    control.addEventListener("change", () => {
      setRatingAvailability(form);
      setEvidenceRequirements(form);
    });
  }
  setRatingAvailability(form);
  setEvidenceRequirements(form);
}

const evidenceView = document.getElementById("evidence-view");
if (evidenceView) {
  evidenceView.addEventListener("change", () => {
    for (const cell of document.querySelectorAll(".raw-value")) cell.hidden = evidenceView.checked;
    for (const cell of document.querySelectorAll(".percentile-value")) cell.hidden = !evidenceView.checked;
  });
}

const v2Error = document.getElementById("v2-error");
if (v2Error) v2Error.focus();
