const {test}=require('node:test');
const assert=require('node:assert/strict');
const game=require('../engine.js');
const exploration=require('../exploration.js');
const board=['S..#.', '.....', '.#...', '...E.', '.....'];

test('records the start and successful endpoints, not crossed floor squares',()=>{
  const initial=game.create(board),stops=exploration.start(initial);
  const next=game.step(initial,'right'),visited=exploration.recordMove(stops,initial,next);
  assert.deepEqual([...visited],['0,0','0,2']);
  assert.equal(exploration.has(visited,[0,1]),false);
  assert.equal(exploration.has(visited,[0,3]),false);
  assert.deepEqual([...stops],['0,0']);
  assert.deepEqual(initial.position,[0,0]);
});

test('blocked moves and revisiting a stop do not add duplicates or change scoring',()=>{
  let state=game.create(board),stops=exploration.start(state);
  for(const action of ['up','right','left','right']){
    const next=game.step(state,action);stops=exploration.recordMove(stops,state,next);state=next;
  }
  assert.deepEqual([...stops],['0,0','0,2']);
  assert.equal(state.moves,3);
});

test('exploration can outlive undo and records a newly chosen branch',()=>{
  const initial=game.create(board),right=game.step(initial,'right');
  let stops=exploration.recordMove(exploration.start(initial),initial,right);
  // Undo restores the initial game state while retaining its exploration set.
  const down=game.step(initial,'down');
  stops=exploration.recordMove(stops,initial,down);
  assert.deepEqual([...stops],['0,0','0,2','4,0']);
  assert.equal(down.moves,1);
});

test('a reset or another board starts an independent exploration record',()=>{
  const initial=game.create(board),right=game.step(initial,'right');
  const old=exploration.recordMove(exploration.start(initial),initial,right);
  assert.deepEqual([...exploration.start(game.create(board))],['0,0']);
  assert.deepEqual([...exploration.start(game.create(['..S','...','E..']))],['0,2']);
  assert.deepEqual([...old],['0,0','0,2']);
});

test('a mid-slide exit is a visited stop and terminal actions add nothing',()=>{
  const initial=game.create(['S.E..','.....','.....']),won=game.step(initial,'right');
  const stops=exploration.recordMove(exploration.start(initial),initial,won);
  assert.deepEqual([...stops],['0,0','0,2']);
  assert.equal(won.won,true);
  assert.equal(exploration.recordMove(stops,won,game.step(won,'down')),stops);
});
