(function(root){
 const levels = [
  {name:'Find your feet', prompt:'A wall can give you somewhere to stop.', board:['S#.#..#','.....#.','#.##...','....E..','....#..','..#.#..','#....#.']},
  {name:'Take the long way', prompt:'Being near the door is only part of the problem.', board:['S..#...','...#...','.......','..##E..','#......','.....##','#....#.']},
  {name:'Change direction', prompt:'Which stopping point opens a new route?', board:['S#.....','.....##','...#.#.','..#.E.#','.......','.......','...#...']},
  {name:'A useful detour', prompt:'Make a prediction before each move.', board:['S......','.###.#.','#......','....E#.','.......','.......','..#....']},
  {name:'Across the wall', prompt:'Enter blue, emerge from orange, and stop. Choose a new direction from there.', board:['S..#...','...#...','..B#...','####...','####O..','####..E','####...']},
  {name:'Find the approach', prompt:'The orange portal is a way in, too. Which stopping point lines you up with it?', board:['#...O#.','.......','..###.#','#....E.','..###B.','.....##','......S']},
  {name:'There and back', prompt:'Both colors work in both directions. A portal can be useful more than once.', board:['...#...','..#.#.#','#......','#.S.#..','.#.#.#.','..#EB..','#O##...']},
  {name:'The last connection', prompt:'Combine detours and both portals. Predict where each slide will stop.', board:['.....#.','...E...','.....#.','....#O.','#.....B','..#....','.#S....']}
 ];
 if(typeof module!=='undefined'&&module.exports)module.exports=levels;else root.GetOutLevels=levels;
})(globalThis);
