import test from "node:test";
import assert from "node:assert/strict";

import {
  DisplayPhase,
  createDisplayViewModel,
  createInitialDisplayState,
  reduceDisplayState
} from "../src/display-state.mjs";

function readyState() {
  let state = createInitialDisplayState(true);
  state = reduceDisplayState(state, { type: "boot", online: true }).state;
  state = reduceDisplayState(state, { type: "host-ready", epoch: state.epoch }).state;
  return state;
}

test("boot and host-ready create a focused, bounded display route", () => {
  const result = reduceDisplayState(
    reduceDisplayState(createInitialDisplayState(), { type: "boot", online: true }).state,
    { type: "host-ready", epoch: 1 }
  );

  assert.equal(result.state.phase, DisplayPhase.READY);
  assert.equal(result.state.epoch, 1);
  assert.deepEqual(result.effects, ["focus-primary"]);

  const view = createDisplayViewModel(result.state);
  assert.deepEqual(
    { width: view.width, height: view.height },
    { width: 600, height: 600 }
  );
  assert.ok(view.title.length <= 42);
  assert.ok(view.body.length <= 110);
});

test("stale input is ignored while current input remains actionable", () => {
  const state = readyState();

  const stale = reduceDisplayState(state, {
    type: "input",
    action: "enter",
    epoch: state.epoch - 1
  });
  assert.deepEqual(stale.effects, ["ignore-stale"]);
  assert.equal(stale.state.phase, DisplayPhase.READY);

  const current = reduceDisplayState(state, {
    type: "input",
    action: "enter",
    epoch: state.epoch
  });
  assert.deepEqual(current.effects, ["primary-action"]);
  assert.equal(current.state.phase, DisplayPhase.FOCUSED);
});

test("left/right input moves focus and the phone control falls back locally", () => {
  const state = readyState();
  const moved = reduceDisplayState(state, { type: "input", action: "right" });
  assert.equal(moved.state.focusIndex, 1);
  assert.deepEqual(moved.effects, ["focus-control"]);

  const fallback = reduceDisplayState(moved.state, { type: "input", action: "phone" });
  assert.equal(fallback.state.phase, DisplayPhase.FALLBACK);
  assert.equal(fallback.state.reason, "phone-requested");
  assert.deepEqual(fallback.effects, ["phone-fallback"]);
});

test("network loss, timeout, and host exit all preserve a phone route", () => {
  const state = readyState();

  const offline = reduceDisplayState(state, { type: "network", online: false });
  assert.equal(offline.state.phase, DisplayPhase.FALLBACK);
  assert.equal(offline.state.reason, "network-unavailable");

  const timedOut = reduceDisplayState(state, { type: "timeout" });
  assert.equal(timedOut.state.reason, "host-timeout");

  const exited = reduceDisplayState(state, { type: "exit" });
  assert.equal(exited.state.phase, DisplayPhase.EXITED);
  assert.deepEqual(exited.effects, ["release-host-resources", "phone-fallback"]);
});

test("error and untrusted reasons are bounded and control-character free", () => {
  const result = reduceDisplayState(readyState(), {
    type: "error",
    reason: "\u0000" + "x".repeat(100)
  });
  const view = createDisplayViewModel(result.state);

  assert.equal(result.state.phase, DisplayPhase.ERROR);
  assert.ok(view.body.length <= 110);
  assert.equal(/\p{Cc}/u.test(view.body), false);
});
