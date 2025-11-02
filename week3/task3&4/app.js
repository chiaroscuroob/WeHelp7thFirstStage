// app.js（Task 4：序號對齊 + 分頁載入更多）
// - 來源：assignment-3-1（名稱）＋ assignment-3-2（圖片）
// - 共同序號（serial/id/...）join，保證名稱與圖片對得上
// - 初始化：promos 取前 3；gallery 以 10 筆一頁分頁；按鈕「載入更多」追加下一頁
// - 只用 createElement/appendChild，不使用 innerHTML

(() => {
  const SRC_NAME  = "https://cwpeng.github.io/test/assignment-3-1";
  const SRC_IMAGE = "https://cwpeng.github.io/test/assignment-3-2";

  // 圖片/路徑偵測
  const ABS_IMG_RE  = /https?:\/\/[^"'()\s]+?\.(?:jpg|jpeg|png)/i;
  const REL_IMG_RE  = /(?:^|["'\s])((?:\/\/|\/)[^"'()\s]+?\.(?:jpg|jpeg|png))/i;
  const HOST_IMG_RE = /(?:^|["'\s])((?:[a-z0-9.-]+\.[a-z]{2,}\/)[^"'()\s]+?\.(?:jpg|jpeg|png))/i;

  // DOM helpers
  const $ = (s) => document.querySelector(s);
  const promosRoot  = () => $("#promos")  || document.querySelector(".promos");
  const galleryRoot = () => $("#gallery") || document.querySelector(".gallery");
  const loadMoreBtn = () => $("#loadMore");
  const clear = (el) => { while (el && el.firstChild) el.removeChild(el.firstChild); };
  const isObj = (x) => x && typeof x === "object" && !Array.isArray(x);

  // 欄位白名單
  const NAME_KEYS   = ["sname","stitle","name","title","標題","景點名稱","SName","Name","TITLE"];
  const SERIAL_KEYS = ["serial","serial_no","serialno","serialnumber","serial_number","id","uid","_id","rowid","row_id","rownum","no","NO","SERIAL","SERIAL_NO"];
  const toHalfWidth = (str) => String(str || "").replace(/[\uFF01-\uFF5E]/g, ch => String.fromCharCode(ch.charCodeAt(0)-0xFEE0)).replace(/\u3000/g, " ");
  const normSerial  = (v) => toHalfWidth(String(v || "")).trim().toUpperCase();

  // 分頁狀態
  let ALL_ITEMS = [];     // { name, img }[]
  let CURSOR = 3;         // 前 3 筆已經給 promos，gallery 從 index 3 開始
  const PAGE_SIZE = 10;   // 每頁 10 筆

  window.addEventListener("DOMContentLoaded", init);

  async function init() {
    try {
      const [j1, j2] = await Promise.all([fetchLoose(SRC_NAME), fetchLoose(SRC_IMAGE)]);
      const baseHost = toAbsoluteHost(j2?.host);

      // ===== 3-1：名稱 + 序號（保順序）=====
      const { names, serials: s1, nameKey: nk1, serialKey: sk1 } = extractNamesAndSerials(j1);
      console.log("[week3] 3-1 nameKey:", nk1, "serialKey:", sk1, "names:", names.length);

      // ===== 3-2：圖片 + 序號（做 map）=====
      const { images, serials: s2, serialKey: sk2, imageKey: ik2 } = extractImagesAndSerials(j2, baseHost);
      console.log("[week3] 3-2 imageKey:", ik2, "serialKey:", sk2, "images:", images.length);

      const imgBySerial = new Map();
      for (let i = 0; i < s2.length; i++){
        const key = normSerial(s2[i]);
        const img = images[i] || null;
        if (key && img && !imgBySerial.has(key)) imgBySerial.set(key, img);
      }

      // 合併（優先用序號對齊；沒有序號就 zip）
      const items = [];
      let bySerial = 0, byZip = 0;
      const N = Math.min(names.length, images.length);
      for (let i=0;i<names.length;i++){
        const name = toStringTrim(names[i]);
        const sKey = normSerial(s1[i]);
        let img = null;
        if (sKey && imgBySerial.has(sKey)) { img = imgBySerial.get(sKey); bySerial++; }
        else if (i < N) { img = images[i] || null; byZip++; }
        items.push({ name, img });
      }
      console.log(`[week3] join bySerial: ${bySerial}, zipFallback: ${byZip}, final: ${items.length}`);

      // ===== 渲染（promos 3 + gallery 分頁 10）=====
      const pRoot = promosRoot();
      const gRoot = galleryRoot();
      if (!pRoot || !gRoot) {
        console.warn("找不到 .promos/.gallery 容器。");
        return;
      }
      clear(pRoot); clear(gRoot);

      ALL_ITEMS = items;
      CURSOR = 3; // 前 3 張給 promos
      renderPromos(pRoot, ALL_ITEMS.slice(0, 3));
      renderNextPage(); // 先渲染第一頁（10 筆）

      // 綁定 Load More
      const btn = loadMoreBtn();
      if (btn) {
        btn.onclick = () => renderNextPage();
        updateButtonState();
      }
    } catch (e) {
      console.error(e);
      const g = galleryRoot();
      if (g) showFallback(g, "載入資料失敗。");
    }
  }

  // ——————— 分頁：每次追加 10 筆到 .gallery ———————
  function renderNextPage(){
    const gRoot = galleryRoot();
    if (!gRoot) return;

    const end = Math.min(CURSOR + PAGE_SIZE, ALL_ITEMS.length);
    const slice = ALL_ITEMS.slice(CURSOR, end);
    appendGallery(gRoot, slice);
    CURSOR = end;
    updateButtonState();
  }

  function updateButtonState(){
    const btn = loadMoreBtn();
    if (!btn) return;
    if (CURSOR >= ALL_ITEMS.length) {
      btn.textContent = "All Loaded";   // 原：已全部載入
      btn.disabled = true;
    } else {
      btn.textContent = "Load More";    // 原：載入更多
      btn.disabled = false;
    }
  }

  // ——————— fetch（寬鬆 JSON 解析）———————
  async function fetchLoose(url) {
    const res = await fetch(url, { cache: "no-cache" });
    const txt = await res.text();
    try {
      const j = JSON.parse(txt);
      console.log("[week3]", url, "parsed ✓", Object.keys(j));
      return j;
    } catch {
      const m = txt.match(/\{[\s\S]*\}|\[[\s\S]*\]/);
      if (m) {
        const j = JSON.parse(m[0]);
        console.log("[week3]", url, "wrapped JSON parsed ✓");
        return j;
      }
      throw new Error(`JSON parse failed @ ${url}`);
    }
  }

  // ——————— 3-1：名稱 + 序號 ———————
  function extractNamesAndSerials(json) {
    const outNames = [], outSerials = [];
    let nameKey = null, serialKey = null;
    if (!Array.isArray(json?.rows)) return { names: outNames, serials: outSerials, nameKey, serialKey };
    const rows = json.rows;

    if (rows.length && isObj(rows[0])) {
      const keys = collectKeys(rows);
      nameKey   = pickFirstExist(keys, NAME_KEYS)   || pickBestShortTextKey(rows);
      serialKey = pickFirstExist(keys, SERIAL_KEYS) || pickBestSerialKey(rows);
      for (const r of rows){ outNames.push(toStringTrim(r?.[nameKey])); outSerials.push(r?.[serialKey] ?? ""); }
      return { names: outNames, serials: outSerials, nameKey, serialKey };
    }
    const header = toLower(json.name);
    const nameIdx   = pickIndexByHeader(header, NAME_KEYS)   ?? 0;
    const serialIdx = pickIndexByHeader(header, SERIAL_KEYS) ?? null;
    for (const row of rows){ outNames.push(getCellString(row, nameIdx)); outSerials.push(serialIdx!=null?getCellString(row, serialIdx):""); }
    nameKey   = String(header?.[nameIdx] || nameIdx);
    serialKey = serialIdx!=null ? String(header?.[serialIdx] || serialIdx) : null;
    return { names: outNames, serials: outSerials, nameKey, serialKey };
  }

  // ——————— 3-2：圖片 + 序號 ———————
  function extractImagesAndSerials(json, baseHost) {
    const outImgs = [], outSerials = [];
    let serialKey = null, imageKey = null;
    if (!Array.isArray(json?.rows)) return { images: outImgs, serials: outSerials, serialKey, imageKey };
    const rows = json.rows;

    if (rows.length && isObj(rows[0])) {
      const keys = collectKeys(rows);
      serialKey = pickFirstExist(keys, SERIAL_KEYS) || pickBestSerialKey(rows);
      imageKey  = pickFirstExist(keys, ["file","pics","images","image","img","picture","photos","Picture1","Picture","FILE","File"]) || pickBestImageKey(rows, baseHost);
      for (const r of rows){
        const img = firstImageFromObject(r, imageKey, baseHost);
        outImgs.push(img);
        outSerials.push(r?.[serialKey] ?? "");
      }
      return { images: outImgs, serials: outSerials, serialKey, imageKey };
    }
    const header = toLower(json.name);
    const imgIdx    = pickIndexByHeader(header, ["file","pics","images","image","img","picture","photos","picture1"]) ?? 0;
    const serialIdx = pickIndexByHeader(header, SERIAL_KEYS) ?? null;
    for (const row of rows){
      const raw = getCellString(row, imgIdx);
      const img = findImageInString(raw, baseHost) || findImageInArray(row, baseHost) || null;
      outImgs.push(img);
      outSerials.push(serialIdx!=null?getCellString(row, serialIdx):"");
    }
    imageKey  = String(header?.[imgIdx] || imgIdx);
    serialKey = serialIdx!=null ? String(header?.[serialIdx] || serialIdx) : null;
    return { images: outImgs, serials: outSerials, serialKey, imageKey };
  }

  // ====== 選鍵工具 ======
  function collectKeys(rows){ const s=new Set(); rows.slice(0,100).forEach(r=>Object.keys(r||{}).forEach(k=>s.add(k))); return Array.from(s); }
  function pickFirstExist(keys, pref){ const map=new Map(keys.map(k=>[k.toLowerCase(),k])); for(const p of pref){ const hit=map.get(p.toLowerCase()); if(hit) return hit; } return null; }
  function pickBestShortTextKey(rows){ const keys=collectKeys(rows); let best=null,score=-1; for(const k of keys){ let s=0; for(const r of rows){ const v=toStringTrim(r?.[k]); if(v && v.length<=40) s++; } if(s>score){ score=s; best=k; } } return best||keys[0]; }
  function pickBestSerialKey(rows){ const keys=collectKeys(rows); let best=null,score=-1; for(const k of keys){ let s=0; for(const r of rows){ const v=toStringTrim(r?.[k]); if(v && /[A-Za-z0-9]/.test(v)) s++; } if(s>score){ score=s; best=k; } } return best||keys[0]; }
  function pickBestImageKey(rows, baseHost){ const keys=collectKeys(rows); let best=null,score=-1; for(const k of keys){ let s=0; for(const r of rows){ const v=toStringTrim(r?.[k]); if(findImageInString(v,baseHost)) s++; } if(s>score){ score=s; best=k; } } return best||keys[0]; }

  // ====== 解析/補全圖片 URL ======
  function firstImageFromObject(obj, imageKey, baseHost) {
    if (typeof obj?.[imageKey] === "string") {
      const u = findImageInString(obj[imageKey], baseHost);
      if (u) return u;
    }
    for (const k of Object.keys(obj || {})) {
      const s = toStringTrim(obj[k]);
      const u = findImageInString(s, baseHost);
      if (u) return u;
    }
    return null;
  }
  function findImageInString(s, baseHost){ if(!s||typeof s!=="string")return null; const a=s.match(ABS_IMG_RE); if(a) return a[0]; const r=s.match(REL_IMG_RE); if(r) return resolveToAbsolute(r[1], baseHost); const h=s.match(HOST_IMG_RE); if(h) return resolveToAbsolute(h[1], baseHost); return null; }
  function resolveToAbsolute(urlLike, baseHost){ if(!urlLike) return null; if(/^https?:\/\//i.test(urlLike)) return urlLike; if(/^\/\//.test(urlLike)) return "https:"+urlLike; if(/^\//.test(urlLike)){ const host=toAbsoluteHost(baseHost); return host? host+urlLike : null; } if(/^[a-z0-9.-]+\.[a-z]{2,}\//i.test(urlLike)) return "https://"+urlLike; return null; }
  function toAbsoluteHost(host){ if(!host) return null; if(/^https?:\/\//i.test(host)) return host.replace(/\/+$/,""); return "https://"+String(host).replace(/\/+$/,""); }
  function findImageInArray(arr, baseHost){ for(const it of arr){ if(typeof it==="string"){ const u=findImageInString(it, baseHost); if(u) return u; } } return null; }

  // ====== 陣列列輔助 ======
  function toLower(arr){ if(!Array.isArray(arr)) return null; return arr.map(h=>String(h||"").trim().toLowerCase()); }
  function pickIndexByHeader(headerLower, keysLower){ if(!headerLower) return null; for(const k of keysLower){ const i=headerLower.indexOf(k.toLowerCase()); if(i!==-1) return i; } return null; }
  function getCellString(row, idx){ if(!Array.isArray(row)) return ""; const v=row[idx]; return typeof v==="string"? v.trim() : ""; }
  function toStringTrim(v){ return typeof v==="string"? v.trim() : ""; }

  // ====== Render ======
  function renderPromos(root, list) {
    list.forEach(({ name, img }) => {
      const wrap  = document.createElement("div"); wrap.className = "wrap"; wrap.setAttribute("role","listitem");
      const thumb = document.createElement("div"); thumb.className = "thumb";
      if (img) {
        const im = document.createElement("img"); im.src = img; im.alt = name || "attraction"; im.loading = "lazy"; im.decoding = "async"; im.onerror = () => (im.style.visibility = "hidden");
        thumb.appendChild(im);
      } else {
        const ph = document.createElement("div");
        ph.textContent = "No Image";
        ph.style.width="80px"; ph.style.height="50px"; ph.style.display="flex"; ph.style.alignItems="center"; ph.style.justifyContent="center";
        ph.style.background="#dbeef6"; ph.style.color="#555"; ph.style.fontSize="12px";
        thumb.appendChild(ph);
      }
      const title = document.createElement("div"); title.className = "title"; title.textContent = name || "未命名";
      wrap.appendChild(thumb); wrap.appendChild(title); root.appendChild(wrap);
    });
  }

  // 這個用在「追加」而不是「整批重畫」
  function appendGallery(root, list) {
    list.forEach(({ name, img }, idxPage) => {
      const card = document.createElement("div");
      const globalIndex = CURSOR + idxPage;
      const isBig = (globalIndex >= 3 && (globalIndex - 3) % 5 === 0);
      // 整體第4(索引3)與第9(索引8)才是 big
      card.className = isBig ? "card big" : "card";
      card.setAttribute("role","listitem");

      if (img) {
        const im = document.createElement("img"); im.src = img; im.alt = name || "attraction"; im.loading = "lazy"; im.decoding = "async"; im.onerror = () => (im.style.display = "none");
        card.appendChild(im);
      } else {
        const ph = document.createElement("div");
        ph.style.width="100%"; ph.style.height="100%"; ph.style.background="#e7f4ff"; ph.style.display="flex"; ph.style.alignItems="center"; ph.style.justifyContent="center"; ph.style.color="#666"; ph.textContent="No Image";
        card.appendChild(ph);
      }
      const star = document.createElement("div"); star.className = "star"; star.textContent = "⭐";
      const caption = document.createElement("div"); caption.className = "caption"; caption.textContent = name || "未命名";
      card.appendChild(star); card.appendChild(caption);
      root.appendChild(card);
    });
  }

  function showFallback(root, text) {
    const msg = document.createElement("div");
    msg.style.padding="16px"; msg.style.background="#fee"; msg.style.border="1px solid #faa";
    msg.style.borderRadius="8px"; msg.style.marginTop="12px";
    msg.textContent = text;
    root.appendChild(msg);
  }
})();
