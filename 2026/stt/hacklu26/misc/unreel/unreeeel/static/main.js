'use strict';

const ICONS = {
  play: 'M8 5v14l11-7z',
  pause: 'M6 19h4V5H6v14zm8-14v14h4V5h-4z',
  up: 'M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z',
  down: 'M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z',
  like: 'M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z',
  dislike: 'M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z',
  comment: 'M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18z',
  share: 'M14 9V5l7 7-7 7v-4.1c-5 0-8.5 1.6-11 5.1 1-5 4-10 11-11z',
  sound: 'M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z',
  muted: 'M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z',
};

const feed = document.getElementById('feed');
const template = document.getElementById('short-template');
const prevButton = document.getElementById('prev');
const nextButton = document.getElementById('next');

let muted = false;
// set once the user uses the mute button, sound then never turns on by itself
let muteChosen = false;
// the tap that turned the sound on shouldn't also pause the video
let swallowVideoClick = false;
let active = null;

const GLOW_INTERVAL_MS = 100;
let lastGlow = 0;

// shorts kept ready after the active one
const QUEUE_AHEAD = 2;
// how many of the last shorts /api/next should avoid repeating
const RECENT = 5;
let filling = null;

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) activate(entry.target);
  });
}, { root: feed, threshold: 0.6 });

function setIcon(el, name) {
  el.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${ICONS[name]}"/></svg>`;
}

function fillIcons(root) {
  root.querySelectorAll('[data-icon]').forEach((el) => setIcon(el, el.dataset.icon));
}

function avatarColor(name) {
  let hash = 0;
  for (const c of name) hash = (hash * 31 + c.codePointAt(0)) | 0;
  return `hsl(${Math.abs(hash) % 360} 55% 40%)`;
}

function flash(short, iconName) {
  const el = short.querySelector('.flash');
  setIcon(el, iconName);
  el.classList.remove('show');
  // restart the animation
  void el.offsetWidth;
  el.classList.add('show');
}

// Browsers refuse sound before the first user gesture, play muted until then
function play(video) {
  video.play().catch((e) => {
    if (e.name !== 'NotAllowedError' || video.muted) return;
    setMuted(true);
    video.play().catch(() => {});
  });
}

function unmuteOnGesture(e) {
  if (muteChosen || !muted) return;
  // the mute button and the m key make their own choice
  if (e.target.closest?.('.mute-toggle') || e.key === 'm') return;
  setMuted(false);
  if (e.target.tagName === 'VIDEO') swallowVideoClick = true;
}

function togglePlay(short) {
  const video = short.querySelector('video');
  if (video.paused) {
    play(video);
    flash(short, 'play');
  } else {
    video.pause();
    flash(short, 'pause');
  }
}

function setMuted(value) {
  muted = value;
  feed.querySelectorAll('.short').forEach((short) => {
    short.querySelector('video').muted = muted;
    setIcon(short.querySelector('.mute-toggle'), muted ? 'muted' : 'sound');
  });
}

// An initial on a colored circle, replaced by the picture once it loads
function fillAvatar(avatar, userId, name) {
  avatar.textContent = name.charAt(0).toUpperCase();
  avatar.style.background = avatarColor(name);
  const pfp = new Image();
  pfp.alt = '';
  pfp.addEventListener('load', () => avatar.append(pfp));
  pfp.src = `/pfp/${encodeURIComponent(userId)}.jpg`;
}

function buildShort(video) {
  const short = template.content.firstElementChild.cloneNode(true);
  short.dataset.id = video.id;
  fillIcons(short);

  const player = short.querySelector('video');
  player.src = `/shorts/${encodeURIComponent(video.id)}.mp4`;
  player.muted = muted;
  setIcon(short.querySelector('.mute-toggle'), muted ? 'muted' : 'sound');

  fillAvatar(short.querySelector('.avatar'), video.uploader_id, video.uploader);
  short.querySelector('.name').textContent = `@${video.uploader}`;
  short.querySelector('.key').textContent = `REEL-${video.id}`;
  short.querySelector('.description').textContent = video.description;

  const playToggle = short.querySelector('.play-toggle');
  const bar = short.querySelector('.progress div');
  player.addEventListener('click', () => {
    if (swallowVideoClick) {
      swallowVideoClick = false;
      return;
    }
    togglePlay(short);
  });
  player.addEventListener('play', () => setIcon(playToggle, 'pause'));
  player.addEventListener('pause', () => setIcon(playToggle, 'play'));
  // a first frame for the glow, even before playback starts
  player.addEventListener('loadeddata', () => drawGlow(short));
  player.addEventListener('timeupdate', () => {
    if (player.duration) bar.style.width = `${(player.currentTime / player.duration) * 100}%`;
  });
  playToggle.addEventListener('click', () => togglePlay(short));
  short.querySelector('.mute-toggle').addEventListener('click', () => {
    muteChosen = true;
    setMuted(!muted);
  });

  const subscribe = short.querySelector('.subscribe');
  subscribe.addEventListener('click', () => {
    const on = subscribe.classList.toggle('on');
    subscribe.textContent = on ? 'Subscribed' : 'Subscribe';
  });

  const like = short.querySelector('.like');
  const dislike = short.querySelector('.dislike');
  like.addEventListener('click', () => {
    if (like.classList.toggle('on')) dislike.classList.remove('on');
  });
  dislike.addEventListener('click', () => {
    if (dislike.classList.toggle('on')) like.classList.remove('on');
  });

  const shareLabel = short.querySelector('.share-label');
  short.querySelector('.share').addEventListener('click', async () => {
    const url = `${location.origin}/#${video.id}`;
    try {
      await navigator.clipboard.writeText(url);
      shareLabel.textContent = 'Copied';
    } catch {
      shareLabel.textContent = 'Failed';
    }
    setTimeout(() => { shareLabel.textContent = 'Share'; }, 1500);
  });

  return short;
}

function drawGlow(short) {
  const video = short.querySelector('video');
  if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) return;
  const canvas = short.querySelector('.glow');
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
}

function glowLoop(now) {
  if (active && now - lastGlow >= GLOW_INTERVAL_MS) {
    drawGlow(active);
    lastGlow = now;
  }
  requestAnimationFrame(glowLoop);
}

function activate(short) {
  if (short === active) return;
  if (active) {
    active.querySelector('video').pause();
    active.classList.remove('active');
  }
  active = short;
  short.classList.add('active');

  const video = short.querySelector('video');
  video.currentTime = 0;
  play(video);
  history.replaceState(null, '', `#${short.dataset.id}`);

  const next = short.nextElementSibling;
  if (next) next.querySelector('video').preload = 'auto';
  updateNav();
  fillQueue().catch(() => {});
}

function updateNav() {
  prevButton.disabled = !active?.previousElementSibling;
  nextButton.disabled = !active?.nextElementSibling;
}

// Returns null for a 404
async function fetchVideo(url) {
  const res = await fetch(url);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

function appendShort(video) {
  const short = buildShort(video);
  feed.append(short);
  observer.observe(short);
  if (active && short.previousElementSibling === active) short.querySelector('video').preload = 'auto';
  updateNav();
}

// Appends random shorts until QUEUE_AHEAD are waiting after the active one
function fillQueue() {
  filling ??= (async () => {
    try {
      while (true) {
        const shorts = [...feed.querySelectorAll('.short')];
        if (shorts.length - 1 - shorts.indexOf(active) >= QUEUE_AHEAD) break;
        const recent = shorts.slice(-RECENT).map((s) => s.dataset.id);
        const video = await fetchVideo(`/api/next?exclude=${recent.join(',')}`);
        if (!video) break;
        appendShort(video);
      }
    } finally {
      filling = null;
    }
  })();
  return filling;
}

function step(direction) {
  const target = direction > 0 ? active?.nextElementSibling : active?.previousElementSibling;
  target?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showMessage(text) {
  feed.innerHTML = '';
  const el = document.createElement('div');
  el.className = 'empty';
  el.textContent = text;
  feed.append(el);
  prevButton.disabled = true;
  nextButton.disabled = true;
}

async function load() {
  try {
    // a shared link starts with that short, the rest is random
    const linked = location.hash.slice(1);
    if (/^\d+$/.test(linked)) {
      const video = await fetchVideo(`/api/videos/${linked}`);
      if (video) appendShort(video);
    }
    await fillQueue();
  } catch {
    if (!feed.querySelector('.short')) showMessage('Could not load reels.');
    return;
  }
  if (!feed.querySelector('.short')) {
    showMessage('No reels yet.');
    return;
  }
  feed.focus();
}

function accountButton(tag, className, text) {
  const el = document.createElement(tag);
  el.className = `button ${className}`;
  el.textContent = text;
  return el;
}

// Log in and register links, or who is logged in
async function showAccount() {
  const box = document.getElementById('account');
  const user = await account.me().catch(() => null);
  box.innerHTML = '';
  if (!user) {
    box.innerHTML = '<a class="button subtle" href="/login">Log in</a>'
      + '<a class="button primary" href="/register">Register</a>';
    return;
  }
  if (user.role === 'senior') {
    const admin = accountButton('a', 'subtle', 'Admin');
    admin.href = '/admin/';
    box.append(admin);
  }
  // a popup, the link still works if it's blocked
  const password = accountButton('a', 'subtle', 'Change password');
  password.href = '/password/';
  password.addEventListener('click', (e) => {
    if (window.open('/password/', 'password', 'popup,width=420,height=480')) e.preventDefault();
  });
  const logout = accountButton('button', 'subtle', 'Log out');
  logout.addEventListener('click', async () => {
    await account.logout();
    showAccount();
  });
  const name = document.createElement('span');
  name.className = 'name';
  name.textContent = `@${user.name}`;
  const avatar = document.createElement('span');
  avatar.className = 'avatar';
  fillAvatar(avatar, user.id, user.name);
  box.append(password, logout, name, avatar);
}

fillIcons(document);
showAccount();
requestAnimationFrame(glowLoop);
prevButton.addEventListener('click', () => step(-1));
nextButton.addEventListener('click', () => step(1));

document.addEventListener('pointerdown', unmuteOnGesture, { capture: true });
document.addEventListener('keydown', unmuteOnGesture, { capture: true });
document.addEventListener('keydown', (e) => {
  if (e.target.closest('input, textarea')) return;
  if (e.key === 'ArrowDown' || e.key === 'j') step(1);
  else if (e.key === 'ArrowUp' || e.key === 'k') step(-1);
  else if (e.key === ' ' && active) togglePlay(active);
  else if (e.key === 'm') {
    muteChosen = true;
    setMuted(!muted);
  }
  else return;
  e.preventDefault();
});

load();
