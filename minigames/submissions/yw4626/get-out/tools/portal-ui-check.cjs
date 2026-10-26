// Optional browser-free UI checks. The game has no jsdom runtime dependency.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {JSDOM}=require(process.env.GETOUT_JSDOM||'jsdom');
const root=path.resolve(__dirname,'..');
const dom=new JSDOM(fs.readFileSync(path.join(root,'index.html'),'utf8'),{runScripts:'outside-only'});
const w=dom.window,d=w.document,$=id=>d.getElementById(id);let errors=[];
w.addEventListener('error',event=>errors.push(event.error));
w.HTMLElement.prototype.scrollIntoView=function(){};
w.setTimeout=fn=>setTimeout(fn,0);
for(const file of ['engine.js','levels.js','app.js'])w.eval(fs.readFileSync(path.join(root,file),'utf8'));
const click=id=>$(id).click(),choose=i=>{$('levels').value=String(i);$('levels').dispatchEvent(new w.Event('change'));};
const move=direction=>d.querySelector(`[data-move=${direction}]`).click();
const boardLabel=()=>$('board').getAttribute('aria-label');let groups=0;
function check(name,fn){fn();groups++;console.log('PASS '+name);}
check('eight puzzles; blue and orange cells are labeled and absent in original puzzles',()=>{
 assert.equal($('levels').options.length,9);assert.equal(d.querySelectorAll('.portal-ring').length,0);
 choose(4);assert.equal(d.querySelectorAll('.blue-portal').length,1);assert.equal(d.querySelectorAll('.orange-portal').length,1);
 assert.match(d.querySelector('.blue-portal').getAttribute('aria-label'),/blue portal/);assert.equal($('portal-rules').hidden,false);
});
check('all eight routes complete using UI controls and portal-aware hints',()=>{
 for(let i=0;i<8;i++){
  choose(i);const path=w.GetOut.solve(w.GetOut.create(w.GetOutLevels[i].board));
  const target=[3,5,7,9,4,6,8,10][i];assert.equal(Number($('minimum-moves').textContent),target);
  for(const action of path){click('hint');assert.ok($('status').textContent.includes(action));move(action);}
  assert.match($('status').textContent,/You got out/);assert.equal(Number($('moves').textContent),path.length);
  assert.equal(Number($('minimum-moves').textContent),target);assert.match($('minimum-feedback').textContent,/Perfect route/);
 }
});
check('minimum target stays fixed, reports extra moves and handles reset and custom boards',()=>{
 choose(0);move('down');move('up');
 for(const action of w.GetOut.solve(w.GetOut.create(w.GetOutLevels[0].board)))move(action);
 assert.equal($('minimum-moves').textContent,'3');assert.match($('minimum-feedback').textContent,/2 moves above/);
 click('undo');assert.doesNotMatch($('minimum-feedback').textContent,/above/);click('reset');assert.equal($('minimum-moves').textContent,'3');
 $('board-code').value='SE\n..';click('import');assert.equal($('minimum-moves').textContent,'1');
 click('edit');assert.equal($('minimum-card').hidden,true);click('cancel-edit');assert.equal($('minimum-card').hidden,false);
});
check('portal transfer, undo and reset preserve the expected position and count',()=>{
 choose(4);move('down');const before=boardLabel();move('right');assert.match($('status').textContent,/Portal transfer/);
 assert.equal($('board').classList.contains('portal-transfer'),true);click('undo');assert.equal(boardLabel(),before);assert.equal($('moves').textContent,'1');
 click('reset');assert.equal($('moves').textContent,'0');assert.match(boardLabel(),/row 1, column 1/);
});
check('portal exchange round trip and malformed pair rejection preserve the game',()=>{
 choose(6);move('up');click('export');const code=$('board-code').value;assert.match(code,/B/);assert.match(code,/O/);
 click('import');assert.equal($('moves').textContent,'0');assert.equal($('levels').value,'custom');
 const before=boardLabel();$('board-code').value=code.replace('B','.');click('import');assert.match($('status').textContent,/one blue/);assert.equal(boardLabel(),before);
 $('board-code').value=code;
});
check('editor preserves portals, enforces pairs and can create a classic board',()=>{
 click('edit');assert.equal($('watch').disabled,true);assert.equal(d.querySelectorAll('.portal-ring').length,2);
 d.querySelector('input[name=tool][value="."]').checked=true;d.querySelector('.blue-portal').click();click('play-custom');assert.match($('status').textContent,/one blue/);assert.equal($('editor').hidden,false);
 click('cancel-edit');assert.equal(d.querySelectorAll('.portal-ring').length,2);
 click('edit');click('blank');click('play-custom');assert.equal(d.querySelectorAll('.portal-ring').length,0);
});
async function finish(){
 choose(7);move('right');const saved=boardLabel(),trace=$('trace-list').textContent;
 click('watch');const deadline=Date.now()+5000;
 while($('watch').disabled&&Date.now()<deadline)await new Promise(r=>setTimeout(r,10));
 check('visible solution completes and restores progress and history',()=>{
  assert.match($('watch-status').textContent,/Solved in 10 moves/);assert.equal(boardLabel(),saved);assert.equal($('trace-list').textContent,trace);
  click('undo');assert.equal($('moves').textContent,'0');
 });
 const cancelled=boardLabel();click('watch');click('stop-watch');await new Promise(r=>setTimeout(r,30));
 check('stopping a solution restores controls and original position',()=>{
  assert.equal($('watch').disabled,false);assert.equal($('levels').disabled,false);assert.equal(boardLabel(),cancelled);assert.match($('watch-status').textContent,/Stopped/);assert.equal(errors.length,0);
 });
 console.log(`${groups} DOM groups passed; rendered layout and touch input are not verified.`);dom.window.close();
}
finish().catch(e=>{console.error(e);process.exitCode=1;dom.window.close();});
