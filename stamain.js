async function enviarDenuncia() {
  const tipo      = document.getElementById("tipo").value;
  const local     = document.getElementById("local").value;
  const descricao = document.getElementById("descricao").value.trim();
  const btn       = document.getElementById("btn-enviar");

  if (!tipo)      { alert("Selecione o tipo de violação."); return; }
  if (!descricao) { alert("Descreva o que você viu."); return; }

  btn.disabled = true;
  btn.textContent = "Enviando...";

  try {
    const res = await fetch("/api/denuncia", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tipo, local, descricao }),
    });
    const data = await res.json();
    if (res.ok) {
      document.getElementById("form-area").classList.add("hidden");
      document.getElementById("form-sucesso").classList.remove("hidden");
      document.getElementById("form-sucesso").scrollIntoView({ behavior: "smooth" });
    } else {
      alert(data.erro || "Erro ao enviar. Tente novamente.");
      btn.disabled = false;
      btn.textContent = "Enviar denúncia";
    }
  } catch (err) {
    alert("Sem conexão. Verifique sua internet.");
    btn.disabled = false;
    btn.textContent = "Enviar denúncia";
  }
}

function novaDenuncia() {
  document.getElementById("tipo").value      = "";
  document.getElementById("local").value     = "";
  document.getElementById("descricao").value = "";
  document.getElementById("form-area").classList.remove("hidden");
  document.getElementById("form-sucesso").classList.add("hidden");
  document.getElementById("denuncia").scrollIntoView({ behavior: "smooth" });
}

document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener("click", e => {
    const target = document.querySelector(a.getAttribute("href"));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: "smooth" }); }
  });
});
