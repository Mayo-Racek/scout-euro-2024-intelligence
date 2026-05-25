// dataform/includes/constants.js
// ONE source of truth for every threshold. Change here, everything inherits it.
// This is WHY the agent stays accurate: definitions never drift.

module.exports = {
  // StatsBomb pitch is 120 long x 80 wide. Goal is at x=120.
  PITCH_LENGTH: 120,
  PITCH_WIDTH: 80,

  // A pass is "forward" if it advances > 5m toward goal, "backward" if < -5m.
  FORWARD_THRESHOLD: 5,

  // "Progressive": ends at least 25% closer to the goal than it started.
  PROGRESSIVE_RATIO: 0.75,

  // Opening phase default window (minutes).
  OPENING_END: 15,
  CLOSING_START: 75,

  // PPDA is measured in the opponent's defensive 60% of the pitch (x < 72 = own 60).
  // Defensive actions counted where x >= PPDA_LINE (high up the pitch).
  PPDA_LINE: 48,   // 40% line from defending team's perspective

  // Sample-size honesty thresholds.
  MIN_MINUTES_RELIABLE: 180,
  MIN_SHOTS_FOR_FINISHING_CLAIM: 20,
};
