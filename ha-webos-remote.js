/* LG webOS Remote for Home Assistant — independent MIT-licensed Home Assistant dashboard card.
 * Uses documented browser APIs and its own JSON protocol; no third-party UI source.
 */
const ICONS = {
  back: '<path d="m15 18-6-6 6-6"/><path d="M9 12h12"/>',
  home: '<path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9"/><path d="M9 21v-7h6v7"/>',
  keyboard: '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M6 9h.01M10 9h.01M14 9h.01M18 9h.01M6 12h.01M10 12h.01M14 12h.01M18 12h.01M7 16h10"/>',
  settings: '<path d="M4 7h16M4 12h16M4 17h16"/><circle cx="9" cy="7" r="2" fill="#1b2634"/><circle cx="16" cy="12" r="2" fill="#1b2634"/><circle cx="10" cy="17" r="2" fill="#1b2634"/>',
  power: '<path d="M12 2v10"/><path d="M6.6 5.5a9 9 0 1 0 10.8 0"/>',
  up: '<path d="m6 15 6-6 6 6"/>', down: '<path d="m6 9 6 6 6-6"/>',
  left: '<path d="m15 6-6 6 6 6"/>', right: '<path d="m9 6 6 6-6 6"/>',
  pageUp: '<path d="m7 13 5-5 5 5M7 19l5-5 5 5"/>',
  pageDown: '<path d="m7 5 5 5 5-5M7 11l5 5 5-5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>', minus: '<path d="M5 12h14"/>',
  mute: '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="m17 9 5 6m0-6-5 6"/>',
  volume: '<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15 9a5 5 0 0 1 0 6"/>',
  tv: '<rect x="2" y="4" width="20" height="15" rx="2"/><path d="M8 22h8M12 19v3"/>',
  pointer: '<path d="m4 3 6.5 17 2.6-6.5L20 11z"/>',
  globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a16 16 0 0 0 0 20M12 2a16 16 0 0 1 0 20"/>',
  youtube: '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z"/>',
  gallery: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1"/><path d="m4 17 5-5 4 4 3-3 4 4"/>',
  send: '<path d="m22 2-7 20-4-9-9-4 20-7ZM22 2 11 13"/>',
};
const svg = (key, size=20) => `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[key]||ICONS.tv}</svg>`;
const esc = text => String(text ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');
const ALIASES = ['netflix','internet','youtube','gallery'];

class LGWebOSRemoteCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({mode:'open'});
    this.config = null;
    this.ws = null;
    this.authenticated = false;
    this.tvOnline = false;
    this.appCatalog = [];
    this.keyboardOpen = false;
    this.speedMultiplier = 1;
    this.liveText = false;
    this.textComposing = false;
    this.liveTextTimer = null;
    this.pendingMessage = '';
    this.mousePointers = new Map();
    this.twoFinger = false;
    this.pendingMove = {x:0,y:0};
    this.pendingScroll = {x:0,y:0};
    this.frame = 0;
    this.repeatTimer = null;
    this.reconnectTimer = null;
  }
  static getStubConfig() {return {type:'custom:lg-webos-remote', name:'Living Room TV', url:'ws://homeassistant.local:8788', token:''};}
  static getConfigElement() {return undefined;} // YAML editor is supported in the dashboard.
  setConfig(config) {
    if (!config || !config.url || typeof config.url !== 'string') throw Error('LG webOS Remote: url is required');
    const url = new URL(config.url);
    if (!['ws:','wss:'].includes(url.protocol)) throw Error('LG webOS Remote: WebSocket ws:// or wss:// URL required');
    this.config = {name:'LG webOS TV',scrollSensitivity:1,...config};
    this._render();
    if (this.isConnected) this._connect();
  }
  set hass(value) {this._hass=value;}
  connectedCallback() {this.isConnected && this.config && this._connect();}
  disconnectedCallback() {this._disconnect();}
  _disconnect() {
    clearTimeout(this.reconnectTimer);
    this._stopRepeat();
    clearTimeout(this.liveTextTimer);
    if (this.frame) cancelAnimationFrame(this.frame);
    if (this.ws) {this.ws.onclose=null; this.ws.close(); this.ws=null;}
    this.authenticated=false;
  }
  _connect() {
    this._disconnect();
    this._setState('Connecting…');
    const ws = new WebSocket(this.config.url);
    this.ws = ws;
    ws.addEventListener('open',()=> {if(this.ws===ws) ws.send(JSON.stringify({type:'auth', token:this.config.token??''}));});
    ws.addEventListener('message',(ev)=>{
      if(this.ws!==ws)return;
      let msg;try{msg=JSON.parse(ev.data);}catch{return;}
      if(msg.type==='auth-ok') {this.authenticated=true;this._setState('Connected');this._send('apps');this._send('status');}
      if(msg.type==='status') {this.tvOnline=Boolean(msg.online);this._setState(this.tvOnline?'TV On':'TV Off · Wake ready');this._renderState();}
      if(msg.type==='apps') {this.appCatalog=Array.isArray(msg.apps)?msg.apps:[];this._renderAppStates();}
      if(msg.type==='notice') this._toast(msg.message||'');
      if(msg.type==='error') this._toast(msg.message||'Unsupported command');
    });
    ws.addEventListener('close',(event)=>{if(this.ws!==ws)return;this.authenticated=false;if(event.code===1008){this._setState('Invalid token');this._toast('Authentication rejected. Check the token in card YAML.');return;}this._setState('Disconnected');this.reconnectTimer=setTimeout(()=>this.isConnected&&this._connect(),5000);});
    ws.addEventListener('error',()=>this._setState('Connection error'));
  }
  _send(type, data={}) {
    if(!this.authenticated || this.ws?.readyState!==WebSocket.OPEN)return false;
    this.ws.send(JSON.stringify({type,...data}));return true;
  }
  _toast(message){const el=this.shadowRoot.querySelector('.notice'); if(!el)return;el.textContent=String(message).slice(0,140);el.hidden=false;clearTimeout(this.noticeTimer);this.noticeTimer=setTimeout(()=>el.hidden=true,4500);}
  _setState(text){let el=this.shadowRoot.querySelector('.connection');if(el)el.textContent=text;}
  _renderState(){const b=this.shadowRoot.querySelector('[data-command="power"]');if(b)b.title=this.tvOnline?'Power off':'Power on (Wake-on-LAN)';}
  _matchApp(alias){return this.appCatalog.find(a=>{
    const text=(a.title+' '+a.id).toLowerCase();
    return alias==='internet'?/browser|internet|web browser/.test(text):alias==='gallery'?/gallery|art gallery|gallery\+/.test(text):alias==='youtube'?/youtube/.test(text):/netflix/.test(text);
  });}
  _renderAppStates(){for(const alias of ALIASES){const b=this.shadowRoot.querySelector(`[data-app="${alias}"]`);if(b){const app=this._matchApp(alias);b.title=app?`Open ${app.title}`:`${alias} — not found on TV`;b.classList.toggle('unavailable',this.appCatalog.length>0&&!app);}}}
  _tap(command) {if(command==='power')this._send('power');else if(command==='keyboard'){this.keyboardOpen=!this.keyboardOpen;this._render();}else this._send('key',{key:command});}
  _app(alias){const app=this._matchApp(alias);if(!app){this._toast(`${alias} app not found. Check installed TV apps.`);return;}this._send('launch',{alias});}
  _sendText(){
    const field=this.shadowRoot.querySelector('.text-field');
    const text=field?.value??'';
    if(!text)return;
    clearTimeout(this.liveTextTimer);
    const sent=this._send('text',{text,replace:this.liveText});
    if(sent){
      if(!this.liveText)field.value='';
      this._toast(this.liveText?'Text synced (beta)':'Text sent to TV');
    }
  }
  _setSpeed(value){
    this.speedMultiplier=this.speedMultiplier===value?1:value;
    const speeds=this.shadowRoot.querySelectorAll('[data-speed]');
    speeds.forEach(b=>{const active=Number(b.dataset.speed)===this.speedMultiplier;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  }
  _setLiveText(){
    this.liveText=!this.liveText;
    this.textComposing=false;
    clearTimeout(this.liveTextTimer);
    const b=this.shadowRoot.querySelector('.live-toggle');
    if(b){b.classList.toggle('active',this.liveText);b.setAttribute('aria-pressed',String(this.liveText));}
    const hint=this.shadowRoot.querySelector('.text-hint');
    if(hint)hint.textContent=this.liveText?'Live beta · synced on pause (TV app dependent)':'Enter / Send · full composed text';
    const send=this.shadowRoot.querySelector('.send-label');
    if(send)send.textContent=this.liveText?'Sync':'Send';
  }
  _scheduleLiveText(){
    clearTimeout(this.liveTextTimer);
    if(!this.liveText||this.textComposing)return;
    this.liveTextTimer=setTimeout(()=>{
      if(!this.liveText||this.textComposing)return;
      const field=this.shadowRoot.querySelector('.text-field');
      if(!field)return;
      // Replace the entire focused TV text field, including deletions and Korean composition.
      this._send('text',{text:field.value,replace:true});
    },260);
  }
  _startRepeat(direction,element){this._stopRepeat();this._send('page',{direction});const tick=()=>this._send('page',{direction});this.repeatTimer=setTimeout(()=>{tick();this.repeatTimer=setInterval(tick,320);},500);element?.setPointerCapture?.(this.lastButtonPointerId);}
  _stopRepeat(){if(this.repeatTimer){clearTimeout(this.repeatTimer);clearInterval(this.repeatTimer);this.repeatTimer=null;}}
  _queue(){if(this.frame)return;this.frame=requestAnimationFrame(()=>{this.frame=0;const m=this.pendingMove, s=this.pendingScroll;const mx=Math.trunc(m.x),my=Math.trunc(m.y),sx=Math.trunc(s.x),sy=Math.trunc(s.y);this.pendingMove={x:m.x-mx,y:m.y-my};this.pendingScroll={x:s.x-sx,y:s.y-sy};if(mx||my)this._send('move',{dx:mx,dy:my});if(sx||sy)this._send('scroll',{dx:sx,dy:sy});});}
  _bindTouchpad(){const pad=this.shadowRoot.querySelector('.pad');if(!pad)return;
    pad.addEventListener('pointerdown',e=>{e.preventDefault();pad.setPointerCapture(e.pointerId);this.mousePointers.set(e.pointerId,{x:e.clientX,y:e.clientY,initialX:e.clientX,initialY:e.clientY,t:performance.now()});if(this.mousePointers.size>1)this.twoFinger=true;});
    pad.addEventListener('pointermove',e=>{const p=this.mousePointers.get(e.pointerId);if(!p)return;const dx=e.clientX-p.x,dy=e.clientY-p.y;p.x=e.clientX;p.y=e.clientY;if(this.twoFinger || this.mousePointers.size>1){this.pendingScroll.x+=dx/9;this.pendingScroll.y+=dy/9;}else{this.pendingMove.x+=dx*(Number(this.config?.sensitivity)||1)*this.speedMultiplier;this.pendingMove.y+=dy*(Number(this.config?.sensitivity)||1)*this.speedMultiplier;}this._queue();});
    const end=e=>{const p=this.mousePointers.get(e.pointerId);if(!p)return;this.mousePointers.delete(e.pointerId);if(!this.twoFinger&&Math.hypot(e.clientX-p.initialX,e.clientY-p.initialY)<9&&performance.now()-p.t<350)this._send('click');if(this.mousePointers.size===0)this.twoFinger=false;};
    pad.addEventListener('pointerup',end);pad.addEventListener('pointercancel',end);
    pad.addEventListener('wheel',e=>{e.preventDefault();const scale=e.deltaMode===1?1:e.deltaMode===2?25:0.08;this.pendingScroll.x+=e.deltaX*scale*(Number(this.config?.scrollSensitivity)||1);this.pendingScroll.y+=e.deltaY*scale*(Number(this.config?.scrollSensitivity)||1);this._queue();},{passive:false});
  }
  _render(){if(!this.config)return;const wasField=this.shadowRoot.querySelector('.text-field');const fieldText=wasField?.value??'';
  const buttons=(items)=>items.map(([key,label,icon])=>`<button class="small" title="${esc(label)}" aria-label="${esc(label)}" data-command="${key}">${svg(icon,22)}</button>`).join('');
  this.shadowRoot.innerHTML=`<style>
  :host{display:block;--rd-bg:#111923;--rd-panel:#1b2634;--rd-outline:#33445b;--rd-text:#eef4fe;--rd-muted:#9babc1;--rd-accent:#5687ea;font-family:system-ui,-apple-system,sans-serif;color:var(--rd-text)}
  *{box-sizing:border-box}.shell{padding:16px;border:1px solid var(--rd-outline);border-radius:22px;max-width:410px;margin:auto;background:var(--rd-bg);box-shadow:0 14px 35px #0003}
  .head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:15px}.heading{display:flex;align-items:center;gap:10px}.name{font-weight:700;font-size:15px}.connection{font-size:11px;color:var(--rd-muted);margin-top:4px}.small,.nav,.volume-btn,.app,.scroll-btn,.send{font:inherit;cursor:pointer;border:1px solid var(--rd-outline);border-radius:12px;background:var(--rd-panel);color:var(--rd-text);transition:background .15s,transform .1s;touch-action:manipulation}.small:active,.nav:active,.volume-btn:active,.app:active,.scroll-btn:active,.send:active{transform:scale(.97)}.small:hover,.nav:hover,.volume-btn:hover,.app:hover,.scroll-btn:hover{background:#293b52}
  .small svg,.nav svg,.app svg,.volume-btn svg,.scroll-btn svg,.send svg{display:block;flex:none}.power{width:44px;height:44px;padding:0;display:grid;place-items:center;line-height:0;flex:0 0 44px;color:#ff8c94}.icon-row{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:12px 0 17px}.icon-row .small{height:49px;display:grid;place-items:center}
  .label{font-size:10px;font-weight:750;letter-spacing:1.5px;color:var(--rd-muted);margin:13px 0 9px}.apps{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}.app{height:76px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;font-size:10px;min-width:0;padding:8px 2px}.app.unavailable{opacity:.55}.app-icon{display:grid;place-items:center;width:30px;height:30px;flex:0 0 30px;line-height:1}.app-label{display:block;height:14px;line-height:14px;font-size:10px;white-space:nowrap}.app .netflix{font-size:25px;line-height:1;color:#ed3949;font-weight:900}.app .yt{color:#fa5262}
  .pad-panel{background:var(--rd-panel);border:1px solid var(--rd-outline);border-radius:16px;padding:12px;margin-top:17px}.pad-head{display:flex;gap:8px;align-items:center;justify-content:space-between;font-size:13px;font-weight:650;margin-bottom:9px}.pad-content{display:grid;grid-template-columns:minmax(0,1fr) 67px;gap:8px}.pad{border-radius:12px;min-height:178px;background:linear-gradient(145deg,#26374b,#1b2a3b);display:flex;align-items:center;justify-content:center;flex-direction:column;color:var(--rd-muted);touch-action:none;user-select:none;cursor:crosshair}.pad small{font-size:10px;margin-top:6px}.pages{display:grid;grid-template-rows:1fr 1fr;gap:8px}.scroll-btn{display:flex;align-items:center;justify-content:center;flex-direction:column;gap:4px;font-size:9px;user-select:none;touch-action:none}.scroll-btn span{white-space:nowrap;font-size:9px;letter-spacing:-.3px}
  .speed-group{display:flex;align-items:center;gap:6px;margin-left:auto}.speed-btn{border:1px solid var(--rd-outline);border-radius:9px;background:#172435;color:var(--rd-muted);font:inherit;font-size:11px;font-weight:700;padding:6px 9px;cursor:pointer;min-width:38px}.speed-btn.active{background:var(--rd-accent);border-color:var(--rd-accent);color:white}.speed-btn:focus-visible,.small:focus-visible,.app:focus-visible,.volume-btn:focus-visible,.scroll-btn:focus-visible,.nav:focus-visible{outline:2px solid #a9c7ff;outline-offset:2px}
  .text-heading{display:flex;align-items:center;justify-content:space-between;gap:8px}.live-toggle{border:1px solid var(--rd-outline);border-radius:999px;background:var(--rd-panel);color:var(--rd-muted);font-size:11px;padding:6px 11px;cursor:pointer}.live-toggle.active{background:#214a42;color:#a5f4d7;border-color:#4a9b83}.text-hint{font-size:10px;color:var(--rd-muted);margin:7px 0 0}
  .nav-volume{display:grid;grid-template-columns:minmax(0,1fr) 62px;gap:20px;align-items:center}.dpad{display:grid;grid-template:repeat(3,44px)/repeat(3,52px);gap:5px;justify-content:center}.nav{display:grid;place-items:center}.nav.ok{background:var(--rd-accent);border:0;font-weight:750;font-size:13px}.nav.up{grid-area:1/2}.nav.left{grid-area:2/1}.nav.ok{grid-area:2/2}.nav.right{grid-area:2/3}.nav.down{grid-area:3/2}.volumes{display:grid;grid-template-rows:repeat(3,44px);gap:5px}.volume-btn{display:grid;place-items:center}
  .text-area{margin-top:16px;border-top:1px solid var(--rd-outline);padding-top:13px}.type-line{display:flex;gap:8px}.text-field{min-width:0;flex:1;background:var(--rd-panel);color:var(--rd-text);border:1px solid var(--rd-outline);border-radius:10px;padding:11px;font:inherit;font-size:14px}.send{background:var(--rd-accent);border:0;padding:0 12px;display:flex;gap:5px;align-items:center;font-weight:650}.notice{font-size:11px;padding:10px;background:#263955;border-radius:8px;margin-top:10px}.footer{font-size:10px;color:var(--rd-muted);margin-top:13px;text-align:center}
  @media (max-width:345px){.shell{padding:10px}.nav-volume{gap:4px}.dpad{grid-template-columns:repeat(3,44px)}.pad-content{grid-template-columns:minmax(0,1fr) 58px}}
  </style><div class="shell">
   <div class="head"><div class="heading">${svg('tv',28)}<div><div class="name">${esc(this.config.name)}</div><div class="connection">Connecting…</div></div></div><button title="Power" aria-label="Power" class="small power" data-command="power">${svg('power',22)}</button></div>
   <div class="icon-row">${buttons([['BACK','Back','back'],['HOME','Home','home'],['keyboard','Keyboard','keyboard'],['MENU','Settings','settings']])}</div>
   <div class="label">QUICK APPS</div><div class="apps">
   ${[['netflix','Netflix','<strong class="netflix">N</strong>'],['internet','Internet',svg('globe',24)],['youtube','YouTube',`<span class="yt">${svg('youtube',24)}</span>`],['gallery','Gallery+',svg('gallery',24)]].map(([key,label,icon])=>`<button class="app" data-app="${key}" aria-label="${label}"><span class="app-icon">${icon}</span><span class="app-label">${label}</span></button>`).join('')}</div>
   <div class="pad-panel"><div class="pad-head"><span>Magic Touchpad</span><div class="speed-group" role="group" aria-label="Pointer sensitivity"><button class="speed-btn" data-speed="2" type="button" aria-pressed="${this.speedMultiplier===2}">×2</button><button class="speed-btn" data-speed="4" type="button" aria-pressed="${this.speedMultiplier===4}">×4</button></div></div><div class="pad-content"><div class="pad" role="application" aria-label="TV pointer touchpad">${svg('pointer',24)}<small>Move · Click · Scroll</small></div><div class="pages"><button class="scroll-btn" data-page="up" title="Page Up">${svg('pageUp')}<span>PAGE UP</span></button><button class="scroll-btn" data-page="down" title="Page Down">${svg('pageDown')}<span>PAGE DOWN</span></button></div></div></div>
   <div class="label">NAVIGATION & VOLUME</div><div class="nav-volume"><div class="dpad">
   ${[['UP','up','up'],['LEFT','left','left'],['ENTER','ok',''],['RIGHT','right','right'],['DOWN','down','down']].map(([key,cls,ic])=>`<button class="nav ${cls}" data-command="${key}" aria-label="${key}">${ic?svg(ic,21):'OK'}</button>`).join('')}
   </div><div class="volumes"><button class="volume-btn" data-volume="up" aria-label="Volume Up">${svg('plus')}</button><button class="volume-btn" data-volume="mute" aria-label="Mute">${svg('mute')}</button><button class="volume-btn" data-volume="down" aria-label="Volume Down">${svg('minus')}</button></div></div>
   <div class="text-area" ${this.keyboardOpen?'':'hidden'}><div class="text-heading"><div class="label">TEXT INPUT</div><button type="button" class="live-toggle ${this.liveText?'active':''}" aria-pressed="${this.liveText}" title="Experimental live IME text sync">Live (beta)</button></div><div class="type-line"><input class="text-field" type="text" placeholder="Type in Korean or English" autocomplete="off" autocorrect="off" spellcheck="false"><button class="send" title="Send text">${svg('send',16)} <span class="send-label">${this.liveText?'Sync':'Send'}</span></button></div><div class="text-hint">${this.liveText?'Live beta · synced on pause (TV app dependent)':'Enter / Send · full composed text'}</div></div>
   <div class="notice" hidden role="status"></div><div class="footer">LG webOS Remote for Home Assistant · ${this.authenticated?'Connected':'Secure local remote'}</div>
  </div>`;
  const field=this.shadowRoot.querySelector('.text-field');if(field)field.value=fieldText;
  this.shadowRoot.querySelectorAll('[data-command]').forEach(b=>b.addEventListener('click',()=>this._tap(b.dataset.command)));
  this.shadowRoot.querySelectorAll('[data-app]').forEach(b=>b.addEventListener('click',()=>this._app(b.dataset.app)));
  this.shadowRoot.querySelectorAll('[data-volume]').forEach(b=>b.addEventListener('click',()=>this._send('volume',{action:b.dataset.volume})));
  this.shadowRoot.querySelector('.send')?.addEventListener('click',()=>this._sendText());
  this.shadowRoot.querySelector('.live-toggle')?.addEventListener('click',()=>this._setLiveText());
  this.shadowRoot.querySelectorAll('[data-speed]').forEach(b=>{b.classList.toggle('active',Number(b.dataset.speed)===this.speedMultiplier);b.addEventListener('click',()=>this._setSpeed(Number(b.dataset.speed)));});
  field?.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.isComposing&&e.keyCode!==229){e.preventDefault();this._sendText();}});
  field?.addEventListener('compositionstart',()=>{this.textComposing=true;clearTimeout(this.liveTextTimer);});
  field?.addEventListener('compositionend',()=>{this.textComposing=false;this._scheduleLiveText();});
  field?.addEventListener('input',()=>this._scheduleLiveText());
  this.shadowRoot.querySelectorAll('[data-page]').forEach(b=>{b.addEventListener('pointerdown',e=>{e.preventDefault();this.lastButtonPointerId=e.pointerId;this._startRepeat(b.dataset.page,b);});['pointerup','pointercancel','lostpointercapture'].forEach(k=>b.addEventListener(k,()=>this._stopRepeat()));});
  this._bindTouchpad();this._renderAppStates();this._renderState();this._setState(this.authenticated?(this.tvOnline?'TV On':'TV Off · Wake ready'):'Connecting…');
  }
  getCardSize(){return 9;}
}
if(!customElements.get('lg-webos-remote'))customElements.define('lg-webos-remote', LGWebOSRemoteCard);
window.customCards=window.customCards||[];
if(!window.customCards.some(c=>c.type==='lg-webos-remote'))window.customCards.push({type:'lg-webos-remote',name:'LG webOS Remote for Home Assistant',description:'MIT-licensed LG webOS remote with touchpad, apps, typing and Wake-on-LAN'});
