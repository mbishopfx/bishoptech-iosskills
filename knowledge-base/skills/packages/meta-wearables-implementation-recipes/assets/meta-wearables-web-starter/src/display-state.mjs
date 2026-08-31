export const DISPLAY_WIDTH = 600;
export const DISPLAY_HEIGHT = 600;

const MAX_TITLE_LENGTH = 42;
const MAX_BODY_LENGTH = 110;
const MAX_ACTION_LENGTH = 24;

const PHASES = Object.freeze({
  LOADING: "loading",
  READY: "ready",
  FOCUSED: "focused",
  FALLBACK: "fallback",
  EXITED: "exited",
  ERROR: "error"
});

export const DisplayPhase = PHASES;

export function createInitialDisplayState(online = true) {
  return {
    phase: PHASES.LOADING,
    epoch: 0,
    focusIndex: 0,
    online: Boolean(online),
    reason: null
  };
}

function withEffect(state, effect) {
  return {
    state,
    effects: effect ? [effect] : []
  };
}

function withEffects(state, effects) {
  return { state, effects };
}

function isStale(state, event) {
  return Number.isInteger(event.epoch) && event.epoch !== state.epoch;
}

function staleResult(state) {
  return withEffect(state, "ignore-stale");
}

function fallbackState(state, reason) {
  return {
    ...state,
    phase: PHASES.FALLBACK,
    reason: sanitize(reason, "wearable-route-unavailable", 48)
  };
}

export function reduceDisplayState(state, event) {
  if (!event || typeof event.type !== "string") {
    return staleResult(state);
  }

  switch (event.type) {
    case "boot": {
      const next = createInitialDisplayState(event.online ?? state.online);
      next.epoch = state.epoch + 1;
      return withEffect(next, "host-bootstrap");
    }

    case "host-ready":
      if (isStale(state, event) || state.phase !== PHASES.LOADING) {
        return staleResult(state);
      }
      return withEffect(
        { ...state, phase: PHASES.READY, reason: null },
        "focus-primary"
      );

    case "focus":
      if (isStale(state, event) || ![PHASES.READY, PHASES.FOCUSED].includes(state.phase)) {
        return staleResult(state);
      }
      return withEffect(
        {
          ...state,
          phase: PHASES.FOCUSED,
          focusIndex: event.index === 1 ? 1 : 0
        },
        "focus-control"
      );

    case "input": {
      if (isStale(state, event)) {
        return staleResult(state);
      }

      const action = String(event.action ?? "").toLowerCase();
      if ([PHASES.FALLBACK, PHASES.EXITED, PHASES.ERROR].includes(state.phase)) {
        return staleResult(state);
      }

      if (action === "left" || action === "right") {
        return withEffect(
          {
            ...state,
            phase: PHASES.FOCUSED,
            focusIndex: action === "right" ? 1 : 0
          },
          "focus-control"
        );
      }

      if (action === "escape" || action === "back" || action === "exit") {
        return withEffect(
          { ...fallbackState(state, "host-exit"), phase: PHASES.EXITED },
          "phone-fallback"
        );
      }

      if (["enter", "select", "primary"].includes(action) && state.focusIndex === 0) {
        return withEffect(
          { ...state, phase: PHASES.FOCUSED, reason: null },
          "primary-action"
        );
      }

      if (["enter", "select", "secondary", "phone"].includes(action) && state.focusIndex === 1) {
        return withEffect(fallbackState(state, "phone-requested"), "phone-fallback");
      }

      return staleResult(state);
    }

    case "network":
      if (event.online === false) {
        return withEffect(
          fallbackState({ ...state, online: false }, "network-unavailable"),
          "phone-fallback"
        );
      }
      return withEffect({ ...state, online: true }, "network-restored");

    case "timeout":
      return withEffect(fallbackState(state, "host-timeout"), "phone-fallback");

    case "error":
      return withEffects(
        { ...state, phase: PHASES.ERROR, reason: sanitize(event.reason, "host-error", 48) },
        ["show-error", "phone-fallback"]
      );

    case "exit":
      return withEffects(
        { ...fallbackState(state, "host-exit"), phase: PHASES.EXITED },
        ["release-host-resources", "phone-fallback"]
      );

    default:
      return staleResult(state);
  }
}

export function createDisplayViewModel(state) {
  const reason = sanitize(state.reason, "wearable route unavailable", 48);

  if (state.phase === PHASES.LOADING) {
    return viewModel("Preparing display", "Starting the wearable route.", "Please wait", "Use phone", state);
  }

  if ([PHASES.READY, PHASES.FOCUSED].includes(state.phase)) {
    return viewModel("Ready", "Choose an action.", "Open", "Use phone", state);
  }

  if (state.phase === PHASES.ERROR) {
    return viewModel("Display unavailable", `Continue on your phone. (${reason})`, "Use phone", "Close", state);
  }

  if (state.phase === PHASES.EXITED) {
    return viewModel("Display closed", "Continue on your phone.", "Use phone", "Close", state);
  }

  return viewModel("Use your phone", `The wearable route is unavailable. (${reason})`, "Continue on phone", "Close", state);
}

function viewModel(title, body, primaryAction, secondaryAction, state) {
  return {
    width: DISPLAY_WIDTH,
    height: DISPLAY_HEIGHT,
    phase: state.phase,
    focusIndex: state.focusIndex,
    title: sanitize(title, "Display", MAX_TITLE_LENGTH),
    body: sanitize(body, "Continue on your phone.", MAX_BODY_LENGTH),
    primaryAction: sanitize(primaryAction, "Continue", MAX_ACTION_LENGTH),
    secondaryAction: sanitize(secondaryAction, "Close", MAX_ACTION_LENGTH),
    online: state.online
  };
}

function sanitize(value, fallback, maxLength) {
  const normalized = String(value ?? fallback)
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return (normalized || fallback).slice(0, maxLength);
}
