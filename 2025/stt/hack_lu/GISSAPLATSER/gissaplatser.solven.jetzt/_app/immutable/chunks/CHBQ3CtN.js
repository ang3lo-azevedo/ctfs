import { w as Ee, o as De, c as wt } from "./Cp4LAmbD.js";
import { ae as T, y as x, A as P, aw as Be } from "./DgDvesj-.js";
class le {
  constructor(t, n) {
    this.status = t;
    if (typeof n == "string") {
      this.body = {
        message: n
      };
    } else if (n) {
      this.body = n;
    } else {
      this.body = {
        message: `Error: ${t}`
      };
    }
  }
  toString() {
    return JSON.stringify(this.body);
  }
}
class Se {
  constructor(t, n) {
    this.status = t;
    this.location = n;
  }
}
class Re extends Error {
  constructor(t, n, r) {
    super(r);
    this.status = t;
    this.text = n;
  }
}
new URL("sveltekit-internal://");
function yt(e, t) {
  return e === "/" || t === "ignore" ? e : t === "never" ? e.endsWith("/") ? e.slice(0, -1) : e : t === "always" && !e.endsWith("/") ? e + "/" : e;
}
function vt(e) {
  return e.split("%25").map(decodeURI).join("%25");
}
function bt(e) {
  for (const t in e) e[t] = decodeURIComponent(e[t]);
  return e;
}
function _e({
  href: e
}) {
  return e.split("#")[0];
}
function kt(e, t, n, r = false) {
  const a = new URL(e);
  Object.defineProperty(a, "searchParams", {
    value: new Proxy(a.searchParams, {
      get(i, o) {
        if (o === "get" || o === "getAll" || o === "has") {
          return f => (n(f), i[o](f));
        }
        t();
        const c = Reflect.get(i, o);
        return typeof c == "function" ? c.bind(i) : c;
      }
    }),
    enumerable: true,
    configurable: true
  });
  const s = ["href", "pathname", "search", "toString", "toJSON"];
  if (r) {
    s.push("hash");
  }
  for (const i of s) Object.defineProperty(a, i, {
    get() {
      t();
      return e[i];
    },
    enumerable: true,
    configurable: true
  });
  return a;
}
function At(...e) {
  let t = 5381;
  for (const n of e) if (typeof n == "string") {
    let r = n.length;
    for (; r;) {
      t = t * 33 ^ n.charCodeAt(--r);
    }
  } else if (ArrayBuffer.isView(n)) {
    const r = new Uint8Array(n.buffer, n.byteOffset, n.byteLength);
    let a = r.length;
    for (; a;) {
      t = t * 33 ^ r[--a];
    }
  } else {
    throw new TypeError("value must be a string or TypedArray");
  }
  return (t >>> 0).toString(36);
}
function Et(e) {
  const t = atob(e);
  const n = new Uint8Array(t.length);
  for (let r = 0; r < t.length; r++) {
    n[r] = t.charCodeAt(r);
  }
  return n.buffer;
}
const St = window.fetch;
window.fetch = (e, t) => ((e instanceof Request ? e.method : t?.method || "GET") !== "GET" && G.delete(Ie(e)), St(e, t));
const G = new Map();
function Rt(e, t) {
  const n = Ie(e, t);
  const r = document.querySelector(n);
  if (r?.textContent) {
    let {
      body: a,
      ...s
    } = JSON.parse(r.textContent);
    const i = r.getAttribute("data-ttl");
    if (i) {
      G.set(n, {
        body: a,
        init: s,
        ttl: 1e3 * Number(i)
      });
    }
    if (r.getAttribute("data-b64") !== null) {
      a = Et(a);
    }
    return Promise.resolve(new Response(a, s));
  }
  return window.fetch(e, t);
}
function It(e, t, n) {
  if (G.size > 0) {
    const r = Ie(e, n);
    const a = G.get(r);
    if (a) {
      if (performance.now() < a.ttl && ["default", "force-cache", "only-if-cached", undefined].includes(n?.cache)) {
        return new Response(a.body, a.init);
      }
      G.delete(r);
    }
  }
  return window.fetch(t, n);
}
function Ie(e, t) {
  let r = `script[data-sveltekit-fetched][data-url=${JSON.stringify(e instanceof Request ? e.url : e)}]`;
  if (t?.headers || t?.body) {
    const a = [];
    if (t.headers) {
      a.push([...new Headers(t.headers)].join(","));
    }
    if (t.body && (typeof t.body == "string" || ArrayBuffer.isView(t.body))) {
      a.push(t.body);
    }
    r += `[data-hash="${At(...a)}"]`;
  }
  return r;
}
const Ut = /^(\[)?(\.\.\.)?(\w+)(?:=(\w+))?(\])?$/;
function Lt(e) {
  const t = [];
  return {
    pattern: e === "/" ? /^\/$/ : new RegExp(`^${xt(e).map(r => {
      const a = /^\[\.\.\.(\w+)(?:=(\w+))?\]$/.exec(r);
      if (a) {
        t.push({
          name: a[1],
          matcher: a[2],
          optional: false,
          rest: true,
          chained: true
        });
        return "(?:/(.*))?";
      }
      const s = /^\[\[(\w+)(?:=(\w+))?\]\]$/.exec(r);
      if (s) {
        t.push({
          name: s[1],
          matcher: s[2],
          optional: true,
          rest: false,
          chained: true
        });
        return "(?:/([^/]+))?";
      }
      if (!r) {
        return;
      }
      const i = r.split(/\[(.+?)\](?!\])/);
      return "/" + i.map((c, f) => {
        if (f % 2) {
          if (c.startsWith("x+")) {
            return me(String.fromCharCode(parseInt(c.slice(2), 16)));
          }
          if (c.startsWith("u+")) {
            return me(String.fromCharCode(...c.slice(2).split("-").map(m => parseInt(m, 16))));
          }
          const d = Ut.exec(c);
          const [, h, u, l, p] = d;
          t.push({
            name: l,
            matcher: p,
            optional: !!h,
            rest: !!u,
            chained: u ? f === 1 && i[0] === "" : false
          });
          return u ? "(.*?)" : h ? "([^/]*)?" : "([^/]+?)";
        }
        return me(c);
      }).join("");
    }).join("")}/?$`),
    params: t
  };
}
function Tt(e) {
  return e !== "" && !/^\([^)]+\)$/.test(e);
}
function xt(e) {
  return e.slice(1).split("/").filter(Tt);
}
function Pt(e, t, n) {
  const r = {};
  const a = e.slice(1);
  const s = a.filter(o => o !== undefined);
  let i = 0;
  for (let o = 0; o < t.length; o += 1) {
    const c = t[o];
    let f = a[o - i];
    if (c.chained && c.rest && i) {
      f = a.slice(o - i, o + 1).filter(d => d).join("/");
      i = 0;
    }
    if (f === undefined) {
      if (c.rest) {
        r[c.name] = "";
      }
      continue;
    }
    if (!c.matcher || n[c.matcher](f)) {
      r[c.name] = f;
      const d = t[o + 1];
      const h = a[o + 1];
      if (d && !d.rest && d.optional && h && c.chained) {
        i = 0;
      }
      if (!d && !h && Object.keys(r).length === s.length) {
        i = 0;
      }
      continue;
    }
    if (c.optional && c.chained) {
      i++;
      continue;
    }
    return;
  }
  if (!i) {
    return r;
  }
}
function me(e) {
  return e.normalize().replace(/[[\]]/g, "\\$&").replace(/%/g, "%25").replace(/\//g, "%2[Ff]").replace(/\?/g, "%3[Ff]").replace(/#/g, "%23").replace(/[.*+?^${}()|\\]/g, "\\$&");
}
function Ct({
  nodes: e,
  server_loads: t,
  dictionary: n,
  matchers: r
}) {
  const a = new Set(t);
  return Object.entries(n).map(([o, [c, f, d]]) => {
    const {
      pattern: h,
      params: u
    } = Lt(o);
    const l = {
      id: o,
      exec: p => {
        const m = h.exec(p);
        if (m) {
          return Pt(m, u, r);
        }
      },
      errors: [1, ...(d || [])].map(p => e[p]),
      layouts: [0, ...(f || [])].map(i),
      leaf: s(c)
    };
    l.errors.length = l.layouts.length = Math.max(l.errors.length, l.layouts.length);
    return l;
  });
  function s(o) {
    const c = o < 0;
    if (c) {
      o = ~o;
    }
    return [c, e[o]];
  }
  function i(o) {
    return o === undefined ? o : [a.has(o), e[o]];
  }
}
function ze(e, t = JSON.parse) {
  try {
    return t(sessionStorage[e]);
  } catch {}
}
function Fe(e, t, n = JSON.stringify) {
  const r = n(t);
  try {
    sessionStorage[e] = r;
  } catch {}
}
const U = globalThis.__sveltekit_wwkpge?.base ?? "";
const Ot = globalThis.__sveltekit_wwkpge?.assets ?? U;
const j = {
  tap: 1,
  hover: 2,
  viewport: 3,
  eager: 4,
  off: -1,
  false: -1
};
const Z = location.origin;
function Ue(e) {
  if (e instanceof URL) {
    return e;
  }
  let t = document.baseURI;
  if (!t) {
    const n = document.getElementsByTagName("base");
    t = n.length ? n[0].href : document.URL;
  }
  return new URL(e, t);
}
function fe() {
  return {
    x: pageXOffset,
    y: pageYOffset
  };
}
function B(e, t) {
  return e.getAttribute(`data-sveltekit-${t}`);
}
const Ve = {
  ...j,
  "": 2
};
function et(e) {
  let t = e.assignedSlot ?? e.parentNode;
  if (t?.nodeType === 11) {
    t = t.host;
  }
  return t;
}
function tt(e, t) {
  for (; e && e !== t;) {
    if (e.nodeName.toUpperCase() === "A" && e.hasAttribute("href")) {
      return e;
    }
    e = et(e);
  }
}
function ve(e, t, n) {
  let r;
  try {
    r = new URL(e instanceof SVGAElement ? e.href.baseVal : e.href, document.baseURI);
    if (n && r.hash.match(/^#[^/]/)) {
      const o = location.hash.split("#")[1] || "/";
      r.hash = `#${o}${r.hash}`;
    }
  } catch {}
  const a = e instanceof SVGAElement ? e.target.baseVal : e.target;
  const s = !r || !!a || ue(r, t, n) || (e.getAttribute("rel") || "").split(/\s+/).includes("external");
  const i = r?.origin === Z && e.hasAttribute("download");
  return {
    url: r,
    external: s,
    target: a,
    download: i
  };
}
function te(e) {
  let t = null;
  let n = null;
  let r = null;
  let a = null;
  let s = null;
  let i = null;
  let o = e;
  for (; o && o !== document.documentElement;) {
    if (r === null) {
      r = B(o, "preload-code");
    }
    if (a === null) {
      a = B(o, "preload-data");
    }
    if (t === null) {
      t = B(o, "keepfocus");
    }
    if (n === null) {
      n = B(o, "noscroll");
    }
    if (s === null) {
      s = B(o, "reload");
    }
    if (i === null) {
      i = B(o, "replacestate");
    }
    o = et(o);
  }
  function c(f) {
    switch (f) {
      case "":
      case "true":
        return true;
      case "off":
      case "false":
        return false;
      default:
        return;
    }
  }
  return {
    preload_code: Ve[r ?? "off"],
    preload_data: Ve[a ?? "off"],
    keepfocus: c(t),
    noscroll: c(n),
    reload: c(s),
    replace_state: c(i)
  };
}
function qe(e) {
  const t = Ee(e);
  let n = true;
  function r() {
    n = true;
    t.update(i => i);
  }
  function a(i) {
    n = false;
    t.set(i);
  }
  function s(i) {
    let o;
    return t.subscribe(c => {
      if (o === undefined || n && c !== o) {
        i(o = c);
      }
    });
  }
  return {
    notify: r,
    set: a,
    subscribe: s
  };
}
const nt = {
  v: () => {}
};
function $t() {
  const {
    set: e,
    subscribe: t
  } = Ee(false);
  let n;
  async function r() {
    clearTimeout(n);
    try {
      const a = await fetch(`${Ot}/_app/version.json`, {
        headers: {
          pragma: "no-cache",
          "cache-control": "no-cache"
        }
      });
      if (!a.ok) {
        return false;
      }
      const i = (await a.json()).version !== "1760728545651";
      if (i) {
        e(true);
        nt.v();
        clearTimeout(n);
      }
      return i;
    } catch {
      return false;
    }
  }
  return {
    subscribe: t,
    check: r
  };
}
function ue(e, t, n) {
  return e.origin !== Z || !e.pathname.startsWith(t) ? true : n ? !(e.pathname === t + "/" || e.pathname === t + "/index.html" || e.protocol === "file:" && e.pathname.replace(/\/[^/]+\.html?$/, "") === t) : false;
}
function kn(e) {}
function Me(e) {
  const t = Bt(e);
  const n = new ArrayBuffer(t.length);
  const r = new DataView(n);
  for (let a = 0; a < n.byteLength; a++) {
    r.setUint8(a, t.charCodeAt(a));
  }
  return n;
}
function Bt(e) {
  if (e.length % 4 === 0) {
    e = e.replace(/==?$/, "");
  }
  let t = "";
  let n = 0;
  let r = 0;
  for (let a = 0; a < e.length; a++) {
    n <<= 6;
    n |= "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".indexOf(e[a]);
    r += 6;
    if (r === 24) {
      t += String.fromCharCode((n & 16711680) >> 16);
      t += String.fromCharCode((n & 65280) >> 8);
      t += String.fromCharCode(n & 255);
      n = r = 0;
    }
  }
  if (r === 12) {
    n >>= 4;
    t += String.fromCharCode(n);
  } else if (r === 18) {
    n >>= 2;
    t += String.fromCharCode((n & 65280) >> 8);
    t += String.fromCharCode(n & 255);
  }
  return t;
}
const Ft = -1;
const Vt = -2;
const qt = -3;
const Mt = -4;
const Gt = -5;
const Ht = -6;
function Kt(e, t) {
  if (typeof e == "number") {
    return a(e, true);
  }
  if (!Array.isArray(e) || e.length === 0) {
    throw new Error("Invalid input");
  }
  const r = Array(e.length);
  function a(s, i = false) {
    if (s === Ft) {
      return;
    }
    if (s === qt) {
      return NaN;
    }
    if (s === Mt) {
      return Infinity;
    }
    if (s === Gt) {
      return -Infinity;
    }
    if (s === Ht) {
      return -0;
    }
    if (i) {
      throw new Error("Invalid input");
    }
    if (s in r) {
      return r[s];
    }
    const o = e[s];
    if (!o || typeof o != "object") {
      r[s] = o;
    } else if (Array.isArray(o)) {
      if (typeof o[0] == "string") {
        const c = o[0];
        const f = t?.[c];
        if (f) {
          return r[s] = f(a(o[1]));
        }
        switch (c) {
          case "Date":
            r[s] = new Date(o[1]);
            break;
          case "Set":
            const d = new Set();
            r[s] = d;
            for (let l = 1; l < o.length; l += 1) {
              d.add(a(o[l]));
            }
            break;
          case "Map":
            const h = new Map();
            r[s] = h;
            for (let l = 1; l < o.length; l += 2) {
              h.set(a(o[l]), a(o[l + 1]));
            }
            break;
          case "RegExp":
            r[s] = new RegExp(o[1], o[2]);
            break;
          case "Object":
            r[s] = Object(o[1]);
            break;
          case "BigInt":
            r[s] = BigInt(o[1]);
            break;
          case "null":
            const u = Object.create(null);
            r[s] = u;
            for (let l = 1; l < o.length; l += 2) {
              u[o[l]] = a(o[l + 1]);
            }
            break;
          case "Int8Array":
          case "Uint8Array":
          case "Uint8ClampedArray":
          case "Int16Array":
          case "Uint16Array":
          case "Int32Array":
          case "Uint32Array":
          case "Float32Array":
          case "Float64Array":
          case "BigInt64Array":
          case "BigUint64Array":
            {
              const l = globalThis[c];
              const p = o[1];
              const m = Me(p);
              const _ = new l(m);
              r[s] = _;
              break;
            }
          case "ArrayBuffer":
            {
              const l = o[1];
              const p = Me(l);
              r[s] = p;
              break;
            }
          default:
            throw new Error(`Unknown type ${c}`);
        }
      } else {
        const c = new Array(o.length);
        r[s] = c;
        for (let f = 0; f < o.length; f += 1) {
          const d = o[f];
          if (d !== Vt) {
            c[f] = a(d);
          }
        }
      }
    } else {
      const c = {};
      r[s] = c;
      for (const f in o) {
        const d = o[f];
        c[f] = a(d);
      }
    }
    return r[s];
  }
  return a(0);
}
const rt = new Set(["load", "prerender", "csr", "ssr", "trailingSlash", "config"]);
[...rt];
const Wt = new Set([...rt]);
[...Wt];
function Yt(e) {
  return e.filter(t => t != null);
}
function ne(e) {
  return e instanceof le || e instanceof Re ? e.status : 500;
}
function Xt(e) {
  return e instanceof Re ? e.text : "Internal Error";
}
let E;
let J;
let we;
const Zt = De.toString().includes("$$") || /function \w+\(\) \{\}/.test(De.toString());
if (Zt) {
  E = {
    data: {},
    form: null,
    error: null,
    params: {},
    route: {
      id: null
    },
    state: {},
    status: -1,
    url: new URL("https://example.com")
  };
  J = {
    current: null
  };
  we = {
    current: false
  };
} else {
  E = new class {
    #e = T({});
    get data() {
      return x(this.#e);
    }
    set data(t) {
      P(this.#e, t);
    }
    #t = T(null);
    get form() {
      return x(this.#t);
    }
    set form(t) {
      P(this.#t, t);
    }
    #n = T(null);
    get error() {
      return x(this.#n);
    }
    set error(t) {
      P(this.#n, t);
    }
    #r = T({});
    get params() {
      return x(this.#r);
    }
    set params(t) {
      P(this.#r, t);
    }
    #a = T({
      id: null
    });
    get route() {
      return x(this.#a);
    }
    set route(t) {
      P(this.#a, t);
    }
    #o = T({});
    get state() {
      return x(this.#o);
    }
    set state(t) {
      P(this.#o, t);
    }
    #s = T(-1);
    get status() {
      return x(this.#s);
    }
    set status(t) {
      P(this.#s, t);
    }
    #i = T(new URL("https://example.com"));
    get url() {
      return x(this.#i);
    }
    set url(t) {
      P(this.#i, t);
    }
  }();
  J = new class {
    #e = T(null);
    get current() {
      return x(this.#e);
    }
    set current(t) {
      P(this.#e, t);
    }
  }();
  we = new class {
    #e = T(false);
    get current() {
      return x(this.#e);
    }
    set current(t) {
      P(this.#e, t);
    }
  }();
  nt.v = () => we.current = true;
}
function Qt(e) {
  Object.assign(E, e);
}
function nn(e) {
  return e.endsWith(".html") ? e.replace(/\.html$/, ".html__data.json") : e.replace(/\/$/, "") + "/__data.json";
}
const {
  tick: rn
} = wt;
const an = new Set(["icon", "shortcut icon", "apple-touch-icon"]);
const D = ze("sveltekit:scroll") ?? {};
const z = ze("sveltekit:snapshot") ?? {};
const N = {
  url: qe({}),
  page: qe({}),
  navigating: Ee(null),
  updated: $t()
};
function Le(e) {
  D[e] = fe();
}
function on(e, t) {
  let n = e + 1;
  for (; D[n];) {
    delete D[n];
    n += 1;
  }
  for (n = t + 1; z[n];) {
    delete z[n];
    n += 1;
  }
}
function q(e) {
  location.href = e.href;
  return new Promise(() => {});
}
async function at() {
  if ("serviceWorker" in navigator) {
    const e = await navigator.serviceWorker.getRegistration(U || "/");
    if (e) {
      await e.update();
    }
  }
}
function Ge() {}
let Te;
let be;
let re;
let C;
let ke;
let v;
const ae = [];
const oe = [];
let O = null;
const ee = new Map();
const ot = new Set();
const sn = new Set();
const H = new Set();
let y = {
  branch: [],
  error: null,
  url: null
};
let xe = false;
let se = false;
let He = true;
let X = false;
let M = false;
let st = false;
let Pe = false;
let it;
let k;
let I;
let $;
const K = new Set();
const Ke = new Map();
async function Rn(e, t, n) {
  if (document.URL !== location.href) {
    location.href = location.href;
  }
  v = e;
  n?.remote;
  await e.hooks.init?.();
  Te = Ct(e);
  C = document.documentElement;
  ke = t;
  be = e.nodes[0];
  re = e.nodes[1];
  be();
  re();
  k = history.state?.["sveltekit:history"];
  I = history.state?.["sveltekit:navigation"];
  if (!k) {
    k = I = Date.now();
    history.replaceState({
      ...history.state,
      "sveltekit:history": k,
      "sveltekit:navigation": I
    }, "");
  }
  const r = D[k];
  function a() {
    if (r) {
      history.scrollRestoration = "manual";
      scrollTo(r.x, r.y);
    }
  }
  if (n) {
    a();
    await mn(ke, n);
  } else {
    await W({
      type: "enter",
      url: Ue(v.hash ? yn(new URL(location.href)) : location.href),
      replace_state: true
    });
    a();
  }
  _n();
}
function cn() {
  ae.length = 0;
  Pe = false;
}
function ct(e) {
  if (oe.some(t => t?.snapshot)) {
    z[e] = oe.map(t => t?.snapshot?.capture());
  }
}
function lt(e) {
  z[e]?.forEach((t, n) => {
    oe[n]?.snapshot?.restore(t);
  });
}
function We() {
  Le(k);
  Fe("sveltekit:scroll", D);
  ct(I);
  Fe("sveltekit:snapshot", z);
}
async function Ce(e, t, n, r) {
  let a;
  const s = await W({
    type: "goto",
    url: Ue(e),
    keepfocus: t.keepFocus,
    noscroll: t.noScroll,
    replace_state: t.replaceState,
    state: t.state,
    redirect_count: n,
    nav_token: r,
    accept: () => {
      if (t.invalidateAll) {
        Pe = true;
        a = [...Ke.keys()];
      }
      if (t.invalidate) {
        t.invalidate.forEach(gn);
      }
    }
  });
  if (t.invalidateAll) {
    Be().then(Be).then(() => {
      Ke.forEach(({
        resource: i
      }, o) => {
        if (a?.includes(o)) {
          i.refresh?.();
        }
      });
    });
  }
  return s;
}
async function ln(e) {
  if (e.id !== O?.id) {
    const t = {};
    K.add(t);
    O = {
      id: e.id,
      token: t,
      promise: dt({
        ...e,
        preload: t
      }).then(n => (K.delete(t), n.type === "loaded" && n.state.error && (O = null), n))
    };
  }
  return O.promise;
}
async function ye(e) {
  const t = (await he(e, false))?.route;
  if (t) {
    await Promise.all([...t.layouts, t.leaf].map(n => n?.[1]()));
  }
}
function ft(e, t, n) {
  y = e.state;
  const r = document.querySelector("style[data-sveltekit]");
  if (r) {
    r.remove();
  }
  Object.assign(E, e.props.page);
  it = new v.root({
    target: t,
    props: {
      ...e.props,
      stores: N,
      components: oe
    },
    hydrate: n,
    sync: false
  });
  lt(I);
  if (n) {
    const a = {
      from: null,
      to: {
        params: y.params,
        route: {
          id: y.route?.id ?? null
        },
        url: new URL(location.href)
      },
      willUnload: false,
      type: "enter",
      complete: Promise.resolve()
    };
    H.forEach(s => s(a));
  }
  se = true;
}
function ie({
  url: e,
  params: t,
  branch: n,
  status: r,
  error: a,
  route: s,
  form: i
}) {
  let o = "never";
  if (U && (e.pathname === U || e.pathname === U + "/")) {
    o = "always";
  } else {
    for (const l of n) if (l?.slash !== undefined) {
      o = l.slash;
    }
  }
  e.pathname = yt(e.pathname, o);
  e.search = e.search;
  const c = {
    type: "loaded",
    state: {
      url: e,
      params: t,
      branch: n,
      error: a,
      route: s
    },
    props: {
      constructors: Yt(n).map(l => l.node.component),
      page: $e(E)
    }
  };
  if (i !== undefined) {
    c.props.form = i;
  }
  let f = {};
  let d = !E;
  let h = 0;
  for (let l = 0; l < Math.max(n.length, y.branch.length); l += 1) {
    const p = n[l];
    const m = y.branch[l];
    if (p?.data !== m?.data) {
      d = true;
    }
    if (p) {
      f = {
        ...f,
        ...p.data
      };
      if (d) {
        c.props[`data_${h}`] = f;
      }
      h += 1;
    }
  }
  if (!y.url || e.href !== y.url.href || y.error !== a || i !== undefined && i !== E.form || d) {
    c.props.page = {
      error: a,
      params: t,
      route: {
        id: s?.id ?? null
      },
      state: {},
      status: r,
      url: new URL(e),
      form: i ?? null,
      data: d ? f : E.data
    };
  }
  return c;
}
async function Oe({
  loader: e,
  parent: t,
  url: n,
  params: r,
  route: a,
  server_data_node: s
}) {
  let i = null;
  let o = true;
  const c = {
    dependencies: new Set(),
    params: new Set(),
    parent: false,
    route: false,
    url: false,
    search_params: new Set()
  };
  const f = await e();
  if (f.universal?.load) {
    let d = function (...u) {
      for (const l of u) {
        const {
          href: p
        } = new URL(l, n);
        c.dependencies.add(p);
      }
    };
    const h = {
      route: new Proxy(a, {
        get: (u, l) => (o && (c.route = true), u[l])
      }),
      params: new Proxy(r, {
        get: (u, l) => (o && c.params.add(l), u[l])
      }),
      data: s?.data ?? null,
      url: kt(n, () => {
        if (o) {
          c.url = true;
        }
      }, u => {
        if (o) {
          c.search_params.add(u);
        }
      }, v.hash),
      async fetch(u, l) {
        if (u instanceof Request) {
          l = {
            body: u.method === "GET" || u.method === "HEAD" ? undefined : await u.blob(),
            cache: u.cache,
            credentials: u.credentials,
            headers: [...u.headers].length > 0 ? u?.headers : undefined,
            integrity: u.integrity,
            keepalive: u.keepalive,
            method: u.method,
            mode: u.mode,
            redirect: u.redirect,
            referrer: u.referrer,
            referrerPolicy: u.referrerPolicy,
            signal: u.signal,
            ...l
          };
        }
        const {
          resolved: p,
          promise: m
        } = ut(u, l, n);
        if (o) {
          d(p.href);
        }
        return m;
      },
      setHeaders: () => {},
      depends: d,
      parent() {
        if (o) {
          c.parent = true;
        }
        return t();
      },
      untrack(u) {
        o = false;
        try {
          return u();
        } finally {
          o = true;
        }
      }
    };
    i = (await f.universal.load.call(null, h)) ?? null;
  }
  return {
    node: f,
    loader: e,
    server: s,
    universal: f.universal?.load ? {
      type: "data",
      data: i,
      uses: c
    } : null,
    data: i ?? s?.data ?? null,
    slash: f.universal?.trailingSlash ?? s?.slash
  };
}
function ut(e, t, n) {
  let r = e instanceof Request ? e.url : e;
  const a = new URL(r, n);
  if (a.origin === n.origin) {
    r = a.href.slice(n.origin.length);
  }
  const s = se ? It(r, a.href, t) : Rt(r, t);
  return {
    resolved: a,
    promise: s
  };
}
function Ye(e, t, n, r, a, s) {
  if (Pe) {
    return true;
  }
  if (!a) {
    return false;
  }
  if (a.parent && e || a.route && t || a.url && n) {
    return true;
  }
  for (const i of a.search_params) if (r.has(i)) {
    return true;
  }
  for (const i of a.params) if (s[i] !== y.params[i]) {
    return true;
  }
  for (const i of a.dependencies) if (ae.some(o => o(new URL(i)))) {
    return true;
  }
  return false;
}
function Ne(e, t) {
  return e?.type === "data" ? e : e?.type === "skip" ? t ?? null : null;
}
function fn(e, t) {
  if (!e) {
    return new Set(t.searchParams.keys());
  }
  const n = new Set([...e.searchParams.keys(), ...t.searchParams.keys()]);
  for (const r of n) {
    const a = e.searchParams.getAll(r);
    const s = t.searchParams.getAll(r);
    if (a.every(i => s.includes(i)) && s.every(i => a.includes(i))) {
      n.delete(r);
    }
  }
  return n;
}
function Je({
  error: e,
  url: t,
  route: n,
  params: r
}) {
  return {
    type: "loaded",
    state: {
      error: e,
      url: t,
      route: n,
      params: r,
      branch: []
    },
    props: {
      page: $e(E),
      constructors: []
    }
  };
}
async function dt({
  id: e,
  invalidating: t,
  url: n,
  params: r,
  route: a,
  preload: s
}) {
  if (O?.id === e) {
    K.delete(O.token);
    return O.promise;
  }
  const {
    errors: i,
    layouts: o,
    leaf: c
  } = a;
  const f = [...o, c];
  i.forEach(g => g?.().catch(() => {}));
  f.forEach(g => g?.[1]().catch(() => {}));
  let d = null;
  const h = y.url ? e !== ce(y.url) : false;
  const u = y.route ? a.id !== y.route.id : false;
  const l = fn(y.url, n);
  let p = false;
  const m = f.map((g, w) => {
    const b = y.branch[w];
    const A = !!g?.[0] && (b?.loader !== g[1] || Ye(p, u, h, l, b.server?.uses, r));
    if (A) {
      p = true;
    }
    return A;
  });
  if (m.some(Boolean)) {
    try {
      d = await gt(n, m);
    } catch (g) {
      const w = await V(g, {
        url: n,
        params: r,
        route: {
          id: e
        }
      });
      return K.has(s) ? Je({
        error: w,
        url: n,
        params: r,
        route: a
      }) : de({
        status: ne(g),
        error: w,
        url: n,
        route: a
      });
    }
    if (d.type === "redirect") {
      return d;
    }
  }
  const _ = d?.nodes;
  let R = false;
  const S = f.map(async (g, w) => {
    if (!g) {
      return;
    }
    const b = y.branch[w];
    const A = _?.[w];
    if ((!A || A.type === "skip") && g[1] === b?.loader && !Ye(R, u, h, l, b.universal?.uses, r)) {
      return b;
    }
    R = true;
    if (A?.type === "error") {
      throw A;
    }
    return Oe({
      loader: g[1],
      url: n,
      params: r,
      route: a,
      parent: async () => {
        const pe = {};
        for (let ge = 0; ge < w; ge += 1) {
          Object.assign(pe, (await S[ge])?.data);
        }
        return pe;
      },
      server_data_node: Ne(A === undefined && g[0] ? {
        type: "skip"
      } : A ?? null, g[0] ? b?.server : undefined)
    });
  });
  for (const g of S) g.catch(() => {});
  const L = [];
  for (let g = 0; g < f.length; g += 1) {
    if (f[g]) {
      try {
        L.push(await S[g]);
      } catch (w) {
        if (w instanceof Se) {
          return {
            type: "redirect",
            location: w.location
          };
        }
        if (K.has(s)) {
          return Je({
            error: await V(w, {
              params: r,
              url: n,
              route: {
                id: a.id
              }
            }),
            url: n,
            params: r,
            route: a
          });
        }
        let b = ne(w);
        let A;
        if (_?.includes(w)) {
          b = w.status ?? b;
          A = w.error;
        } else if (w instanceof le) {
          A = w.body;
        } else {
          if (await N.updated.check()) {
            await at();
            return await q(n);
          }
          A = await V(w, {
            params: r,
            url: n,
            route: {
              id: a.id
            }
          });
        }
        const Q = await un(g, L, i);
        return Q ? ie({
          url: n,
          params: r,
          branch: L.slice(0, Q.idx).concat(Q.node),
          status: b,
          error: A,
          route: a
        }) : await pt(n, {
          id: a.id
        }, A, b);
      }
    } else {
      L.push(undefined);
    }
  }
  return ie({
    url: n,
    params: r,
    branch: L,
    status: 200,
    error: null,
    route: a,
    form: t ? undefined : null
  });
}
async function un(e, t, n) {
  for (; e--;) {
    if (n[e]) {
      let r = e;
      for (; !t[r];) {
        r -= 1;
      }
      try {
        return {
          idx: r + 1,
          node: {
            node: await n[e](),
            loader: n[e],
            data: {},
            server: null,
            universal: null
          }
        };
      } catch {
        continue;
      }
    }
  }
}
async function de({
  status: e,
  error: t,
  url: n,
  route: r
}) {
  const a = {};
  let s = null;
  if (v.server_loads[0] === 0) {
    try {
      const o = await gt(n, [true]);
      if (o.type !== "data" || o.nodes[0] && o.nodes[0].type !== "data") {
        throw 0;
      }
      s = o.nodes[0] ?? null;
    } catch {
      if (n.origin !== Z || n.pathname !== location.pathname || xe) {
        await q(n);
      }
    }
  }
  try {
    const o = await Oe({
      loader: be,
      url: n,
      params: a,
      route: r,
      parent: () => Promise.resolve({}),
      server_data_node: Ne(s)
    });
    const c = {
      node: await re(),
      loader: re,
      universal: null,
      server: null,
      data: null
    };
    return ie({
      url: n,
      params: a,
      branch: [o, c],
      status: e,
      error: t,
      route: null
    });
  } catch (o) {
    if (o instanceof Se) {
      return Ce(new URL(o.location, location.href), {}, 0);
    }
    throw o;
  }
}
async function dn(e) {
  const t = e.href;
  if (ee.has(t)) {
    return ee.get(t);
  }
  let n;
  try {
    const r = (async () => {
      let a = (await v.hooks.reroute({
        url: new URL(e),
        fetch: async (s, i) => ut(s, i, e).promise
      })) ?? e;
      if (typeof a == "string") {
        const s = new URL(e);
        if (v.hash) {
          s.hash = a;
        } else {
          s.pathname = a;
        }
        a = s;
      }
      return a;
    })();
    ee.set(t, r);
    n = await r;
  } catch {
    ee.delete(t);
    return;
  }
  return n;
}
async function he(e, t) {
  if (e && !ue(e, U, v.hash)) {
    const n = await dn(e);
    if (!n) {
      return;
    }
    const r = hn(n);
    for (const a of Te) {
      const s = a.exec(r);
      if (s) {
        return {
          id: ce(e),
          invalidating: t,
          route: a,
          params: bt(s),
          url: e
        };
      }
    }
  }
}
function hn(e) {
  return vt(v.hash ? e.hash.replace(/^#/, "").replace(/[?#].+/, "") : e.pathname.slice(U.length)) || "/";
}
function ce(e) {
  return (v.hash ? e.hash.replace(/^#/, "") : e.pathname) + e.search;
}
function ht({
  url: e,
  type: t,
  intent: n,
  delta: r
}) {
  let a = false;
  const s = je(y, n, e, t);
  if (r !== undefined) {
    s.navigation.delta = r;
  }
  const i = {
    ...s.navigation,
    cancel: () => {
      a = true;
      s.reject(new Error("navigation cancelled"));
    }
  };
  if (!X) {
    ot.forEach(o => o(i));
  }
  return a ? null : s;
}
async function W({
  type: e,
  url: t,
  popped: n,
  keepfocus: r,
  noscroll: a,
  replace_state: s,
  state: i = {},
  redirect_count: o = 0,
  nav_token: c = {},
  accept: f = Ge,
  block: d = Ge
}) {
  const h = $;
  $ = c;
  const u = await he(t, false);
  const l = e === "enter" ? je(y, u, t, e) : ht({
    url: t,
    type: e,
    delta: n?.delta,
    intent: u
  });
  if (!l) {
    d();
    if ($ === c) {
      $ = h;
    }
    return;
  }
  const p = k;
  const m = I;
  f();
  X = true;
  if (se && l.navigation.type !== "enter") {
    N.navigating.set(J.current = l.navigation);
  }
  let _ = u && (await dt(u));
  if (!_) {
    if (ue(t, U, v.hash)) {
      return await q(t);
    }
    _ = await pt(t, {
      id: null
    }, await V(new Re(404, "Not Found", `Not found: ${t.pathname}`), {
      url: t,
      params: {},
      route: {
        id: null
      }
    }), 404);
  }
  t = u?.url || t;
  if ($ !== c) {
    l.reject(new Error("navigation aborted"));
    return false;
  }
  if (_.type === "redirect") {
    if (o >= 20) {
      _ = await de({
        status: 500,
        error: await V(new Error("Redirect loop"), {
          url: t,
          params: {},
          route: {
            id: null
          }
        }),
        url: t,
        route: {
          id: null
        }
      });
    } else {
      await Ce(new URL(_.location, t).href, {}, o + 1, c);
      return false;
    }
  } else if (_.props.page.status >= 400 && (await N.updated.check())) {
    await at();
    await q(t);
  }
  cn();
  Le(p);
  ct(m);
  if (_.props.page.url.pathname !== t.pathname) {
    t.pathname = _.props.page.url.pathname;
  }
  i = n ? n.state : i;
  if (!n) {
    const g = s ? 0 : 1;
    const w = {
      "sveltekit:history": k += g,
      "sveltekit:navigation": I += g,
      "sveltekit:states": i
    };
    (s ? history.replaceState : history.pushState).call(history, w, "", t);
    if (!s) {
      on(k, I);
    }
  }
  O = null;
  _.props.page.state = i;
  if (se) {
    const g = (await Promise.all(Array.from(sn, w => w(l.navigation)))).filter(w => typeof w == "function");
    if (g.length > 0) {
      let w = function () {
        g.forEach(b => {
          H.delete(b);
        });
      };
      g.push(w);
      g.forEach(b => {
        H.add(b);
      });
    }
    y = _.state;
    if (_.props.page) {
      _.props.page.url = t;
    }
    it.$set(_.props);
    Qt(_.props.page);
    st = true;
  } else {
    ft(_, ke, false);
  }
  const {
    activeElement: R
  } = document;
  await rn();
  const S = n ? n.scroll : a ? {
    x: pageXOffset,
    y: pageYOffset
  } : null;
  if (He) {
    const g = t.hash && document.getElementById(mt(t));
    if (S) {
      scrollTo(S.x, S.y);
    } else if (g) {
      g.scrollIntoView();
    } else {
      scrollTo(0, 0);
    }
  }
  const L = document.activeElement !== R && document.activeElement !== document.body;
  if (!r && !L) {
    wn(t);
  }
  He = true;
  if (_.props.page) {
    Object.assign(E, _.props.page);
  }
  X = false;
  if (e === "popstate") {
    lt(I);
  }
  l.fulfil(undefined);
  H.forEach(g => g(l.navigation));
  N.navigating.set(J.current = null);
}
async function pt(e, t, n, r) {
  return e.origin === Z && e.pathname === location.pathname && !xe ? await de({
    status: r,
    error: n,
    url: e,
    route: t
  }) : await q(e);
}
function pn() {
  let e;
  let t;
  let n;
  C.addEventListener("mousemove", o => {
    const c = o.target;
    clearTimeout(e);
    e = setTimeout(() => {
      s(c, 2);
    }, 20);
  });
  function r(o) {
    if (!o.defaultPrevented) {
      s(o.composedPath()[0], 1);
    }
  }
  C.addEventListener("mousedown", r);
  C.addEventListener("touchstart", r, {
    passive: true
  });
  const a = new IntersectionObserver(o => {
    for (const c of o) if (c.isIntersecting) {
      ye(new URL(c.target.href));
      a.unobserve(c.target);
    }
  }, {
    threshold: 0
  });
  async function s(o, c) {
    const f = tt(o, C);
    const d = f === t && c >= n;
    if (!f || d) {
      return;
    }
    const {
      url: h,
      external: u,
      download: l
    } = ve(f, U, v.hash);
    if (u || l) {
      return;
    }
    const p = te(f);
    const m = h && (v.hash ? y.url.hash.replace(/^#/, "") : y.url.pathname) + y.url.search === (v.hash ? h.hash.replace(/^#/, "") : h.pathname) + h.search;
    if (!(p.reload || m)) {
      if (c <= p.preload_data) {
        t = f;
        n = 1;
        const _ = await he(h, false);
        if (!_) {
          return;
        }
        ln(_);
      } else if (c <= p.preload_code) {
        t = f;
        n = c;
        ye(h);
      }
    }
  }
  function i() {
    a.disconnect();
    for (const o of C.querySelectorAll("a")) {
      const {
        url: c,
        external: f,
        download: d
      } = ve(o, U, v.hash);
      if (f || d) {
        continue;
      }
      const h = te(o);
      if (!h.reload) {
        if (h.preload_code === 3) {
          a.observe(o);
        }
        if (h.preload_code === 4) {
          ye(c);
        }
      }
    }
  }
  H.add(i);
  i();
}
function V(e, t) {
  if (e instanceof le) {
    return e.body;
  }
  const n = e instanceof le || e instanceof Re ? e.status : 500;
  const r = e instanceof Re ? e.text : "Internal Error";
  return v.hooks.handleError({
    error: e,
    event: t,
    status: n,
    message: r
  }) ?? {
    message: r
  };
}
function In(e, t = {}) {
  e = new URL(Ue(e));
  return e.origin !== Z ? Promise.reject(new Error("goto: invalid URL")) : Ce(e, t, 0);
}
function gn(e) {
  if (typeof e == "function") {
    ae.push(e);
  } else {
    const {
      href: t
    } = new URL(e, location.href);
    ae.push(n => n.href === t);
  }
}
function _n() {
  history.scrollRestoration = "manual";
  addEventListener("beforeunload", t => {
    let n = false;
    We();
    if (!X) {
      const r = je(y, undefined, null, "leave");
      const a = {
        ...r.navigation,
        cancel: () => {
          n = true;
          r.reject(new Error("navigation cancelled"));
        }
      };
      ot.forEach(s => s(a));
    }
    if (n) {
      t.preventDefault();
      t.returnValue = "";
    } else {
      history.scrollRestoration = "auto";
    }
  });
  addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      We();
    }
  });
  if (!navigator.connection?.saveData) {
    pn();
  }
  C.addEventListener("click", async t => {
    if (t.button || t.which !== 1 || t.metaKey || t.ctrlKey || t.shiftKey || t.altKey || t.defaultPrevented) {
      return;
    }
    const n = tt(t.composedPath()[0], C);
    if (!n) {
      return;
    }
    const {
      url: r,
      external: a,
      target: s,
      download: i
    } = ve(n, U, v.hash);
    if (!r) {
      return;
    }
    if (s === "_parent" || s === "_top") {
      if (window.parent !== window) {
        return;
      }
    } else if (s && s !== "_self") {
      return;
    }
    const o = te(n);
    if (!(n instanceof SVGAElement) && r.protocol !== location.protocol && !(r.protocol === "https:" || r.protocol === "http:") || i) {
      return;
    }
    const [f, d] = (v.hash ? r.hash.replace(/^#/, "") : r.href).split("#");
    const h = f === _e(location);
    if (a || o.reload && (!h || !d)) {
      if (ht({
        url: r,
        type: "link"
      })) {
        X = true;
      } else {
        t.preventDefault();
      }
      return;
    }
    if (d !== undefined && h) {
      const [, u] = y.url.href.split("#");
      if (u === d) {
        t.preventDefault();
        if (d === "" || d === "top" && n.ownerDocument.getElementById("top") === null) {
          window.scrollTo({
            top: 0
          });
        } else {
          const l = n.ownerDocument.getElementById(decodeURIComponent(d));
          if (l) {
            l.scrollIntoView();
            l.focus();
          }
        }
        return;
      }
      M = true;
      Le(k);
      e(r);
      if (!o.replace_state) {
        return;
      }
      M = false;
    }
    t.preventDefault();
    await new Promise(u => {
      requestAnimationFrame(() => {
        setTimeout(u, 0);
      });
      setTimeout(u, 100);
    });
    await W({
      type: "link",
      url: r,
      keepfocus: o.keepfocus,
      noscroll: o.noscroll,
      replace_state: o.replace_state ?? r.href === location.href
    });
  });
  C.addEventListener("submit", t => {
    if (t.defaultPrevented) {
      return;
    }
    const n = HTMLFormElement.prototype.cloneNode.call(t.target);
    const r = t.submitter;
    if ((r?.formTarget || n.target) === "_blank" || (r?.formMethod || n.method) !== "get") {
      return;
    }
    const i = new URL(r?.hasAttribute("formaction") && r?.formAction || n.action);
    if (!!(i.origin !== Z || !i.pathname.startsWith(U))) {
      return;
    }
    const o = t.target;
    const c = te(o);
    if (c.reload) {
      return;
    }
    t.preventDefault();
    t.stopPropagation();
    const f = new FormData(o);
    const d = r?.getAttribute("name");
    if (d) {
      f.append(d, r?.getAttribute("value") ?? "");
    }
    i.search = new URLSearchParams(f).toString();
    W({
      type: "form",
      url: i,
      keepfocus: c.keepfocus,
      noscroll: c.noscroll,
      replace_state: c.replace_state ?? i.href === location.href
    });
  });
  addEventListener("popstate", async t => {
    if (!Ae) {
      if (t.state?.["sveltekit:history"]) {
        const n = t.state["sveltekit:history"];
        $ = {};
        if (n === k) {
          return;
        }
        const r = D[n];
        const a = t.state["sveltekit:states"] ?? {};
        const s = new URL(t.state["sveltekit:pageurl"] ?? location.href);
        const i = t.state["sveltekit:navigation"];
        const o = y.url ? _e(location) === _e(y.url) : false;
        if (i === I && (st || o)) {
          if (a !== E.state) {
            E.state = a;
          }
          e(s);
          D[k] = {
            x: pageXOffset,
            y: pageYOffset
          };
          if (r) {
            scrollTo(r.x, r.y);
          }
          k = n;
          return;
        }
        const f = n - k;
        await W({
          type: "popstate",
          url: s,
          popped: {
            state: a,
            scroll: r,
            delta: f
          },
          accept: () => {
            k = n;
            I = i;
          },
          block: () => {
            history.go(-f);
          },
          nav_token: $
        });
      } else if (!M) {
        const n = new URL(location.href);
        e(n);
        if (v.hash) {
          location.reload();
        }
      }
    }
  });
  addEventListener("hashchange", () => {
    if (M) {
      M = false;
      history.replaceState({
        ...history.state,
        "sveltekit:history": ++k,
        "sveltekit:navigation": I
      }, "", location.href);
    }
  });
  for (const t of document.querySelectorAll("link")) if (an.has(t.rel)) {
    t.href = t.href;
  }
  addEventListener("pageshow", t => {
    if (t.persisted) {
      N.navigating.set(J.current = null);
    }
  });
  function e(t) {
    y.url = E.url = t;
    N.page.set({
      data: E.data,
      error: E.error,
      form: E.form,
      params: E.params,
      route: E.route,
      state: E.state,
      status: E.status,
      url: E.url
    });
    N.page.notify();
  }
}
async function mn(e, {
  status: t = 200,
  error: n,
  node_ids: r,
  params: a,
  route: s,
  server_route: i,
  data: o,
  form: c
}) {
  xe = true;
  const f = new URL(location.href);
  let d;
  ({
    params: a = {},
    route: s = {
      id: null
    }
  } = (await he(f, false)) || {});
  d = Te.find(({
    id: l
  }) => l === s.id);
  let h;
  let u = true;
  try {
    const l = r.map(async (m, _) => {
      const R = o[_];
      if (R?.uses) {
        R.uses = {
          dependencies: new Set(R.uses?.dependencies ?? []),
          params: new Set(R.uses?.params ?? []),
          parent: !!R.uses?.parent,
          route: !!R.uses?.route,
          url: !!R.uses?.url,
          search_params: new Set(R.uses?.search_params ?? [])
        };
      }
      return Oe({
        loader: v.nodes[m],
        url: f,
        params: a,
        route: s,
        parent: async () => {
          const S = {};
          for (let L = 0; L < _; L += 1) {
            Object.assign(S, (await l[L]).data);
          }
          return S;
        },
        server_data_node: R?.type === "data" ? R : R?.type === "skip" ? undefined ?? null : null
      });
    });
    const p = await Promise.all(l);
    if (d) {
      const m = d.layouts;
      for (let _ = 0; _ < m.length; _++) {
        if (!m[_]) {
          p.splice(_, 0, undefined);
        }
      }
    }
    h = ie({
      url: f,
      params: a,
      branch: p,
      status: t,
      error: n,
      form: c,
      route: d ?? null
    });
  } catch (l) {
    if (l instanceof Se) {
      await q(new URL(l.location, location.href));
      return;
    }
    h = await de({
      status: l instanceof le || l instanceof Re ? l.status : 500,
      error: await V(l, {
        url: f,
        params: a,
        route: s
      }),
      url: f,
      route: s
    });
    e.textContent = "";
    u = false;
  }
  if (h.props.page) {
    h.props.page.state = {};
  }
  ft(h, e, u);
}
async function gt(e, t) {
  const n = new URL(e);
  n.pathname = e.pathname.endsWith(".html") ? e.pathname.replace(/\.html$/, ".html__data.json") : e.pathname.replace(/\/$/, "") + "/__data.json";
  if (e.pathname.endsWith("/")) {
    n.searchParams.append("x-sveltekit-trailing-slash", "1");
  }
  n.searchParams.append("x-sveltekit-invalidated", t.map(s => s ? "1" : "0").join(""));
  const r = window.fetch;
  const a = await r(n.href, {});
  if (!a.ok) {
    let s;
    if (a.headers.get("content-type")?.includes("application/json")) {
      s = await a.json();
    } else if (a.status === 404) {
      s = "Not Found";
    } else if (a.status === 500) {
      s = "Internal Error";
    }
    throw new le(a.status, s);
  }
  return new Promise(async s => {
    const i = new Map();
    const o = a.body.getReader();
    const c = new TextDecoder();
    function f(h) {
      return Kt(h, {
        ...v.decoders,
        Promise: u => new Promise((l, p) => {
          i.set(u, {
            fulfil: l,
            reject: p
          });
        })
      });
    }
    let d = "";
    for (;;) {
      const {
        done: h,
        value: u
      } = await o.read();
      if (h && !d) {
        break;
      }
      for (d += !u && d ? `
` : c.decode(u, {
        stream: true
      });;) {
        const l = d.indexOf(`
`);
        if (l === -1) {
          break;
        }
        const p = JSON.parse(d.slice(0, l));
        d = d.slice(l + 1);
        if (p.type === "redirect") {
          return s(p);
        }
        if (p.type === "data") {
          p.nodes?.forEach(m => {
            if (m?.type === "data") {
              m.uses = {
                dependencies: new Set(m.uses?.dependencies ?? []),
                params: new Set(m.uses?.params ?? []),
                parent: !!m.uses?.parent,
                route: !!m.uses?.route,
                url: !!m.uses?.url,
                search_params: new Set(m.uses?.search_params ?? [])
              };
              m.data = f(m.data);
            }
          });
          s(p);
        } else if (p.type === "chunk") {
          const {
            id: m,
            data: _,
            error: R
          } = p;
          const S = i.get(m);
          i.delete(m);
          if (R) {
            S.reject(f(R));
          } else {
            S.fulfil(f(_));
          }
        }
      }
    }
  });
}
function _t(e) {
  return {
    dependencies: new Set(e?.dependencies ?? []),
    params: new Set(e?.params ?? []),
    parent: !!e?.parent,
    route: !!e?.route,
    url: !!e?.url,
    search_params: new Set(e?.search_params ?? [])
  };
}
let Ae = false;
function wn(e) {
  const t = document.querySelector("[autofocus]");
  if (t) {
    t.focus();
  } else {
    const n = mt(e);
    if (n && document.getElementById(n)) {
      const {
        x: a,
        y: s
      } = {
        x: pageXOffset,
        y: pageYOffset
      };
      setTimeout(() => {
        const i = history.state;
        Ae = true;
        location.replace(`#${n}`);
        if (v.hash) {
          location.replace(e.hash);
        }
        history.replaceState(i, "", e.hash);
        scrollTo(a, s);
        Ae = false;
      });
    } else {
      const a = document.body;
      const s = a.getAttribute("tabindex");
      a.tabIndex = -1;
      a.focus({
        preventScroll: true,
        focusVisible: false
      });
      if (s !== null) {
        a.setAttribute("tabindex", s);
      } else {
        a.removeAttribute("tabindex");
      }
    }
    const r = getSelection();
    if (r && r.type !== "None") {
      const a = [];
      for (let s = 0; s < r.rangeCount; s += 1) {
        a.push(r.getRangeAt(s));
      }
      setTimeout(() => {
        if (r.rangeCount === a.length) {
          for (let s = 0; s < r.rangeCount; s += 1) {
            const i = a[s];
            const o = r.getRangeAt(s);
            if (i.commonAncestorContainer !== o.commonAncestorContainer || i.startContainer !== o.startContainer || i.endContainer !== o.endContainer || i.startOffset !== o.startOffset || i.endOffset !== o.endOffset) {
              return;
            }
          }
          r.removeAllRanges();
        }
      });
    }
  }
}
function je(e, t, n, r) {
  let a;
  let s;
  const i = new Promise((c, f) => {
    a = c;
    s = f;
  });
  i.catch(() => {});
  return {
    navigation: {
      from: {
        params: e.params,
        route: {
          id: e.route?.id ?? null
        },
        url: e.url
      },
      to: n && {
        params: t?.params ?? null,
        route: {
          id: t?.route?.id ?? null
        },
        url: n
      },
      willUnload: !t,
      type: r,
      complete: i
    },
    fulfil: a,
    reject: s
  };
}
function $e(e) {
  return {
    data: e.data,
    error: e.error,
    form: e.form,
    params: e.params,
    route: e.route,
    state: e.state,
    status: e.status,
    url: e.url
  };
}
function yn(e) {
  const t = new URL(e);
  t.hash = decodeURIComponent(e.hash);
  return t;
}
function mt(e) {
  let t;
  if (v.hash) {
    const [,, n] = e.hash.split("#", 3);
    t = n ?? "";
  } else {
    t = e.hash.slice(1);
  }
  return decodeURIComponent(t);
}
export { Rn as a, In as g, kn as l, E as p, N as s };