/* Get Out! classroom adaptation, swap-sides-with-a-roadblock variation. Pure rules shared by browser and Node.
   A move that misses the exit swaps the ball and the exit, so play alternates sides.
   A no-entry roadblock (X) stops the ball like a wall; placeRoadblock drops one on the shortest way out. */
(function (root) {
  'use strict';
  const directions = {up: [-1, 0], right: [0, 1], down: [1, 0], left: [0, -1]};
  function create(board) {
    if (!Array.isArray(board) || board.length < 2 || board.length > 20 ||
        typeof board[0] !== 'string' || board[0].length < 2 || board[0].length > 20 ||
        board.some(row => typeof row !== 'string' || row.length !== board[0].length || /[^.#SEX]/.test(row))) {
      throw new Error('Use a rectangular board, 2–20 rows and columns, with only S, E, #, X, and .');
    }
    const all = board.join('');
    if (all.split('S').length !== 2 || all.split('E').length !== 2) {
      throw new Error('Place exactly one start (S) and one exit (E).');
    }
    const r = board.findIndex(row => row.includes('S')), er = board.findIndex(row => row.includes('E'));
    return {board: board.slice(), position: [r, board[r].indexOf('S')], exit: [er, board[er].indexOf('E')], moves: 0, won: false};
  }
  // Walls and roadblocks both stop a slide; a roadblock is a wall the player did not expect.
  function solid(board, r, c) {
    return r < 0 || r >= board.length || c < 0 || c >= board[0].length || board[r][c] === '#' || board[r][c] === 'X';
  }
  // Every square the ball enters on one slide, ending where it stops or at the exit.
  function slide(state, action) {
    const [dr, dc] = directions[action];
    const [er, ec] = state.exit;
    let [r, c] = state.position;
    const cells = [];
    while (!solid(state.board, r + dr, c + dc)) {
      r += dr; c += dc; cells.push([r, c]);
      if (r === er && c === ec) break;
    }
    return cells;
  }
  function step(state, action) {
    if (!Object.hasOwn(directions, action)) throw new Error('Unknown direction.');
    if (state.won) return state;
    const [er, ec] = state.exit;
    const cells = slide(state, action);
    if (!cells.length) return state;
    const [r, c] = cells[cells.length - 1];
    if (r === er && c === ec) return {...state, position: [r, c], moves: state.moves + 1, won: true};
    // Missed the exit: the ball continues from the old exit, and the exit waits where the ball stopped.
    return {...state, position: [er, ec], exit: [r, c], moves: state.moves + 1, won: false};
  }
  function legalActions(state) {
    return Object.keys(directions).filter(action => step(state, action) !== state);
  }
  function observe(state) {
    // Board letters follow the moving exit, so the grid never shows a stale door.
    const [er, ec] = state.exit;
    const board = state.board.map((row, r) => [...row].map((v, c) => r === er && c === ec ? 'E' : v === 'E' ? '.' : v).join(''));
    return {board, position: state.position.slice(), exit: state.exit.slice(), moves: state.moves,
      won: state.won, legalActions: legalActions(state)};
  }
  function solve(state) {
    // The exit moves, so a search position is the ball and the exit together.
    const key = s => `${s.position}|${s.exit}`;
    const queue = [{state, path: []}], seen = new Set([key(state)]);
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i];
      if (item.state.won) return item.path;
      for (const action of legalActions(item.state)) {
        const next = step(item.state, action);
        if (!seen.has(key(next))) {
          seen.add(key(next)); queue.push({state: next, path: [...item.path, action]});
        }
      }
    }
    return null;
  }
  function placeRoadblock(board, random = Math.random, avoid = null) {
    // A board that already has a roadblock keeps it, so an exchanged code plays the same puzzle.
    const initial = create(board), path = solve(initial);
    if (board.join('').includes('X') || path === null) return board.slice();
    // Candidates are the floor squares the ball slides across on the current shortest route.
    const onRoute = new Map();
    path.reduce((s, action) => {
      for (const [r, c] of slide(s, action)) if (board[r][c] === '.') onRoute.set(`${r},${c}`, [r, c]);
      return step(s, action);
    }, initial);
    const shuffle = cells => {
      const out = cells.slice();
      for (let i = out.length - 1; i > 0; i--) {
        const j = Math.floor(random() * (i + 1));[out[i], out[j]] = [out[j], out[i]];
      }
      return out;
    };
    // A square to avoid (the previous roadblock) is tried last, so a reroll moves it when it can.
    const ordered = cells => {
      const out = shuffle(cells), i = avoid ? out.findIndex(([r, c]) => r === avoid[0] && c === avoid[1]) : -1;
      return i < 0 ? out : [...out.slice(0, i), ...out.slice(i + 1), out[i]];
    };
    const withBlock = ([r, c]) => board.map((row, i) => i === r ? row.slice(0, c) + 'X' + row.slice(c + 1) : row);
    const floor = [];
    board.forEach((row, r) => [...row].forEach((v, c) => { if (v === '.' && !onRoute.has(`${r},${c}`)) floor.push([r, c]); }));
    // Prefer a route square that breaks the old route, then any route square, then any floor square.
    // Never leave the board unsolvable.
    const solvable = b => solve(create(b)) !== null;
    const breaks = b => !path.reduce((s, action) => step(s, action), create(b)).won;
    const route = ordered([...onRoute.values()]).map(withBlock);
    // An off-route square never touches a slide on the route, so the last check is only a guard.
    const chosen = route.find(b => breaks(b) && solvable(b)) || route.find(solvable) ||
      ordered(floor).map(withBlock).find(solvable);
    return chosen || board.slice();
  }
  const api = {create, step, legalActions, observe, solve, placeRoadblock};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.GetOut = api;
})(globalThis);
