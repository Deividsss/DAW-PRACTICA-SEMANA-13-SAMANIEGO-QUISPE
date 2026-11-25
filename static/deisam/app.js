const $ = (id) => document.getElementById(id);
const state = { page: 1, next: null, prev: null };
const cats = {};

const csrf = () => (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || "";
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function cargarCategorias() {
  const r = await fetch("/api/categorias/?limit=50");
  const data = await r.json();
  data.results.forEach((c, i) => (cats[c.id] = { nombre: c.nombre, color: i % 5 }));
  const opts = data.results.map((c) => `<option value="${c.id}">${esc(c.nombre)}</option>`).join("");
  $("categoria").innerHTML = `<option value="">Todas</option>` + opts;
  $("catNuevo").innerHTML = opts;
}

async function cargar() {
  const p = new URLSearchParams({ page: state.page, ordering: $("ordering").value });
  if ($("q").value.trim()) p.set("search", $("q").value.trim());
  if ($("categoria").value) p.set("categoria", $("categoria").value);
  if ($("soloActivos").checked) p.set("estado", "activo");

  const r = await fetch(`/api/productos/?${p}`);
  if (r.status === 429) { $("resumen").textContent = "Demasiadas solicitudes. Espera un momento e intenta otra vez."; return; }
  if (r.status === 404 && state.page > 1) { state.page = 1; return cargar(); }
  const data = await r.json();
  state.next = data.next; state.prev = data.previous;

  $("resumen").textContent = data.count ? `${data.count} productos encontrados` : "No hay productos con esos filtros. Prueba quitando alguno.";
  $("grid").innerHTML = data.results.map((x, i) => `
    <article class="card c${(cats[x.categoria] || {}).color ?? 0}" style="animation-delay:${i * 40}ms">
      <span class="cat">${esc(x.categoria_nombre)}</span>
      <h2>${esc(x.nombre)}</h2>
      <p>${esc(x.descripcion)}</p>
      <div class="pie"><span class="precio">S/ ${Number(x.precio).toFixed(2)}</span><span class="estado">${esc(x.disponibilidad)}</span></div>
    </article>`).join("");
  $("pagina").textContent = `Página ${state.page}`;
  $("prev").disabled = !state.prev; $("next").disabled = !state.next;
}

["q", "categoria", "ordering", "soloActivos"].forEach((id) =>
  $(id).addEventListener(id === "q" ? "input" : "change", () => { state.page = 1; cargar(); }));
$("filtros").addEventListener("submit", (e) => e.preventDefault());
$("prev").onclick = () => { state.page--; cargar(); scrollTo({ top: 0 }); };
$("next").onclick = () => { state.page++; cargar(); scrollTo({ top: 0 }); };

$("formNuevo").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = Object.fromEntries(new FormData(e.target));
  const r = await fetch("/api/productos/", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrf() },  // CSRF para AJAX/SPA
    body: JSON.stringify({ ...f, estado: "activo" }),
  });
  const body = await r.json().catch(() => ({}));
  const m = $("msgNuevo");
  if (r.ok) { m.textContent = "Producto guardado."; e.target.reset(); state.page = 1; cargar(); }
  else if (r.status === 403) m.textContent = "Inicia sesión para agregar productos.";
  else m.textContent = Object.values(body).flat().join(" ") || "No se pudo guardar.";
});

cargarCategorias().then(cargar);
