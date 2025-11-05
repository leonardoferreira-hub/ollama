from jinja2 import Template
from typing import Dict

TEMPLATE = Template("""
<!doctype html>
<html><head><meta charset="utf-8"><title>Relatório de Validação</title>
<style>
body { font-family: Arial, sans-serif; padding: 16px; }
table { border-collapse: collapse; width: 100%; margin-top: 12px; }
th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
th { background: #f4f4f4; }
.status-conforme { color: #0a7f00; font-weight: bold; }
.status-divergente { color: #b00020; font-weight: bold; }
.status-ambigua { color: #b26a00; font-weight: bold; }
.status-ausente { color: #666; font-weight: bold; }
pre { white-space: pre-wrap; }
</style></head><body>
<h1>Relatório de Validação</h1>
<p><b>Standard:</b> {{ standard_version }} | <b>PDF SHA256:</b> {{ pdf_sha256 }}</p>
<table>
  <thead><tr><th>Cláusula</th><th>Status</th><th>Evidência</th><th>Parâmetros</th><th>Notas</th></tr></thead>
  <tbody>
  {% for r in results %}
    <tr>
      <td>{{ r.clause_id }}</td>
      <td class="status-{{ r.status }}">{{ r.status }}</td>
      <td>
        {% if r.evidence %}
          <div><b>Pág.:</b> {{ r.evidence.page }}</div>
          <pre>{{ r.evidence.text }}</pre>
        {% else %}-{% endif %}
      </td>
      <td><pre>{{ r.parameters | tojson(indent=2) }}</pre></td>
      <td>{{ r.notes or "-" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>
</body></html>
""")

def render_html(payload: Dict) -> str:
    """
    Renderiza relatório HTML a partir dos resultados da validação.

    Args:
        payload: Dicionário com standard_version, pdf_sha256 e results

    Returns:
        String HTML renderizada
    """
    return TEMPLATE.render(**payload)
