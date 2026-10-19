function web(cx,cy,R,spokes,rings,start=0,end=90){
  let s='';const pts=[];
  for(let i=0;i<=spokes;i++){const a=(start+(end-start)*i/spokes)*Math.PI/180;pts.push(a);s+=`<line x1="${cx}" y1="${cy}" x2="${cx+R*Math.cos(a)}" y2="${cy+R*Math.sin(a)}"/>`}
  for(let r=1;r<=rings;r++){const rr=R*r/rings;let d='';pts.forEach((a,i)=>{const x=cx+rr*Math.cos(a),y=cy+rr*Math.sin(a);if(!i)d+=`M${x} ${y}`;else{const pa=(pts[i-1]+a)/2,c=rr*.82;d+=` Q${cx+c*Math.cos(pa)} ${cy+c*Math.sin(pa)} ${x} ${y}`}});s+=`<path d="${d}"/>`}
  return s;
}
