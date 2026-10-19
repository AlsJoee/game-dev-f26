const {test}=require('node:test');
const assert=require('node:assert/strict');
const game=require('../engine.js');
const board=['S..#.', '.....', '.#...', '...E.', '.....'];
test('slides to a wall or border, then swaps with the exit, without mutating the input',()=>{
 const s=game.create(board);const next=game.step(s,'right');
 // Slid to (0,2), missed the exit, so the ball continues from the old exit and the exit waits at (0,2).
 assert.deepEqual(next.position,[3,3]);assert.deepEqual(next.exit,[0,2]);assert.equal(next.moves,1);
 assert.deepEqual(s.position,[0,0]);assert.deepEqual(s.exit,[3,3]);assert.equal(s.moves,0);
 const down=game.step(s,'down');assert.deepEqual(down.position,[3,3]);assert.deepEqual(down.exit,[4,0]);
});
test('the next move is played from the exit side and swaps again',()=>{
 const s=game.step(game.create(board),'right');const next=game.step(s,'up');
 // From (3,3) the ball stops under the wall at (1,3); the exit at (0,2) is not crossed.
 assert.deepEqual(next.position,[0,2]);assert.deepEqual(next.exit,[1,3]);assert.equal(next.moves,2);
});
test('blocked and unknown actions do not spend moves or swap',()=>{
 const s=game.create(board);assert.deepEqual(game.step(s,'up'),s);
 assert.throws(()=>game.step(s,'teleport'),/direction/i);
 // After two swaps the ball is at (0,2) under the border and beside a wall.
 const swapped=['right','up'].reduce((s,a)=>game.step(s,a),s);
 assert.equal(game.step(swapped,'up'),swapped);assert.equal(game.step(swapped,'right'),swapped);
 assert.deepEqual(game.legalActions(swapped),['down','left']);
});
test('the original exit square is plain floor once the exit has moved',()=>{
 const s=['right','up','down','down'].reduce((s,a)=>game.step(s,a),game.create(board));
 // The last slide crosses the starting E square at (3,3) without winning.
 assert.equal(s.won,false);assert.deepEqual(s.position,[4,2]);assert.deepEqual(s.exit,[4,3]);assert.equal(s.moves,4);
});
test('reaching an exit mid-slide wins and terminal states cannot move',()=>{
 const s=game.create(['S.E..','.....','.....']);
 const won=game.step(s,'right');assert.deepEqual(won.position,[0,2]);assert.deepEqual(won.exit,[0,2]);
 assert.equal(won.won,true);assert.deepEqual(game.step(won,'down'),won);
});
test('solver plans across swaps and identifies unreachable exits',()=>{
 // Reference answer was right, down. After right the ball swaps into the corner exit and must go up.
 assert.deepEqual(game.solve(game.create(['S..','...','..E'])),['right','up']);
 // Unreachable under the reference rules; the swap makes the centre exit reachable in three moves.
 const centre=game.create(['S..','.E.','...']),path=game.solve(centre);
 assert.equal(path.length,3);assert.equal(path.reduce((s,a)=>game.step(s,a),centre).won,true);
 // A walled-in exit traps the ball after the first swap.
 assert.equal(game.solve(game.create(['S..','.##','.#E'])),null);
 // A walled-in start has no first move at all.
 assert.equal(game.solve(game.create(['S#.','#..','..E'])),null);
});
test('invalid imported boards fail before play',()=>{
 for(const b of [[],['S.E','..'],['SSE'],['S..'],['S?E'],['S.E',42],Array(21).fill('S.E')]){
  assert.throws(()=>game.create(b));
 }
});
test('observations are detached, show the moving exit, and legal actions follow actual movement',()=>{
 const s=game.create(board);assert.deepEqual(game.legalActions(s),['right','down']);
 const obs=game.observe(s);assert.deepEqual(obs.exit,[3,3]);assert.equal(obs.board[3],'...E.');
 obs.position[0]=99;obs.exit[0]=99;obs.board[0]='broken';
 assert.deepEqual(s.position,[0,0]);assert.deepEqual(s.exit,[3,3]);assert.equal(s.board[0],board[0]);
 // The observed board letters follow the moving exit, so no stale door is shown.
 const after=game.observe(game.step(s,'right'));assert.deepEqual(after.exit,[0,2]);
 assert.deepEqual(after.board,['S.E#.', '.....', '.#...', '.....', '.....']);
});
// Seeded stand-in for Math.random, so roadblock placement is repeatable in tests.
function seeded(seed){return()=>{seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const roadblocks=b=>b.flatMap((row,r)=>[...row].flatMap((v,c)=>v==='X'?[[r,c]]:[]));
test('a roadblock stops a slide like a wall, and the swap still happens',()=>{
 const s=game.create(['S.X#.', '.....', '.#...', '...E.', '.....']);const next=game.step(s,'right');
 // The ball stops in front of the roadblock at (0,1), then swaps with the exit.
 assert.deepEqual(next.position,[3,3]);assert.deepEqual(next.exit,[0,1]);assert.equal(next.moves,1);
 // From the exit side, sliding up stops under the wall at (1,3); the roadblock never moves.
 const up=game.step(next,'up');assert.deepEqual(up.position,[0,1]);assert.deepEqual(up.exit,[1,3]);
 assert.equal(up.board[0],'S.X#.');
});
test('moving into a roadblock is blocked, and the solver routes around it',()=>{
 const s=game.create(['SX...','.....','....E']);
 assert.equal(game.step(s,'right'),s);assert.deepEqual(game.legalActions(s),['down']);
 // Without the roadblock this is one move; with it the ball must go down first.
 assert.deepEqual(game.solve(game.create(['S...E','.....'])),['right']);
 const around=game.create(['S.X.E','.....']),path=game.solve(around);
 assert.ok(path.length>1);assert.equal(path.reduce((s,a)=>game.step(s,a),around).won,true);
 // Roadblocks can wall in an exit just as walls do.
 assert.equal(game.solve(game.create(['S..','.XX','.XE'])),null);
});
test('observations show the roadblock',()=>{
 const obs=game.observe(game.create(['S.X','..E']));
 assert.deepEqual(obs.board,['S.X','..E']);assert.deepEqual(obs.legalActions,['right','down']);
});
test('placeRoadblock blocks the shortest route on a floor square and keeps the board solvable',()=>{
 const input=['S.....','......','......','.....E'],copy=input.slice();
 const route=game.solve(game.create(input));
 for(let seed=1;seed<=50;seed++){
  const placed=game.placeRoadblock(input,seeded(seed)),blocks=roadblocks(placed);
  assert.equal(blocks.length,1);const [[r,c]]=blocks;assert.equal(input[r][c],'.');
  const state=game.create(placed),path=game.solve(state);
  assert.ok(path,`seed ${seed} left the board unsolvable`);
  assert.equal(path.reduce((s,a)=>game.step(s,a),state).won,true);
  // The old shortest route no longer reaches the exit.
  assert.equal(route.reduce((s,a)=>game.step(s,a),state).won,false,`seed ${seed}`);
 }
 assert.deepEqual(input,copy);
 // The same random sequence gives the same roadblock.
 assert.deepEqual(game.placeRoadblock(input,seeded(7)),game.placeRoadblock(input,seeded(7)));
});
test('placeRoadblock keeps an authored roadblock and leaves unsolvable boards alone',()=>{
 assert.deepEqual(game.placeRoadblock(['S.X','..E'],seeded(1)),['S.X','..E']);
 assert.deepEqual(game.placeRoadblock(['S..','.##','.#E'],seeded(1)),['S..','.##','.#E']);
 // Solvable, but a roadblock on any of its three floor squares would trap the ball: no roadblock.
 assert.notEqual(game.solve(game.create(['S#E','...'])),null);
 for(let seed=1;seed<=10;seed++)assert.deepEqual(game.placeRoadblock(['S#E','...'],seeded(seed)),['S#E','...']);
 // No floor square lies on the one-move route, so it falls back to another floor square.
 const placed=game.placeRoadblock(['SE','..'],seeded(3));
 assert.equal(roadblocks(placed).length,1);assert.notEqual(game.solve(game.create(placed)),null);
});
test('a reroll avoids the previous square when another one works',()=>{
 const levels=require('../levels.js');
 for(const level of levels)for(let seed=1;seed<=20;seed++){
  const first=roadblocks(game.placeRoadblock(level.board,seeded(seed)))[0];
  const again=game.placeRoadblock(level.board,seeded(seed+100),first),[next]=roadblocks(again);
  assert.notDeepEqual(next,first,`${level.name}, seed ${seed}`);
  assert.notEqual(game.solve(game.create(again)),null);
 }
 // With only one possible square, avoiding it still returns that square rather than none.
 const only=game.placeRoadblock(['SE','.#'],seeded(1));
 assert.deepEqual(game.placeRoadblock(['SE','.#'],seeded(2),roadblocks(only)[0]),only);
});
test('every teaching board gets a roadblock that breaks its old route and stays solvable',()=>{
 const levels=require('../levels.js');
 for(const level of levels){
  const route=game.solve(game.create(level.board));
  for(let seed=1;seed<=40;seed++){
   const placed=game.placeRoadblock(level.board,seeded(seed)),state=game.create(placed),path=game.solve(state);
   assert.equal(roadblocks(placed).length,1,level.name);
   assert.ok(path,`${level.name}, seed ${seed}`);
   assert.equal(path.reduce((s,a)=>game.step(s,a),state).won,true,level.name);
   assert.equal(route.reduce((s,a)=>game.step(s,a),state).won,false,`${level.name}, seed ${seed}`);
  }
 }
});
test('every teaching board is solvable and its solution reaches the exit',()=>{
 const levels=require('../levels.js');
 for(const level of levels){
  const initial=game.create(level.board),solution=game.solve(initial);
  assert.ok(solution && solution.length>0,level.name);
  const final=solution.reduce((s,a)=>game.step(s,a),initial);
  assert.equal(final.won,true,level.name);
 }
});
