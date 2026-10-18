/* In-memory exploration, separate from movement rules and undo history. */
(function (root) {
  'use strict';
  const key = position => position.join(',');
  function start(state) {
    return new Set([key(state.position)]);
  }
  function recordMove(stops, previous, next) {
    if (next === previous || stops.has(key(next.position))) return stops;
    return new Set([...stops, key(next.position)]);
  }
  function has(stops, position) {
    return stops.has(key(position));
  }
  const api = {start, recordMove, has};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GetOutExploration = api;
})(globalThis);
