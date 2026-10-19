(function () {
  'use strict';
  const $ = id => document.getElementById(id), game = GetOut, levels = GetOutLevels;
  const arrows = {up:'↑',right:'→',down:'↓',left:'←'};
  const deltas = {up:[-1,0],right:[0,1],down:[1,0],left:[0,-1]};
  let levelIndex = 0, state, history = [], trace = [], hints = 0, editing = false, draft;
  let title = '', prompt = '', initialBoard, baseBoard, swapTimer;
  for (const [i,level] of levels.entries()) {
    const option = document.createElement('option'); option.value = i;
    option.textContent = `${i+1}. ${level.name}`; $('levels').append(option);
  }
  const customOption=document.createElement('option');customOption.value='custom';customOption.textContent='Your puzzle';customOption.disabled=true;$('levels').append(customOption);
  function announce(message) { $('status').textContent = message; }
  const blockCells = board => board.flatMap((row,r)=>[...row].flatMap((v,c)=>v==='X'?[[r,c]]:[]));
  // A fresh roadblock lands on the current shortest way out; Reset keeps it so retries are comparable.
  function start(base, name, thought, index, avoid) {
    baseBoard=base.slice();load(game.placeRoadblock(base,Math.random,avoid),name,thought,index);
  }
  const authored=()=>baseBoard.join('').includes('X');
  function load(board, name, thought, index) {
    finishSwap();state=game.create(board);initialBoard=board.slice();history=[];trace=[];hints=0;
    title=name;prompt=thought;levelIndex=index;editing=false;
    customOption.disabled=index!==null;$('levels').value=index===null?'custom':String(index);
    renderBoard();refresh();
    const blocks=blockCells(board).map(([r,c])=>`row ${r+1}, column ${c+1}`).join(' and ');
    announce(`${blocks?`A no-entry roadblock closes ${blocks}. `:''}Choose a direction. Miss the door and you swap places with it.`);
  }
  function refresh(slideEnd) {
    $('level-number').textContent=editing?'PUZZLE WORKSHOP':levelIndex===null?'YOUR PUZZLE':`PUZZLE ${String(levelIndex+1).padStart(2,'0')} / ${String(levels.length).padStart(2,'0')}`;
    $('level-title').textContent=editing?'Design a way out':title;$('moves').textContent=state.moves;
    $('prompt').textContent=prompt;$('editor').hidden=!editing;$('edit').hidden=editing;
    $('undo').disabled=editing||history.length===0;$('reset').disabled=editing;
    $('hint').disabled=editing||state.won;$('reroll').hidden=editing||authored();$('next').hidden=editing||!state.won||levelIndex===null||levelIndex===levels.length-1;
    document.querySelectorAll('[data-move]').forEach(b=>b.disabled=editing||state.won);
    $('levels').disabled=editing;
    // Before a swap, show the ball where it stopped and the exit where it was; then trade places.
    const place=(token,[r,c])=>{if(token){token.style.setProperty('--x',c);token.style.setProperty('--y',r);}};
    place($('board').querySelector('.player'),slideEnd||state.position);
    place($('board').querySelector('.exit-token'),slideEnd?state.position:state.exit);
    if(!editing)$('board').querySelectorAll('.cell').forEach((cell,i)=>{
      const r=Math.floor(i/state.board[0].length),c=i%state.board[0].length;
      cell.setAttribute('aria-label',`Row ${r+1}, column ${c+1}: ${r===state.exit[0]&&c===state.exit[1]?'exit':cell.dataset.description}`);
    });
    $('board').setAttribute('aria-label',editing?'Puzzle editor. Choose a paint tool, then select a square.':`Puzzle board, ${state.board.length} rows and ${state.board[0].length} columns. You are at row ${state.position[0]+1}, column ${state.position[1]+1}. The exit is at row ${state.exit[0]+1}, column ${state.exit[1]+1}. Arrow keys move.`);
    const list=$('trace-list');list.replaceChildren();
    if(!trace.length){const li=document.createElement('li');li.textContent='No moves yet.';list.append(li);}
    for(const event of trace){const li=document.createElement('li');li.textContent=event.type==='move'?`${arrows[event.action]} ${event.action}: (${event.from[0]+1}, ${event.from[1]+1}) → (${(event.swapped?event.exit:event.to)[0]+1}, ${(event.swapped?event.exit:event.to)[1]+1})${event.blocked?' · blocked':''}${event.roadblock?' by roadblock':''}${event.swapped?` · swap: you (${event.to[0]+1}, ${event.to[1]+1}), exit (${event.exit[0]+1}, ${event.exit[1]+1})`:''}${event.won?' · escaped':''}`:event.type==='hint'?`Hint requested: ${event.message}`:'Undid the previous move.';list.append(li);}
  }
  function renderBoard() {
    const board=$('board'), rows=editing?draft:state.board;
    board.replaceChildren();board.classList.toggle('editing',editing);
    board.style.setProperty('--rows',rows.length);board.style.setProperty('--cols',rows[0].length);
    for(let r=0;r<rows.length;r++)for(let c=0;c<rows[r].length;c++){
      const value=rows[r][c],cell=document.createElement(editing?'button':'span');
      cell.className=`cell ${value==='#'?'wall':value==='X'?'roadblock':editing&&value==='E'?'exit':''}`;
      const description=value==='#'?'wall':value==='X'?'no-entry roadblock':value==='E'&&editing?'exit':value==='S'?'start':'floor';
      cell.dataset.description=description;cell.setAttribute('aria-label',`Row ${r+1}, column ${c+1}: ${description}`);
      if(editing&&value==='E'){const door=document.createElement('span');door.className='door';door.textContent='↗';door.setAttribute('aria-hidden','true');cell.append(door);}
      if(value==='X'){const sign=document.createElement('span');sign.className='no-entry';sign.setAttribute('aria-hidden','true');cell.append(sign);}
      if(value==='S'){const mark=document.createElement('span');mark.className='start-mark';mark.textContent='×';mark.setAttribute('aria-hidden','true');cell.append(mark);}
      if(editing)cell.addEventListener('click',()=>{
        const tool=document.querySelector('input[name=tool]:checked').value;
        if(tool==='S'||tool==='E'||tool==='X')draft=draft.map(row=>row.map(v=>v===tool?'.':v));
        draft[r][c]=tool;renderBoard();refresh();
        $('board').children[r*rows[0].length+c].focus({preventScroll:true});
        announce(`${description} changed. Choose Check & play when your board is ready.`);
      });
      board.append(cell);
    }
    if(!editing){const exit=document.createElement('div');exit.className='exit-token';exit.setAttribute('aria-hidden','true');const door=document.createElement('span');door.className='door';door.textContent='↗';exit.append(door);board.append(exit);}
    if(!editing){const player=document.createElement('div');player.className='player';player.setAttribute('aria-hidden','true');const dot=document.createElement('span');dot.textContent='••';player.append(dot);board.append(player);}
  }
  function finishSwap(){clearTimeout(swapTimer);swapTimer=null;}
  function move(action) {
    // Input waits for the swap to finish, so every move starts from the position on screen.
    if(editing||state.won||swapTimer)return;
    const previous=state,next=game.step(state,action),swapped=next!==previous&&!next.won;
    // Was the slide (or the blocked attempt) stopped by the roadblock rather than a wall or the edge?
    const stop=next===previous?previous.position:next.exit,[dr,dc]=deltas[action];
    const roadblock=!next.won&&previous.board[stop[0]+dr]?.[stop[1]+dc]==='X';
    trace.push({type:'move',action,from:previous.position.slice(),to:next.position.slice(),exit:next.exit.slice(),swapped,blocked:next===previous,roadblock,won:next.won});
    if(next!==previous){history.push(previous);state=next;}
    if(swapped){refresh(state.exit);swapTimer=setTimeout(()=>{swapTimer=null;refresh();},matchMedia('(prefers-reduced-motion: reduce)').matches?0:260);}
    else refresh();
    if(state.won)announce(`You got out in ${state.moves} moves${hints?`, with ${hints} hint${hints===1?'':'s'}`:''}. What made the route click?`);
    else if(next===previous)announce(`Blocked ${action}${roadblock?' by the roadblock':''}. Try another direction; your move count stays the same.`);
    else announce(`Slid ${action} and stopped at row ${state.exit[0]+1}, column ${state.exit[1]+1}. Swap! You are now at row ${state.position[0]+1}, column ${state.position[1]+1}; the exit waits where you stopped.${roadblock?' The roadblock stopped your slide.':''}`);
  }
  document.querySelectorAll('[data-move]').forEach(b=>b.addEventListener('click',()=>move(b.dataset.move)));
  document.addEventListener('keydown',e=>{
    if(editing||e.repeat||e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,textarea,select,summary,.workshop-guide'))return;
    const action={ArrowUp:'up',ArrowRight:'right',ArrowDown:'down',ArrowLeft:'left',w:'up',d:'right',s:'down',a:'left'}[e.key];
    if(action){e.preventDefault();move(action);}
  });
  let startTouch=null;
  $('board').addEventListener('pointerdown',e=>{if(!editing&&e.pointerType!=='mouse')startTouch={x:e.clientX,y:e.clientY};});
  $('board').addEventListener('pointerup',e=>{
    if(!startTouch)return;const dx=e.clientX-startTouch.x,dy=e.clientY-startTouch.y;startTouch=null;
    if(Math.max(Math.abs(dx),Math.abs(dy))>20)move(Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up'));
  });
  $('board').addEventListener('pointercancel',()=>startTouch=null);
  $('undo').addEventListener('click',()=>{if(history.length){finishSwap();state=history.pop();trace.push({type:'undo'});refresh();announce('Move undone. Try another route.');}});
  $('reset').addEventListener('click',()=>load(initialBoard,title,prompt,levelIndex));
  $('reroll').addEventListener('click',()=>start(baseBoard,title,prompt,levelIndex,blockCells(initialBoard)[0]));
  $('hint').addEventListener('click',()=>{
    const path=game.solve(state);hints++;
    const message=path===null?'There is no route from here. Undo a move or reset.':`Try ${arrows[path[0]]} ${path[0]}.`;
    trace.push({type:'hint',message});refresh();announce(message);
  });
  function loadLevel(i){const level=levels[i];start(level.board,level.name,level.prompt,i);}
  $('next').addEventListener('click',()=>loadLevel(levelIndex+1));
  $('levels').addEventListener('change',e=>{if(e.target.value!=='custom')loadLevel(Number(e.target.value));});
  $('edit').addEventListener('click',()=>{editing=true;draft=baseBoard.map(row=>row.split(''));renderBoard();refresh();announce('Choose a tool and tap a square. Your current game is kept until you play the new board.');});
  $('cancel-edit').addEventListener('click',()=>{editing=false;renderBoard();refresh();announce('Back to your puzzle.');});
  $('blank').addEventListener('click',()=>{draft=Array.from({length:7},()=>Array(7).fill('.'));draft[0][0]='S';draft[6][6]='E';renderBoard();refresh();announce('A fresh 7 × 7 board. Add walls to make a route.');});
  function loadCustom(rows){
    const candidate=game.create(rows);
    if(game.solve(candidate)===null)throw new Error('This board has no route to the exit. Change a wall, roadblock, start, or exit and try again.');
    start(rows,'Your puzzle','What will your partner discover?',null);
    announce(`Your board has a route to the exit${blockCells(initialBoard).length?', even with the roadblock':', but no square could take a roadblock without trapping you'}. ${$('status').textContent}`);
  }
  $('play-custom').addEventListener('click',()=>{try{loadCustom(draft.map(row=>row.join('')));}catch(e){announce(e.message);}});
  $('export').addEventListener('click',()=>{
    $('board-code').value=(editing?draft.map(row=>row.join('')):initialBoard).join('\n');
    $('board-code').focus();$('board-code').select();announce('Board code selected. Copy it and send it to your partner.');
  });
  $('import').addEventListener('click',()=>{try{loadCustom($('board-code').value.trim().split(/\r?\n/).map(row=>row.trim()));}catch(e){announce(e.message);}});
  $('download').addEventListener('click',()=>{
    const payload={format:'get-out-roadblock-trace-v1',board:initialBoard,roadblocks:blockCells(initialBoard),roadblockSource:authored()?'authored':'random',events:trace,moves:state.moves,hints,outcome:state.won?'escaped':'in_progress',position:state.position,exit:state.exit};
    const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='get-out-trace.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  document.querySelectorAll('[data-guide]').forEach(button=>button.addEventListener('click',()=>{
    const guide=$(button.dataset.guide);
    guide.open=true;
    guide.querySelector('summary').focus({preventScroll:true});
    guide.scrollIntoView({block:'start'});
  }));
  loadLevel(0);
})();
