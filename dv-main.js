function rayar(el) {
  const texto = el.textContent.trim();
  el.textContent = '';
  const oculto = Object.assign(document.createElement('span'), { className: 'dv-vh', textContent: texto });
  const visible = document.createElement('span');
  visible.setAttribute('aria-hidden', 'true');
  for (const palabra of texto.split(/\s+/)) {
    const w = Object.assign(document.createElement('span'), { className: 'dv-w' });
    for (const c of palabra) {
      let clase = 'dv-l';
      if ('áéíóúüñÁÉÍÓÚÜÑ'.includes(c)) clase += ' dv-tilde';
      w.append(Object.assign(document.createElement('span'), { className: clase, textContent: c }));
    }
    visible.append(w);
  }
  el.append(oculto, visible);
}
document.querySelectorAll('[data-rayar]').forEach(rayar);

// light / dark button: sets data-modo and remembers it; otherwise follows the system
(function () {
  const root = document.documentElement;
  const boton = document.getElementById('modo');
  const sistema = matchMedia('(prefers-color-scheme: light)');
  const actual = () => root.dataset.modo || (sistema.matches ? 'claro' : 'oscuro');
  const pintar = () => {
    const claro = actual() === 'claro';
    boton.textContent = claro ? 'Dark' : 'Light';
    boton.setAttribute('aria-label', claro ? 'Switch to dark mode' : 'Switch to light mode');
  };
  boton.addEventListener('click', () => {
    root.dataset.modo = actual() === 'claro' ? 'oscuro' : 'claro';
    try { localStorage.setItem(root.dataset.clave, root.dataset.modo); } catch (e) {}
    pintar();
  });
  sistema.addEventListener('change', pintar);
  pintar();
})();

// showreel: the preview stays dimmed until the video plays
(function () {
  const reel = document.querySelector('.ml-reel');
  const boton = reel.querySelector('.ml-play');
  if (!window.Vimeo) { boton.hidden = true; return; }
  const player = new Vimeo.Player(reel.querySelector('iframe'));
  boton.addEventListener('click', () => player.play());
  player.on('play', () => reel.classList.add('playing'));
  player.on('pause', () => reel.classList.remove('playing'));
  player.on('ended', () => reel.classList.remove('playing'));
})();
