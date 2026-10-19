window.ICONS={
 safe:`<svg viewBox="0 0 64 64"><defs><linearGradient id="sf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6b7383"/><stop offset="1" stop-color="#2a2f38"/></linearGradient></defs>
   <rect x="6" y="6" width="52" height="50" rx="6" fill="url(#sf)" stroke="#11141a" stroke-width="2"/><rect x="11" y="11" width="42" height="40" rx="4" fill="#1b1f27" stroke="#8b94a5"/>
   <circle cx="32" cy="31" r="12" fill="#3a404c" stroke="#f2c14e" stroke-width="2.5"/><circle cx="32" cy="31" r="3" fill="#f2c14e"/>
   ${[0,45,90,135,180,225,270,315].map(a=>`<line x1="32" y1="31" x2="${32+10*Math.cos(a*Math.PI/180)}" y2="${31+10*Math.sin(a*Math.PI/180)}" stroke="#f2c14e" stroke-width="1.4"/>`).join('')}
   <rect x="12" y="56" width="8" height="5" fill="#11141a"/><rect x="44" y="56" width="8" height="5" fill="#11141a"/>
   <g transform="translate(36 34) rotate(-12)"><rect x="0" y="0" width="26" height="14" rx="2" fill="#2f9e58" stroke="#0e3d1f"/><rect x="0" y="5" width="26" height="4" fill="#f2c14e"/></g>
   <g transform="translate(40 40) rotate(-4)"><rect x="0" y="0" width="24" height="13" rx="2" fill="#38b866" stroke="#0e3d1f"/><rect x="0" y="4.5" width="24" height="4" fill="#f2c14e"/><text x="12" y="11.5" font-family="Anton" font-size="7" fill="#0e3d1f" text-anchor="middle"></text></g></svg>`,
 building:`<svg viewBox="0 0 64 64"><defs><linearGradient id="bd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffb547"/><stop offset="1" stop-color="#b8410b"/></linearGradient></defs>
   <rect x="6" y="20" width="22" height="38" fill="#3a2a22" stroke="#120c08" stroke-width="1.5"/><rect x="26" y="6" width="32" height="52" fill="url(#bd)" stroke="#3b1504" stroke-width="1.5"/>
   ${[0,1,2,3,4].map(r=>[0,1,2].map(c=>`<rect x="${30+c*9}" y="${11+r*9}" width="6" height="6" fill="${(r+c)%3?'#ffe9b0':'#5a2408'}"/>`).join('')).join('')}
   ${[0,1,2].map(r=>`<rect x="10" y="${25+r*10}" width="5" height="6" fill="#ffcf7a"/><rect x="19" y="${25+r*10}" width="5" height="6" fill="#6b4a3a"/>`).join('')}
   <rect x="38" y="50" width="8" height="8" fill="#2a1206"/><rect x="2" y="57" width="60" height="3" fill="#1a1210"/></svg>`,
 shield:`<svg viewBox="0 0 64 64"><defs><linearGradient id="sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#48e08a"/><stop offset="1" stop-color="#127a3e"/></linearGradient></defs>
   <path d="M32 4 L56 12 V30 Q56 50 32 60 Q8 50 8 30 V12 Z" fill="url(#sh)" stroke="#063d1d" stroke-width="2"/>
   <path d="M32 10 L50 16 V30 Q50 45 32 53 Q14 45 14 30 V16 Z" fill="none" stroke="rgba(255,255,255,.35)"/>
   <rect x="19" y="24" width="26" height="14" rx="2" fill="#fff" opacity=".95"/><text x="32" y="35" font-family="Anton" font-size="10" text-anchor="middle" fill="#c21818">WARN</text>
   <line x1="15" y1="44" x2="49" y2="18" stroke="#e3262f" stroke-width="4.5" stroke-linecap="round"/></svg>`,
 shroom:`<svg viewBox="0 0 64 64"><path d="M14 22 h36 l-3 36 h-30 z" fill="#d9e6ee" opacity=".55" stroke="#9fb3c2"/><rect x="14" y="18" width="36" height="6" fill="#e3262f"/>
   <rect x="30" y="38" width="7" height="14" rx="3" fill="#f7ead2"/><path d="M19 40 Q33 18 47 40 Z" fill="#c8283a"/><circle cx="27" cy="34" r="2.6" fill="#fff"/><circle cx="35" cy="29" r="2.3" fill="#fff"/><circle cx="40" cy="36" r="2" fill="#fff"/>
   <rect x="20" y="44" width="5" height="9" rx="2" fill="#f7ead2"/><path d="M15 46 Q22 36 29 46 Z" fill="#a9324d"/><circle cx="21" cy="43" r="1.4" fill="#fff"/></svg>`,
 donate:`<svg viewBox="0 0 64 64"><defs><linearGradient id="dn" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7ef0ff"/><stop offset=".5" stop-color="#3a8bff"/><stop offset="1" stop-color="#7a2cff"/></linearGradient></defs>
   <polygon points="18,10 46,10 58,24 32,56 6,24" fill="url(#dn)" stroke="#1d1658" stroke-width="2"/><polygon points="6,24 58,24" stroke="#1d1658"/>
   <polyline points="6,24 58,24" fill="none" stroke="rgba(255,255,255,.7)" stroke-width="1.5"/><polyline points="18,10 24,24 32,56 40,24 46,10" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.5"/><polygon points="24,24 32,10 40,24" fill="rgba(255,255,255,.35)"/>
   <path d="M52 4 l2 5 5 2 -5 2 -2 5 -2-5 -5-2 5-2z" fill="#fff"/></svg>`,
 rifle:`<svg viewBox="8 8 48 48"><g transform="rotate(-30 32 32)">
   <rect x="2" y="28" width="22" height="8" rx="2" fill="#a8672f" stroke="#e0a060" stroke-width=".6"/><path d="M2 28 L2 40 L10 40 L14 36" fill="#4d2f17"/>
   <rect x="22" y="27" width="22" height="8" fill="#5b6270" stroke="#c9d1dc" stroke-width=".6"/><rect x="44" y="29" width="18" height="3.5" fill="#8a93a3"/>
   <rect x="28" y="35" width="5" height="10" rx="1" fill="#1a1c20" transform="rotate(10 30 35)"/><path d="M36 35 h6 l-2 12 h-5z" fill="#3a3e46"/>
   <rect x="27" y="22" width="14" height="5" rx="2" fill="#1a1c20"/><circle cx="41" cy="24.5" r="2.5" fill="#59a8ff"/><rect x="58" y="27" width="2" height="3" fill="#1a1c20"/></g></svg>`,
 vest:`<svg viewBox="0 0 64 64"><defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a6650"/><stop offset="1" stop-color="#2c3326"/></linearGradient></defs>
   <path d="M18 6 h8 q6 8 12 0 h8 l10 10 v40 q-24 6 -48 0 v-40z" fill="url(#vs)" stroke="#12160f" stroke-width="2"/>
   <rect x="14" y="30" width="12" height="10" rx="1.5" fill="#3d4636" stroke="#12160f"/><rect x="38" y="30" width="12" height="10" rx="1.5" fill="#3d4636" stroke="#12160f"/>
   <rect x="22" y="44" width="20" height="8" rx="1.5" fill="#3d4636" stroke="#12160f"/><rect x="24" y="18" width="16" height="7" rx="1" fill="#1b1f17"/><text x="32" y="24" font-family="Anton" font-size="6.5" text-anchor="middle" fill="#cfd6c4">ARMOR</text></svg>`,
 brain:`<svg viewBox="0 0 64 64"><defs><linearGradient id="bc2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff5fd2"/><stop offset="1" stop-color="#7a1bff"/></linearGradient></defs>
   <rect x="18" y="8" width="28" height="50" rx="7" fill="url(#bc2)" stroke="#2b0a4a" stroke-width="2"/><rect x="20" y="4" width="24" height="6" rx="2" fill="#c9c9d6"/>
   <path d="M24 30 q-4 -8 4 -10 q2 -5 8 -2 q6 -2 6 4 q5 3 1 8 q2 6 -4 7 q-3 4 -8 1 q-6 1 -7 -4 q-4 -1 0 -4z" fill="#ffd0f2" stroke="#7a1bff" stroke-width="1.4"/>
   <path d="M32 20 v19 M27 26 q3 2 5 0 M37 30 q-3 2 -5 0" stroke="#7a1bff" stroke-width="1.2" fill="none"/>
   <path d="M38 41 l-6 9 h5 l-3 7 8 -10 h-5 l3 -6z" fill="#fff36b"/></svg>`,
 medkit:`<svg viewBox="0 0 64 64"><rect x="24" y="8" width="16" height="8" rx="2" fill="none" stroke="#2a301f" stroke-width="3"/>
   <rect x="6" y="14" width="52" height="42" rx="6" fill="#5b6a3f" stroke="#1f2614" stroke-width="2"/><rect x="6" y="24" width="52" height="3" fill="#47542f"/>
   <rect x="26" y="28" width="12" height="24" rx="1.5" fill="#e3262f"/><rect x="20" y="34" width="24" height="12" rx="1.5" fill="#e3262f"/>
   <rect x="26" y="28" width="12" height="24" fill="none" stroke="#fff" stroke-width="1" opacity=".6"/></svg>`,
 defib:`<svg viewBox="0 0 64 64"><defs><linearGradient id="df" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd23a"/><stop offset="1" stop-color="#e08a00"/></linearGradient></defs>
   <rect x="6" y="12" width="52" height="44" rx="7" fill="url(#df)" stroke="#5a3400" stroke-width="2"/><rect x="22" y="6" width="20" height="8" rx="3" fill="#333"/>
   <path d="M32 50 C14 38 14 24 24 22 C29 21 32 26 32 26 C32 26 35 21 40 22 C50 24 50 38 32 50Z" fill="#2bb54a" stroke="#0b4a1a" stroke-width="1.5"/>
   <path d="M35 26 l-7 11 h5 l-3 9 9 -12 h-5 l3 -8z" fill="#fff"/><text x="32" y="20" font-family="Anton" font-size="6" text-anchor="middle" fill="#5a3400">AED</text></svg>`,
};
