(() => {
  const $ = id => document.getElementById(id);
  const root = document.documentElement;
  const card = $('card');
  const form = $('form');
  const username = $('username');
  const pw = $('pw');
  const eye = $('eye');
  const pwField = $('pwField');
  const usernameField = $('usernameField');
  const helper = $('helper');
  const cta = $('cta');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Ambient parallax from the original design.
  let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  const tick = () => {
    cx += (tx - cx) * .06;
    cy += (ty - cy) * .06;
    root.style.setProperty('--mx', cx.toFixed(2));
    root.style.setProperty('--my', cy.toFixed(2));
    raf = (Math.abs(tx - cx) > .05 || Math.abs(ty - cy) > .05)
      ? requestAnimationFrame(tick)
      : 0;
  };

  if (!reduce) {
    addEventListener('pointermove', event => {
      tx = (event.clientX / innerWidth - .5) * 2;
      ty = (event.clientY / innerHeight - .5) * 2;
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
  }

  // Password reveal.
  eye.addEventListener('click', () => {
    const show = pw.type === 'password';
    pw.type = show ? 'text' : 'password';
    pwField.classList.toggle('revealed', show);
    eye.setAttribute('aria-pressed', show);
    eye.setAttribute('aria-label', show ? 'hide password' : 'show password');
    eye.classList.remove('blink');
    void eye.offsetWidth;
    eye.classList.add('blink');
    pw.focus({ preventScroll: true });
  });

  const say = (message, bad = false) => {
    helper.textContent = message || '';
    helper.classList.toggle('on', Boolean(message));
    helper.classList.toggle('bad', bad);
  };

  const clearError = () => {
    usernameField.classList.remove('err');
    pwField.classList.remove('err');
    say('');
  };

  const fail = (message, ...fields) => {
    say(message, true);
    fields.forEach(field => field.classList.add('err'));
    card.classList.remove('shake');
    void card.offsetWidth;
    card.classList.add('shake');
    (fields[0] === usernameField ? username : pw).focus({ preventScroll: true });
  };

  [username, pw].forEach(input => input.addEventListener('input', clearError));

  // Real FastAPI authentication. The backend sets the HttpOnly JWT cookie.
  form.addEventListener('submit', async event => {
    event.preventDefault();
    clearError();

    const user = username.value.trim();
    const password = pw.value;

    if (!user) return fail('enter your username.', usernameField);
    if (!password) return fail('enter your password.', pwField);

    cta.disabled = true;
    cta.classList.add('loading');

    try {
      const response = await fetch('/login', {
        method: 'POST',
        body: new FormData(form),
        credentials: 'same-origin',
        redirect: 'follow'
      });

      if (!response.ok) {
        if (response.status === 401) {
          pw.select();
          fail('invalid username or password.', usernameField, pwField);
        } else {
          fail('something went wrong. please try again.', usernameField, pwField);
        }
        return;
      }

      card.classList.add('done');
      root.style.setProperty('--glow', 'var(--em)');
      card.style.boxShadow = '0 0 0 1px rgba(61,220,151,.18),0 30px 60px -20px rgba(0,0,0,.7),0 0 70px -20px rgba(61,220,151,.5),inset 0 1px 0 rgba(255,255,255,.08)';
      card.style.transition = 'box-shadow .8s';

      setTimeout(() => {
        window.location.href = '/';
      }, 700);
    } catch (error) {
      fail('unable to reach the server. please try again.', usernameField, pwField);
    } finally {
      cta.disabled = false;
      cta.classList.remove('loading');
    }
  });
})();
