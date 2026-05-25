// dataform/includes/zones.js
// The 18-zone pitch model (3 thirds x 6 channels) — a recognized framework,
// so it's defensible. Pitch is 120 long x 80 wide. Goal attacked is at x=120.
//
// Returns a BigQuery SQL expression that maps (x_col, y_col) -> a zone label.
// Thirds (length):   Def [0,40)  Mid [40,80)  Att [80,120]
// Channels (width):  6 bands of 13.33 each. Names below are from the
//   ATTACKING team's perspective (left touchline = y=0).
//
// Channel names: LW (left wing), LHS (left half-space), LC (left centre),
//                RC (right centre), RHS (right half-space), RW (right wing)

function zoneExpr(x, y) {
  return `
  CASE
    WHEN ${x} IS NULL OR ${y} IS NULL THEN NULL
    ELSE CONCAT(
      CASE WHEN ${x} < 40 THEN 'Def'
           WHEN ${x} < 80 THEN 'Mid'
           ELSE 'Att' END,
      '-',
      CASE WHEN ${y} < 13.33 THEN 'LW'
           WHEN ${y} < 26.67 THEN 'LHS'
           WHEN ${y} < 40.0  THEN 'LC'
           WHEN ${y} < 53.33 THEN 'RC'
           WHEN ${y} < 66.67 THEN 'RHS'
           ELSE 'RW' END
    )
  END`;
}

// Also expose third + channel separately for simpler aggregations
function thirdExpr(x) {
  return `CASE WHEN ${x} < 40 THEN 'Def' WHEN ${x} < 80 THEN 'Mid' ELSE 'Att' END`;
}

module.exports = { zoneExpr, thirdExpr };
