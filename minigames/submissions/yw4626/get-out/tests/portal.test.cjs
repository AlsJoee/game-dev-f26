const test=require('node:test'),assert=require('node:assert/strict');
const g=require('../engine.js');
const board=['S.B..','.###.','O...E'];
test('blue transfers to orange and stops; the next slide leaves normally',()=>{
 const start=g.create(board),before=JSON.stringify(start),next=g.step(start,'right');
 assert.deepEqual(next.position,[2,0]);assert.equal(next.moves,1);assert.equal(next.won,false);assert.equal(JSON.stringify(start),before);
 const won=g.step(next,'right');assert.equal(won.won,true);assert.equal(won.moves,2);
 assert.equal(g.step(won,'up'),won);
});
test('orange transfers to blue; reentry transfers again rather than bouncing forever',()=>{
 const s=g.create(board),atBlue=g.step(s,'down');assert.deepEqual(atBlue.position,[0,2]);
 const edge=g.step(atBlue,'right');assert.deepEqual(edge.position,[0,4]);
 assert.deepEqual(g.step(edge,'left').position,[2,0]);
});
test('blocked and unknown actions on a portal preserve the state',()=>{
 const s=g.step(g.create(board),'right');assert.equal(g.step(s,'left'),s);
 assert.throws(()=>g.step(s,'wait'),/Unknown/);assert.deepEqual(s.position,[2,0]);assert.equal(s.moves,1);
});
test('validation rejects incomplete or duplicated pairs and detached observations cannot edit the board',()=>{
 for(const rows of [['SBE','...'],['SOE','...'],['SBBOE','.....']])assert.throws(()=>g.create(rows),/one blue.*one orange/i);
 const s=g.create(board),o=g.observe(s);o.board[0]='.....';o.position[0]=99;assert.equal(s.board[0],board[0]);assert.deepEqual(s.position,[0,0]);
 assert.ok(!('solution' in o));
});
test('solver understands portals and exits before a later portal',()=>{
 const s=g.create(board);assert.deepEqual(g.solve(s),['right','right']);
 assert.equal(g.step(g.create(['SEBO','....']),'right').won,true);
});
test('a trip through a portal back to the current square still costs one move',()=>{
 const s=g.step(g.create(['SBOE','....']),'right'),next=g.step(s,'left');
 assert.deepEqual(next.position,s.position);assert.equal(next.moves,s.moves+1);assert.notEqual(next,s);
});
test('campaign preserves the four original puzzles exactly and adds four essential portal puzzles',()=>{
 const levels=require('../levels.js'),original=require('../../../../get-out/levels.js');
 assert.equal(levels.length,8);assert.deepEqual(levels.slice(0,4),original);
 const lengths=[],transfers=[];
 for(const l of levels.slice(4)){
  let state=g.create(l.board);const path=g.solve(state);assert.ok(path);lengths.push(path.length);
  assert.equal(g.solve(g.create(l.board.map(row=>row.replace(/[BO]/g,'.')))),null);
  let count=0;for(const action of path){state=g.step(state,action);if(/[BO]/.test(state.board[state.position[0]][state.position[1]]))count++;}
  assert.equal(state.won,true);transfers.push(count);
 }
 assert.deepEqual(lengths,[4,6,8,10]);assert.deepEqual(transfers,[1,1,2,2]);
});
