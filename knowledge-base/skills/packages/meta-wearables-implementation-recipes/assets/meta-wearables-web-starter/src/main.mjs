import {
  createDisplayViewModel,
  createInitialDisplayState,
  reduceDisplayState
} from "./display-state.mjs";

const root = document.querySelector("#app");
const title = document.querySelector("#title");
const body = document.querySelector("#body");
const status = document.querySelector("#status");
const controls = [
  document.querySelector("#primary"),
  document.querySelector("#phone")
];

let state = createInitialDisplayState(window.navigator.onLine);

function dispatch(event) {
  const result = reduceDisplayState(state, {
    ...event,
    epoch: event.epoch ?? state.epoch
  });
  state = result.state;
  render();
  applyEffects(result.effects);
}

function render() {
  const snapshot = createDisplayViewModel(state);
  root.dataset.phase = snapshot.phase;
  root.dataset.online = String(snapshot.online);
  title.textContent = snapshot.title;
  body.textContent = snapshot.body;
  controls[0].textContent = snapshot.primaryAction;
  controls[1].textContent = snapshot.secondaryAction;

  controls.forEach((control, index) => {
    control.tabIndex = index === snapshot.focusIndex ? 0 : -1;
    control.setAttribute("aria-current", index === snapshot.focusIndex ? "true" : "false");
  });
}

function applyEffects(effects) {
  if (effects.includes("primary-action")) {
    status.textContent = "Primary action selected.";
  } else if (effects.includes("phone-fallback")) {
    status.textContent = "Continue on your phone.";
  } else if (effects.includes("ignore-stale")) {
    status.textContent = "Stale input ignored.";
  }
}

function activate(index) {
  dispatch({ type: "focus", index });
  dispatch({ type: "input", action: "enter" });
}

controls[0].addEventListener("click", () => activate(0));
controls[1].addEventListener("click", () => activate(1));

document.addEventListener("keydown", (event) => {
  const actionByKey = {
    ArrowLeft: "left",
    ArrowRight: "right",
    Enter: "enter",
    Escape: "escape"
  };
  const action = actionByKey[event.key];
  if (!action) return;
  event.preventDefault();
  dispatch({ type: "input", action });
});

window.addEventListener("offline", () => dispatch({ type: "network", online: false }));
window.addEventListener("online", () => dispatch({ type: "network", online: true }));

// HOST GATE: adapt the current Meta Wearables Web App host input and exit
// contract here after resolving the selected toolkit revision. This starter
// intentionally never guesses private globals or sends credentials to a host.
window.addEventListener("pagehide", () => dispatch({ type: "exit" }));

dispatch({ type: "boot", online: window.navigator.onLine });
dispatch({ type: "host-ready" });
