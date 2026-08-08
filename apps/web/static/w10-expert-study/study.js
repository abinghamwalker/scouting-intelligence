"use strict";

function checkedValue(form, name) {
  const control = form.querySelector(`input[name="${name}"]:checked`);
  return control ? control.value : "";
}

function setGroupAvailability(group, enabled) {
  group.classList.toggle("is-disabled", !enabled);
  for (const control of group.querySelectorAll("input, select")) {
    control.disabled = !enabled;
    if (!enabled && control.type === "radio") control.checked = false;
  }
}

function setResponseRequirements(form) {
  const fairComparison = checkedValue(form, "fair_comparison");
  const canRate = fairComparison === "yes";
  for (const group of form.querySelectorAll(".rating-question")) {
    setGroupAvailability(group, canRate);
    const firstRating = group.querySelector("input[type=radio]");
    if (firstRating) firstRating.required = canRate;
  }

  const basisControls = [...form.querySelectorAll('input[name="assessment_basis"]')];
  const unableBasis = basisControls.find((control) => control.value === "unable_to_assess");
  if (fairComparison === "no" && unableBasis) unableBasis.checked = true;
  if (fairComparison === "yes" && unableBasis && unableBasis.checked) unableBasis.checked = false;
  for (const control of basisControls) {
    control.disabled = fairComparison === "no" && control.value !== "unable_to_assess";
    if (control.value === "unable_to_assess") control.disabled = fairComparison === "yes";
  }
  const basis = checkedValue(form, "assessment_basis");
  const usesForm = basis === "supplied_evidence" || basis === "both";
  const helpedChoices = [...form.querySelectorAll(".helped-control")];
  for (const control of helpedChoices) {
    control.disabled = !usesForm;
    if (!usesForm) control.checked = false;
  }
  const additionalChoices = [...form.querySelectorAll(".additional-helped-control")];
  const firstAdditional = additionalChoices[0];
  if (firstAdditional) {
    const hasAdditionalChoice = additionalChoices.some((control) => control.checked);
    firstAdditional.setCustomValidity(
      usesForm && !hasAdditionalChoice
        ? "Select at least one kind of additional information that helped your answer."
        : "",
    );
  }

  const missingInformation = checkedValue(form, "important_information_missing") === "yes";
  const gap = form.querySelector('select[name="evidence_gap"]');
  const explanation = form.querySelector('textarea[name="explanation"]');
  if (gap) {
    gap.disabled = !missingInformation;
    gap.required = missingInformation;
    if (!missingInformation) gap.value = "";
  }
  if (explanation) explanation.required = fairComparison === "no" || missingInformation;

  const helpfulError = form.querySelector(".helped-error");
  if (helpfulError) {
    helpfulError.textContent = firstAdditional && firstAdditional.validationMessage
      ? firstAdditional.validationMessage
      : "";
  }

  const status = form.querySelector(".form-status");
  if (status) {
    const messages = [];
    if (!fairComparison) messages.push("say whether a fair comparison is possible");
    if (canRate && !checkedValue(form, "credibility")) messages.push("rate credibility");
    if (canRate && !checkedValue(form, "confidence")) messages.push("rate confidence");
    if (!basis) messages.push("say what you based the answer on");
    if (firstAdditional && firstAdditional.validationMessage) messages.push("choose helpful additional evidence");
    if (!checkedValue(form, "important_information_missing")) messages.push("say whether information was missing");
    if (form.dataset.interacted !== "true" && messages.length) {
      status.textContent = "Complete each question, then save your answer to continue.";
      delete status.dataset.level;
    } else {
      const guidance = fairComparison === "yes"
        ? "You can now rate the comparison and your confidence."
        : fairComparison === "no"
          ? "Because you selected “No,” choose what was missing and explain what prevented a fair judgement."
          : "";
      status.textContent = messages.length
        ? `${guidance} Still needed: ${messages.join(", ")}.`.trim()
        : "Your answer is ready to save.";
      status.dataset.level = messages.length ? "error" : "ready";
    }
  }
}

function prepareResponseForm(form) {
  for (const control of form.querySelectorAll("input, select, textarea")) {
    control.addEventListener("change", () => {
      form.dataset.interacted = "true";
      if (control.name === "fair_comparison") {
        const matchingMissing = form.querySelector(
          `input[name="important_information_missing"][value="${control.value === "yes" ? "no" : "yes"}"]`,
        );
        if (matchingMissing) matchingMissing.checked = true;
      }
      if (control.name === "important_information_missing") {
        const matchingFair = form.querySelector(
          `input[name="fair_comparison"][value="${control.value === "yes" ? "no" : "yes"}"]`,
        );
        if (matchingFair) matchingFair.checked = true;
      }
      setResponseRequirements(form);
    });
    control.addEventListener("input", () => {
      form.dataset.interacted = "true";
      setResponseRequirements(form);
    });
  }
  form.addEventListener("submit", (event) => {
    setResponseRequirements(form);
    if (!form.checkValidity()) {
      event.preventDefault();
      const firstInvalid = form.querySelector(":invalid");
      if (firstInvalid) {
        firstInvalid.focus();
        firstInvalid.reportValidity();
      }
      const status = form.querySelector(".form-status");
      if (status) {
        status.textContent = "Please complete the highlighted questions before continuing.";
        status.dataset.level = "error";
      }
    }
  });
  setResponseRequirements(form);
}

for (const form of document.querySelectorAll(".response-form")) prepareResponseForm(form);

function setStartRequirements(form) {
  const showRequiredErrors = form.dataset.validationAttempted === "true";
  const participantCode = form.querySelector('input[name="participant_code"]');
  const participantCodeError = document.getElementById("participant-code-error");
  if (participantCode) {
    const codeIsValid = /^[A-Z0-9][A-Z0-9-]{5,31}$/.test(participantCode.value);
    participantCode.setCustomValidity(
      participantCode.value && !codeIsValid
        ? "Use 6–32 upper-case letters, numbers or hyphens, starting with a letter or number."
        : "",
    );
    if (participantCodeError) {
      participantCodeError.textContent = showRequiredErrors || participantCode.value
        ? participantCode.validationMessage
        : "";
    }
  }

  const years = form.querySelector('input[name="years_experience"]');
  const yearsError = document.getElementById("experience-years-error");
  if (years) {
    const numberOfYears = Number(years.value);
    years.setCustomValidity(
      years.value && numberOfYears < 2
        ? "This trial requires at least two years of relevant professional football experience."
        : years.value && numberOfYears > 80
          ? "Enter no more than 80 years of relevant professional football experience."
          : "",
    );
    if (yearsError) {
      yearsError.textContent = showRequiredErrors || years.value ? years.validationMessage : "";
    }
  }

  const experienceChoices = [...form.querySelectorAll(".experience-choice")];
  const firstExperience = experienceChoices[0];
  const hasExperience = experienceChoices.some((control) => control.checked);
  if (firstExperience) {
    firstExperience.setCustomValidity(hasExperience ? "" : "Select at least one relevant professional football role.");
  }
  const groupError = form.querySelector(".group-error");
  if (groupError) {
    groupError.textContent = showRequiredErrors && firstExperience ? firstExperience.validationMessage : "";
  }

  const assessmentChoices = [...form.querySelectorAll(".assessment-choice")];
  const recentAssessment = document.getElementById("recent-assessment");
  const assessmentAnswered = assessmentChoices.some((control) => control.checked);
  const assessmentEligible = Boolean(recentAssessment && recentAssessment.checked);
  if (recentAssessment) {
    recentAssessment.setCustomValidity(
      assessmentEligible
        ? ""
        : assessmentAnswered
          ? "This trial requires professional player assessment within the last five years."
          : "Answer whether you have assessed players professionally within the last five years.",
    );
  }
  const assessmentError = form.querySelector(".assessment-error");
  if (assessmentError) {
    assessmentError.textContent = (showRequiredErrors || (assessmentAnswered && !assessmentEligible)) && recentAssessment
      ? recentAssessment.validationMessage
      : "";
  }

  const conflictChoices = [...form.querySelectorAll(".conflict-choice")];
  const firstConflictChoice = conflictChoices[0];
  const conflictAnswered = conflictChoices.some((control) => control.checked);
  const conflictDeclared = form.querySelector('#conflict-declared');
  if (firstConflictChoice) {
    firstConflictChoice.setCustomValidity(
      !conflictAnswered
        ? "Answer whether you have a current or recent player or club conflict."
        : conflictDeclared && conflictDeclared.checked
          ? "You cannot continue with a player or club conflict."
          : "",
    );
  }
  const conflictError = form.querySelector(".conflict-error");
  if (conflictError) {
    conflictError.textContent = (showRequiredErrors || (conflictDeclared && conflictDeclared.checked)) && firstConflictChoice
      ? firstConflictChoice.validationMessage
      : "";
  }

  const conflictNote = form.querySelector('#conflict-note');
  if (conflictDeclared && conflictNote) {
    conflictNote.required = conflictDeclared.checked;
    conflictNote.setCustomValidity(
      conflictDeclared.checked && !conflictNote.value.trim()
        ? "Briefly describe the conflict you declared."
        : "",
    );
  }

  const consentChoices = [...form.querySelectorAll(".consent-choice")];
  for (const consent of consentChoices) {
    consent.setCustomValidity(consent.checked ? "" : "Confirm this statement before continuing.");
  }
  const consentError = form.querySelector(".consent-error");
  if (consentError) {
    const remaining = consentChoices.filter((control) => !control.checked).length;
    consentError.textContent = showRequiredErrors && remaining
      ? "Confirm all five statements before starting."
      : "";
  }
}

const startForm = document.getElementById("start-form");
if (startForm) {
  for (const control of startForm.querySelectorAll("input, textarea")) {
    control.addEventListener("change", () => setStartRequirements(startForm));
    control.addEventListener("input", () => setStartRequirements(startForm));
  }
  startForm.addEventListener("submit", (event) => {
    startForm.dataset.validationAttempted = "true";
    setStartRequirements(startForm);
    if (!startForm.checkValidity()) {
      event.preventDefault();
      const firstInvalid = startForm.querySelector(":invalid");
      if (firstInvalid) {
        firstInvalid.focus();
        firstInvalid.reportValidity();
      }
      const status = document.getElementById("start-status");
      if (status) {
        status.textContent = "Please complete the highlighted eligibility and consent questions.";
        status.dataset.level = "error";
      }
    }
  });
  setStartRequirements(startForm);
}

function setFeedbackRequirements(form) {
  let unanswered = 0;
  for (const question of form.querySelectorAll(".feedback-question")) {
    const detailsName = question.dataset.detailsName;
    const selected = question.querySelector("input[type=radio]:checked");
    const details = form.querySelector(`textarea[name="${detailsName}"]`);
    if (!selected) unanswered += 1;
    if (details) {
      const needsDetails = selected && selected.value === "yes";
      details.required = Boolean(needsDetails);
      details.setCustomValidity(
        needsDetails && !details.value.trim()
          ? "Please add a short explanation for this answer."
          : "",
      );
    }
  }
  const status = form.querySelector(".form-status");
  if (status) {
    if (form.dataset.interacted !== "true" && unanswered) {
      status.textContent = "Answer each question, adding details wherever you select Yes.";
      delete status.dataset.level;
    } else {
      status.textContent = unanswered
        ? `Please answer ${unanswered} remaining question${unanswered === 1 ? "" : "s"}.`
        : "Your feedback is ready to save.";
      status.dataset.level = unanswered ? "error" : "ready";
    }
  }
}

for (const form of document.querySelectorAll(".feedback-form")) {
  for (const control of form.querySelectorAll("input, textarea")) {
    control.addEventListener("change", () => {
      form.dataset.interacted = "true";
      setFeedbackRequirements(form);
    });
    control.addEventListener("input", () => {
      form.dataset.interacted = "true";
      setFeedbackRequirements(form);
    });
  }
  form.addEventListener("submit", (event) => {
    setFeedbackRequirements(form);
    if (!form.checkValidity()) {
      event.preventDefault();
      const firstInvalid = form.querySelector(":invalid");
      if (firstInvalid) {
        firstInvalid.focus();
        firstInvalid.reportValidity();
      }
      const status = form.querySelector(".form-status");
      if (status) {
        status.textContent = "Please answer each question and add details wherever you selected Yes.";
        status.dataset.level = "error";
      }
    }
  });
  setFeedbackRequirements(form);
}

const evidenceViews = [...document.querySelectorAll('input[name="evidence_view"]')];
if (evidenceViews.length) {
  const updateEvidenceView = () => {
    const referenceView = evidenceViews.some(
      (control) => control.checked && control.value === "reference",
    );
    for (const value of document.querySelectorAll(".recorded-value")) value.hidden = referenceView;
    for (const value of document.querySelectorAll(".percentile-value")) value.hidden = !referenceView;
  };
  for (const control of evidenceViews) control.addEventListener("change", updateEvidenceView);
  updateEvidenceView();
}

const printReceipt = document.getElementById("print-receipt");
if (printReceipt) printReceipt.addEventListener("click", () => window.print());

const participantError = document.getElementById("participant-error");
if (participantError) participantError.focus();
