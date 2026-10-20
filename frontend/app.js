'use strict';

const $ = (id) => document.getElementById(id);
const dom = Object.fromEntries([
  'scene', 'merchantSprite', 'merchantButton', 'merchantSpeech', 'dialogue', 'closeDialogue',
  'chatForm', 'chatInput', 'sendButton', 'messages', 'chatModeLabel',
  'storePanel', 'bagPanel', 'shade', 'bagButton', 'showStore', 'quickStore', 'quickBag', 'quickAsk',
  'hudGold', 'bagGold', 'categories', 'itemSearch', 'catalogueList', 'inventoryList', 'itemCount',
  'purchaseCount', 'connectionDot', 'connectionLabel', 'purchaseModal', 'purchaseItemName',
  'purchaseForm', 'purchaseQuantity', 'purchaseDestination', 'unitPrice', 'subTotal',
  'deliveryPrice', 'totalPrice', 'purchaseError', 'confirmPurchase', 'closePurchase',
  'cancelPurchase', 'resetButton', 'motionButton', 'toast',
].map(id => [id, $(id)]));

const CATEGORIES = {
  todas:'Todas', armas:'Armas', municoes:'Munições', armaduras:'Armaduras',
  pocoes:'Poções', magia:'Magia', utilidades:'Utilidades',
};
const GLYPHS = {armas:'⚔', municoes:'➶', armaduras:'♜', pocoes:'⚗', magia:'✧', utilidades:'◈'};
let shop = {itens:[], destinos:[]};
let player = {ouro_centavos:100000, inventario:[], compras_realizadas:0};
let category = 'todas', selectedItem = null, quote = null, quoteRequest = 0;
let history = [], busy = false, previousFocus = null, toastTimeout;
let reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const money = cents => new Intl.NumberFormat('pt-BR', {minimumFractionDigits: cents % 100 ? 2 : 0, maximumFractionDigits:2}).format(cents / 100);

async function api(path, options={}) {
  let response;
  try { response = await fetch('/api/' + path, {headers:{'Content-Type':'application/json'}, ...options}); }
  catch { throw new Error('Sem conexão com o servidor. Veja o terminal da aplicação.'); }
  let data;
  try { data = await response.json(); } catch { throw new Error('Resposta inesperada do servidor.'); }
  if (!response.ok) {
    let error = data.detail;
    if (Array.isArray(error)) error = error.map(e => e.msg).join('; ');
    throw new Error(typeof error === 'string' ? error : 'Não foi possível completar a operação.');
  }
  return data;
}
const post = (path, obj) => api(path, {method:'POST', body:JSON.stringify(obj)});

function el(tag, cls, text) {
  const x = document.createElement(tag);
  if (cls) x.className = cls;
  if (text !== undefined) x.textContent = text;
  return x;
}
function notify(message) {
  clearTimeout(toastTimeout);
  dom.toast.textContent = message;
  dom.toast.hidden = false;
  toastTimeout = setTimeout(() => dom.toast.hidden = true, 4400);
}

function renderPlayer() {
  dom.hudGold.textContent = money(player.ouro_centavos);
  dom.bagGold.textContent = money(player.ouro_centavos);
  dom.itemCount.textContent = player.inventario.reduce((total,i) => total+i.quantidade, 0) + ' ITENS';
  dom.purchaseCount.textContent = `${player.compras_realizadas} COMPRAS REGISTRADAS`;
  dom.inventoryList.replaceChildren();
  if (!player.inventario.length) {
    dom.inventoryList.append(el('p','empty-state','Tua bolsa ainda está vazia, aventureiro.\nO próximo tesouro aguarda além das sombras.'));
    return;
  }
  for (const item of player.inventario) {
    const row = el('div','inventory-item');
    row.append(el('span','',item.nome), el('span','quantity',`× ${item.quantidade}`));
    dom.inventoryList.append(row);
  }
}

function renderCategories() {
  dom.categories.replaceChildren();
  for (const [id,title] of Object.entries(CATEGORIES)) {
    const button = el('button','category-btn' + (id === category ? ' selected' : ''),title);
    button.type = 'button';
    button.setAttribute('aria-pressed', id === category ? 'true' : 'false');
    button.addEventListener('click', () => {category=id;renderCategories();renderShop();});
    dom.categories.append(button);
  }
}
function renderShop() {
  const search = normalize(dom.itemSearch.value);
  const items = shop.itens.filter(item => (category==='todas' || item.categoria===category) && normalize(item.nome).includes(search));
  dom.catalogueList.replaceChildren();
  if (!items.length) { dom.catalogueList.append(el('p','empty-state','Nenhuma mercadoria encontrada nestas sombras.')); return; }
  for (const item of items) {
    const card = el('article','catalogue-item');
    const main = el('div','catalogue-item-main');
    main.append(el('div','item-glyph',GLYPHS[item.categoria] || '◈'));
    const text = el('div','item-text');
    text.append(el('div','item-name',item.nome), el('div','catalogue-sub',CATEGORIES[item.categoria].toUpperCase()));
    main.append(text);
    const actions = el('div','item-actions');
    actions.append(el('span','item-price',`✦ ${money(item.preco_centavos)}`));
    const buy = el('button','item-buy','NEGOCIAR');
    buy.type='button';buy.addEventListener('click',() => openPurchase(item));
    actions.append(buy);card.append(main,actions);dom.catalogueList.append(card);
  }
}
function normalize(x) {return (x || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}

function closePanels() {
  dom.storePanel.hidden=true;dom.bagPanel.hidden=true;dom.shade.hidden=true;
  if (previousFocus?.isConnected) previousFocus.focus();
}
function openPanel(panel) {
  previousFocus = document.activeElement;
  dom.storePanel.hidden = panel !== 'store';
  dom.bagPanel.hidden = panel !== 'bag';
  dom.shade.hidden = false;
  if (panel === 'store') {renderShop();dom.itemSearch.focus();}
  if (panel === 'bag') {renderPlayer();dom.bagPanel.querySelector('.icon-button').focus();}
}
function openDialogue() {
  dom.dialogue.hidden = false;
  dom.merchantSpeech.hidden = true;
  dom.chatInput.focus();
}
function closeDialogue() {
  dom.dialogue.hidden = true;
  dom.merchantSpeech.hidden = false;
  dom.merchantButton.focus();
}

function cleanReply(text) {
  let t = String(text ?? '').trim();
  try {const obj=JSON.parse(t);if (obj && typeof obj==='object') t=obj.fala || obj.resposta || obj.content || t;} catch {}
  return t.replace(/^```[^\n]*\n?/gm,'').replace(/```$/gm,'')
          .replace(/^\s{0,3}#{1,4}\s+/gm,'').replace(/\*\*(.*?)\*\*/g,'$1')
          .replace(/`([^`]+)`/g,'$1').replace(/^(mercador sombrio|vendedor sombrio):\s*/i,'').slice(0,3300);
}
function addMessage(who, content, meta) {
  const message = el('div', 'message ' + (who==='user' ? 'player-message' : 'merchant-message'));
  message.append(el('div','message-name',who==='user'?'AVENTUREIRO':'MERCADOR SOMBRIO'));
  message.append(el('p','',cleanReply(content)));
  if (meta) message.append(el('div','message-meta',meta));
  dom.messages.append(message);
  dom.messages.scrollTop = dom.messages.scrollHeight;
}
async function sendMessage(text) {
  text = text.trim();if (!text || busy) return;
  openDialogue();
  addMessage('user',text);
  dom.chatInput.value='';busy=true;dom.sendButton.disabled=true;
  const oldHistory = history.slice(-10);
  addMessage('assistant','O mercador consulta seus pergaminhos...');
  const pending = dom.messages.lastElementChild;
  try {
    const result = await post('chat',{mensagem:text,historico:oldHistory});
    pending.remove();
    addMessage('assistant',result.fala, result.modo==='ollama' ? `IA ATIVA · ${result.ferramentas.length} CHAMADAS MCP` : 'DIÁLOGO BÁSICO · SEM IA');
    if (result.aviso) notify(result.aviso);
    history.push({role:'user',content:text},{role:'assistant',content:result.fala});
    history=history.slice(-10);
    dom.chatModeLabel.textContent=result.modo==='ollama'?'AGENTE OLLAMA + MCP':'MODO DEMONSTRAÇÃO';
    if (result.aviso) {dom.connectionDot.classList.add('demo');dom.connectionLabel.textContent='IA INDISPONÍVEL';}
  } catch (error) {
    pending.remove();addMessage('assistant','As sombras interromperam nossa conversa. '+error.message);
  } finally {busy=false;dom.sendButton.disabled=false;dom.chatInput.focus();}
}

function updatePurchaseDestination() {
  dom.purchaseDestination.replaceChildren();
  for (const dst of shop.destinos) {
    const opt=document.createElement('option');opt.value=dst.id;opt.textContent=`${dst.nome} · ✦ ${money(dst.taxa_centavos)}`;
    dom.purchaseDestination.append(opt);
  }
  dom.purchaseDestination.value='vila';
}
function openPurchase(item) {
  selectedItem=item;quote=null;
  dom.purchaseItemName.textContent=item.nome;
  dom.purchaseQuantity.value='1';
  updatePurchaseDestination();
  dom.purchaseModal.hidden=false;
  dom.purchaseError.hidden=true;
  recalculate();
  dom.purchaseQuantity.focus();
}
function closePurchase() {dom.purchaseModal.hidden=true;selectedItem=null;quote=null;quoteRequest++;}
async function recalculate() {
  if (!selectedItem) return;
  const req=++quoteRequest;
  quote=null;dom.confirmPurchase.disabled=true;dom.purchaseError.hidden=true;
  for (const id of ['unitPrice','subTotal','deliveryPrice','totalPrice']) dom[id].textContent='—';
  try {
    const result=await post('orcamentos',{
      item:selectedItem.id, quantidade:Number(dom.purchaseQuantity.value), local:dom.purchaseDestination.value,
    });
    if (req!==quoteRequest) return;
    quote=result;
    dom.unitPrice.textContent='✦ '+money(result.preco_unitario_centavos);
    dom.subTotal.textContent='✦ '+money(result.subtotal_centavos);
    dom.deliveryPrice.textContent='✦ '+money(result.taxa_centavos);
    dom.totalPrice.textContent='✦ '+money(result.total_centavos);
    dom.confirmPurchase.disabled=result.total_centavos>player.ouro_centavos;
    if (result.total_centavos>player.ouro_centavos) {
      dom.purchaseError.textContent='Ouro insuficiente. A bolsa não comporta essa dívida.';
      dom.purchaseError.hidden=false;
    }
  } catch(error) {
    if (req!==quoteRequest) return;
    dom.purchaseError.textContent=error.message;dom.purchaseError.hidden=false;
  }
}
async function confirmPurchase(event) {
  event.preventDefault();if (!selectedItem || !quote) return;
  dom.confirmPurchase.disabled=true;
  try {
    const result=await post('compras',{
      item:quote.item, quantidade:quote.quantidade, local:quote.local,
    });
    player=result.estado;renderPlayer();
    const itemName=selectedItem.nome;
    closePurchase();openPanel('bag');
    notify(`✦ Negócio fechado! ${result.orcamento.quantidade} × ${itemName} agora faz parte da tua bolsa.`);
    addMessage('assistant',`Está feito, aventureiro. ${result.orcamento.quantidade} × ${itemName} agora te pertence. Eu mesmo farei a entrega até ${result.orcamento.local}...`,'COMPRA CONFIRMADA PELO SISTEMA');
  } catch(error) {dom.purchaseError.textContent=error.message;dom.purchaseError.hidden=false;}
  finally {if (selectedItem) dom.confirmPurchase.disabled=false;}
}

// ========= Cena pixel art: desenhada em Canvas, sem dependência de imagens externas =========
const canvas=dom.scene,ctx=canvas.getContext('2d',{alpha:false});
const W=480,H=270;
const pix=(x,y,w,h,c)=>{ctx.fillStyle=c;ctx.fillRect(Math.floor(x),Math.floor(y),Math.ceil(w),Math.ceil(h));};
let seed=721;
const rnd=()=>{seed=(seed*16807)%2147483647;return (seed-1)/2147483646;};
let stars=[], rain=[], towers=[];
for(let i=0;i<100;i++) stars.push({x:Math.floor(rnd()*W),y:Math.floor(rnd()*115),l:rnd()});
for(let i=0;i<115;i++) rain.push({x:rnd()*W,y:rnd()*H,s:1.2+rnd()*3.2,l:2+rnd()*6});
for(let i=0;i<65;i++) towers.push({x:i*9-12,w:4+Math.floor(rnd()*7),h:6+rnd()*24});
const lightFromStorm = (time)=> !reduceMotion && ((time%17000>14850 && time%17000<15000) || (time%17000>15130 && time%17000<15190));
function drawCastle(time) {
  // Layered blue-black skyline
  pix(0,0,W,H,'#0b1128');
  for(let y=0;y<205;y+=2) pix(0,y,W,2,`rgb(${13+Math.floor(y/34)},${15+Math.floor(y/20)},${37+Math.floor(y/19)})`);
  // Moon halo and moon
  ctx.fillStyle='#b2a6c01c';ctx.beginPath();ctx.arc(295,59,51,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#d5d0d0';ctx.beginPath();ctx.arc(295,59,19,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#9d9bab';ctx.beginPath();ctx.arc(301,52,17,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#b8b1be';ctx.beginPath();ctx.arc(296,58,3,0,Math.PI*2);ctx.fill();
  stars.forEach(st=>{pix(st.x,st.y,st.l>.86?2:1,1,st.l>.65?'#9d95b6':'#57506f');});
  // Clouds, low contrast dithery blocks
  for(let i=0;i<16;i++){
    let cloudX=((i*89 + Math.floor((time/220)*((i%3)+1)))%(W+150))-75;
    let cy=21+(i*31)%116;
    pix(cloudX,cy,53+(i%4)*20,7,'#222342');
    pix(cloudX+11,cy-5,36,5,'#222342');
    pix(cloudX-6,cy+6,69,3,'#1a1c38');
  }
  // Distant peaks
  ctx.fillStyle='#12172c';ctx.beginPath();ctx.moveTo(0,187);
  for(let x=0;x<=W;x+=12) ctx.lineTo(x,142+Math.sin(x*.025)*17+Math.cos(x*.087)*9);
  ctx.lineTo(W,H);ctx.lineTo(0,H);ctx.fill();
  // Moat/cemetery mid-ground
  for(let i=0;i<towers.length;i++){
    let b=towers[i];pix(b.x,174-b.h,b.w,36+b.h,i%3===0?'#111329':'#14162b');
  }
  pix(0,188,W,82,'#111525');
  for(let x=0;x<W;x+=18){pix(x,191,8,1,'#252a3f');pix(x+5,210,5,1,'#222638')}
  // Castle walls silhouette, centered right-of-center
  pix(210,104,185,110,'#0d1021');pix(207,117,192,94,'#121325');
  for(let x=212;x<392;x+=13) pix(x,99,9,21,'#0b0e1f');
  // main gate and side parapets
  pix(235,89,36,123,'#101223');pix(331,83,34,129,'#101223');
  pix(240,80,27,9,'#0a0d1c');pix(335,73,26,11,'#0a0d1c');
  for(let x=236;x<271;x+=9)pix(x,77,6,11,'#090d1b');
  for(let x=332;x<370;x+=10)pix(x,70,7,12,'#090d1b');
  // main tower
  pix(283,55,42,155,'#0c1021');pix(277,57,54,12,'#0b0d1e');
  for(let x=282;x<327;x+=10)pix(x,47,7,16,'#0a0d1b');
  pix(296,29,16,23,'#0b0d1b');pix(302,18,4,24,'#0d1020');
  // windows illuminated
  for(let y=95;y<168;y+=25){
    for(let x=225;x<383;x+=33){
      if ((x+y)%4 !==0){pix(x,y,4,10,'#65563d');pix(x+1,y+1,2,7,'#d1a95f');pix(x,y+8,4,2,'#282433');}
    }
  }
  pix(300,83,7,15,'#90724d');pix(302,85,3,10,'#efc68a');
  // gateway with arch
  pix(298,175,17,35,'#030712');pix(300,169,13,16,'#030712');pix(301,165,11,18,'#050913');
  // Castle ridge and distant torch windows
  pix(0,212,W,58,'#10121e');
  for(let x=0;x<W;x+=23){pix(x,214,10,2,'#17192a');pix(x+4,233,6,1,'#1b1b29');}
  // Cobbled path into castle
  ctx.fillStyle='#282633';ctx.beginPath();ctx.moveTo(291,214);ctx.lineTo(317,214);ctx.lineTo(397,270);ctx.lineTo(220,270);ctx.fill();
  for(let y=222;y<H;y+=9){for(let x=227;x<390;x+=23){pix(x+(y%3)*3,y,14,2,'#393343');}}
  // foreground plants/ruins
  for(let x=0;x<W;x+=14){let hh=2+(x*7)%9;pix(x,243-hh,2,hh,'#1e2b28');pix(x-3,240-hh/2,5,2,'#26312a');}
  pix(12,210,17,44,'#171729');pix(9,204,23,7,'#242336');pix(17,201,7,4,'#2c283b');
  pix(425,216,25,35,'#141626');pix(421,210,33,6,'#252438');
  if(lightFromStorm(time)){
    pix(0,0,W,H,'#d8d7fa28');
    ctx.strokeStyle='#c9ceff';ctx.lineWidth=2;
    ctx.beginPath();ctx.moveTo(412,0);ctx.lineTo(398,24);ctx.lineTo(411,30);ctx.lineTo(391,55);ctx.lineTo(405,63);ctx.lineTo(382,96);ctx.stroke();
    ctx.strokeStyle='#ffffff';ctx.lineWidth=1;ctx.stroke();
  }
}
function drawRain(time){
  if(reduceMotion) return;
  ctx.strokeStyle='#96a3cb6d';ctx.lineWidth=.55;ctx.beginPath();
  for(const r of rain){const x=(r.x+(time*.026*r.s))%W;const y=(r.y+(time*.048*r.s))%H;ctx.moveTo(x,y);ctx.lineTo(x-1.5,y+r.l);}
  ctx.stroke();
}
const sprite=dom.merchantSprite.getContext('2d');
function sp(x,y,w,h,color) {sprite.fillStyle=color;sprite.fillRect(x,y,w,h);}
function drawMerchant(time){
  sprite.clearRect(0,0,112,128);sprite.imageSmoothingEnabled=false;
  const bob=reduceMotion?0:Math.round(Math.sin(time/480)*1.6);
  sprite.save();sprite.translate(0,bob);
  // shadow, lantern glow
  sprite.fillStyle='#b7a1fc20';sprite.beginPath();sprite.ellipse(59,77,33,41,0,0,Math.PI*2);sprite.fill();
  // cape geometry
  sp(25,57,64,60,'#151025');sp(20,79,74,35,'#140f26');
  sp(18,109,79,9,'#211833');sp(28,117,65,5,'#0e0c1b');
  sp(30,74,49,33,'#291c40');sp(37,71,33,38,'#332349');
  sp(20,83,13,29,'#251735');sp(79,82,13,28,'#241737');
  sp(33,109,9,11,'#36283c');sp(68,109,10,11,'#36283c');
  // shoulder pads
  sp(23,53,26,16,'#3b2a50');sp(67,53,24,16,'#3a294b');
  sp(20,64,14,12,'#281b36');sp(79,64,16,12,'#281b36');
  // mask and hood
  sp(38,17,38,51,'#170f2a');sp(33,25,47,39,'#261832');
  sp(42,17,27,9,'#221833');sp(30,31,54,15,'#301f43');
  sp(31,39,52,22,'#241536');sp(37,43,37,22,'#070918');
  sp(39,29,7,26,'#403051');sp(69,29,8,27,'#392747');
  sp(44,49,11,4,'#d2b8ff');sp(60,49,12,4,'#c4a9f9');
  sp(47,49,5,4,'#f8e9ff');sp(63,49,6,4,'#f8e9ff');
  sp(38,67,39,6,'#69516c');sp(42,69,29,5,'#9b7e72');
  // cloth highlights and brooch
  sp(40,78,5,21,'#4a3559');sp(70,78,4,20,'#4a3154');
  sp(54,73,8,8,'#aa824f');sp(56,74,4,6,'#e1be7e');
  // arm sleeve hand
  sp(24,72,12,23,'#38254d');sp(21,91,16,10,'#38254b');sp(27,99,7,7,'#83717e');
  sp(76,73,13,24,'#3a284d');sp(78,96,14,9,'#766675');
  // satchel
  sp(73,88,17,24,'#6b4f37');sp(77,91,16,16,'#9a7350');sp(74,94,16,3,'#c3a16a');sp(81,98,5,7,'#503b32');
  // merchant staff (left)
  sp(13,20,4,99,'#49352f');sp(14,14,2,9,'#75523c');sp(8,9,15,9,'#423355');sp(10,7,11,7,'#7659ac');sp(12,5,7,6,'#b38dec');sp(15,9,3,3,'#f7d8ff');
  // shimmer particles
  if(!reduceMotion){let tw=Math.floor(time/420)%9;sp(6+tw,29,2,2,'#8a76bb');sp(18,2+tw,1,2,'#c5a2ec');}
  sprite.restore();
}
let lastFrame=0;
function tick(time) {
  if(time-lastFrame>44 || reduceMotion) {lastFrame=time;drawCastle(reduceMotion?0:time);drawRain(time);drawMerchant(time);}
  if(!reduceMotion) requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

async function boot() {
  renderCategories();
  try {
    const [data,state,health]=await Promise.all([api('loja'),api('estado'),api('saude')]);
    shop=data;player=state;renderPlayer();renderShop();
    const demo=health.modo_ia!=='ollama';
    dom.connectionDot.classList.toggle('demo',demo);
    dom.connectionLabel.textContent=demo?'MODO DEMO':'OLLAMA CONECTÁVEL';
    dom.chatModeLabel.textContent=demo?'MODO DEMONSTRAÇÃO':'AGENTE OLLAMA + MCP';
  } catch(error) {
    dom.connectionDot.classList.add('demo');dom.connectionLabel.textContent='DESCONECTADO';
    notify(error.message);
  }
}

// ========= Eventos =========
dom.merchantButton.addEventListener('click',openDialogue);
dom.closeDialogue.addEventListener('click',closeDialogue);
dom.bagButton.addEventListener('click',()=>openPanel('bag'));
dom.showStore.addEventListener('click',()=>openPanel('store'));
dom.quickStore.addEventListener('click',()=>openPanel('store'));
dom.quickBag.addEventListener('click',()=>openPanel('bag'));
dom.quickAsk.addEventListener('click',()=>sendMessage('Quanto custa a poção de vida?'));
dom.itemSearch.addEventListener('input',renderShop);
dom.shade.addEventListener('click',closePanels);
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',closePanels));
dom.closePurchase.addEventListener('click',closePurchase);
dom.cancelPurchase.addEventListener('click',closePurchase);
dom.purchaseQuantity.addEventListener('input',recalculate);
dom.purchaseDestination.addEventListener('change',recalculate);
dom.purchaseForm.addEventListener('submit',confirmPurchase);
dom.chatForm.addEventListener('submit',(e)=>{e.preventDefault();sendMessage(dom.chatInput.value);});
dom.resetButton.addEventListener('click',async()=>{
  if(!window.confirm('Reiniciar esta demonstração? Seu ouro, itens e compras serão apagados.')) return;
  try {player=await post('reiniciar',{});renderPlayer();notify('Um novo começo... tua bolsa foi restaurada.');}
  catch(error){notify(error.message);}
});
dom.motionButton.addEventListener('click',()=>{
  reduceMotion=!reduceMotion;
  dom.motionButton.textContent=reduceMotion?'✧ SEM EFEITOS':'✧ EFEITOS';
  if(!reduceMotion) requestAnimationFrame(tick);else {drawCastle(0);drawMerchant(0);}
});
document.addEventListener('keydown',(event)=>{
  if(event.key==='Escape'){
    if(!dom.purchaseModal.hidden)closePurchase();
    else if(!dom.shade.hidden)closePanels();
    else if(!dom.dialogue.hidden)closeDialogue();
  }
});
boot();
