/* Get Out! classroom adaptation. Pure rules shared by browser and Node. */
(function (root) {
  'use strict';
  const directions = {up: [-1, 0], right: [0, 1], down: [1, 0], left: [0, -1]};
  function create(board) {
    if (!Array.isArray(board) || board.length < 2 || board.length > 20 ||
        typeof board[0] !== 'string' || board[0].length < 2 || board[0].length > 20 ||
        board.some(row => typeof row !== 'string' || row.length !== board[0].length || /[^.#SEBO]/.test(row))) {
      throw new Error('Use a rectangular board, 2–20 rows and columns, with only S, E, B, O, #, and .');
    }
    const all = board.join('');
    const blue=all.split('B').length-1, orange=all.split('O').length-1;
    if (!((blue===0&&orange===0)||(blue===1&&orange===1))) {
      throw new Error('Place exactly one blue (B) and one orange (O) portal, or remove both.');
    }
    if (all.split('S').length !== 2 || all.split('E').length !== 2) {
      throw new Error('Place exactly one start (S) and one exit (E).');
    }
    const r = board.findIndex(row => row.includes('S'));
    return {board: board.slice(), position: [r, board[r].indexOf('S')], moves: 0, won: false};
  }
  function step(state, action) {
    if (!Object.hasOwn(directions, action)) throw new Error('Unknown direction.');
    if (state.won) return state;
    const [dr, dc] = directions[action];
    let [r, c] = state.position;
    let moved=false;
    while (true) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= state.board.length || nc < 0 || nc >= state.board[0].length || state.board[nr][nc] === '#') break;
      r = nr; c = nc;moved=true;
      if (state.board[r][c] === 'E') break;
      const tile=state.board[r][c];
      if(tile==='B'||tile==='O'){
        const target=tile==='B'?'O':'B';
        r=state.board.findIndex(row=>row.includes(target));c=state.board[r].indexOf(target);
        break; // A portal is a stopping point. It only triggers on entry.
      }
    }
    if (!moved) return state;
    return {...state, position: [r, c], moves: state.moves + 1, won: state.board[r][c] === 'E'};
  }
  function legalActions(state) {
    return Object.keys(directions).filter(action => step(state, action) !== state);
  }
  function observe(state) {
    return {board: state.board.slice(), position: state.position.slice(), moves: state.moves,
      won: state.won, legalActions: legalActions(state)};
  }
  function solve(state) {
    const queue = [{state, path: []}], seen = new Set([state.position.join(',')]);
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i];
      if (item.state.won) return item.path;
      for (const action of legalActions(item.state)) {
        const next = step(item.state, action), key = next.position.join(',');
        if (!seen.has(key)) {
          seen.add(key); queue.push({state: next, path: [...item.path, action]});
        }
      }
    }
    return null;
  }
  const api = {create, step, legalActions, observe, solve};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GetOut = api;
})(globalThis);
