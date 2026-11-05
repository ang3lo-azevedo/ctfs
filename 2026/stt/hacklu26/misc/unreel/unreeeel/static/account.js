'use strict';

// Login sets an HttpOnly token cookie the browser sends on every request,
// so nothing here handles the token itself.
const account = (() => {
  // Throws the server's error message for anything but a 2xx, with the
  // status as err.status
  async function post(url, fields) {
    const res = await fetch(url, { method: 'POST', body: new URLSearchParams(fields) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.error || res.statusText);
      err.status = res.status;
      throw err;
    }
    return data;
  }

  async function login(name, password) {
    await post('/api/login', { name, password });
  }

  async function logout() {
    try {
      await post('/api/logout', {});
    } catch {}
  }

  // The logged in user, or null
  async function me() {
    const res = await fetch('/api/me');
    return res.ok ? res.json() : null;
  }

  // Runs submit(fields) on submit, showing what it throws in the form's .error
  function bindForm(form, submit) {
    const error = form.querySelector('.error');
    const button = form.querySelector('button[type=submit]');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      error.textContent = '';
      button.disabled = true;
      try {
        await submit(Object.fromEntries(new FormData(form)));
      } catch (err) {
        error.textContent = err.message;
      } finally {
        button.disabled = false;
      }
    });
  }

  return { post, login, logout, me, bindForm };
})();
