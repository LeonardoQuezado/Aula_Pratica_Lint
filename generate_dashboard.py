#!/usr/bin/env python3
"""Transforma o relatório XML do Android Lint em dashboard HTML customizado."""
import xml.etree.ElementTree as ET
import sys
import html as esc
from datetime import datetime

ACCESSIBILITY_IDS = {
    'ContentDescription', 'KeyboardInaccessibleWidget', 'LabelFor',
    'ClickableViewAccessibility', 'TouchTargetSizeAtf', 'ImageContrastAtf',
    'TextContrastAtf', 'SpeakableTextPresentAtf', 'DuplicateSpeakableItems',
    'ComposableNaming', 'SemanticsFocusable',
}

PT = {
    'ContentDescription': (
        'Imagem sem Descrição de Conteúdo',
        'Imagens e botões de imagem precisam do atributo <code>contentDescription</code> para que o '
        'TalkBack consiga descrever o elemento ao usuário com deficiência visual. Sem isso, o leitor '
        'de tela anuncia apenas "Imagem" ou "Botão sem rótulo".',
        'Adicione <code>android:contentDescription="@string/sua_descricao"</code> ao elemento. '
        'Para imagens puramente decorativas, use <code>android:contentDescription="@null"</code> '
        'e <code>android:importantForAccessibility="no"</code>.',
    ),
    'KeyboardInaccessibleWidget': (
        'Widget Inacessível por Teclado',
        'Elementos com <code>clickable="true"</code> devem também ter <code>focusable="true"</code>. '
        'Sem isso, usuários que navegam por teclado ou controle direcional (d-pad) não conseguem '
        'alcançar o elemento — tornando a funcionalidade completamente inacessível para eles.',
        'Adicione <code>android:focusable="true"</code> ao elemento que possui '
        '<code>android:clickable="true"</code>. Considere usar um <code>&lt;Button&gt;</code> '
        'nativo, que já inclui esses atributos por padrão.',
    ),
    'LabelFor': (
        'Campo sem Rótulo Associado',
        'Campos de texto devem ter um <code>TextView</code> associado via <code>android:labelFor</code>. '
        'Isso permite que o TalkBack informe ao usuário o propósito do campo antes de ele começar '
        'a digitar.',
        'Adicione <code>android:labelFor="@id/id_do_campo"</code> ao <code>TextView</code> que '
        'serve de rótulo para o campo de entrada.',
    ),
    'Autofill': (
        'Sugestão de Preenchimento Automático Ausente',
        'Campos de entrada devem declarar <code>android:autofillHints</code> para que o Android '
        'possa sugerir preenchimento automático, melhorando a usabilidade para todos os usuários.',
        'Adicione <code>android:autofillHints="name"</code>, <code>"emailAddress"</code>, '
        '<code>"password"</code> etc. ao <code>EditText</code>.',
    ),
    'UnusedResources': (
        'Recursos Não Utilizados',
        'Recursos declarados (cores, strings, drawables) que não são referenciados em nenhum lugar '
        'do projeto aumentam o tamanho do APK desnecessariamente.',
        'Remova os recursos não utilizados do arquivo correspondente em <code>res/values/</code>.',
    ),
    'UnusedIds': (
        'IDs Não Utilizados',
        'IDs de elementos de layout que não são referenciados no código Java/Kotlin. '
        'Geram overhead desnecessário no arquivo <code>R</code>.',
        'Remova <code>android:id</code> dos elementos que não precisam ser acessados '
        'programaticamente.',
    ),
    'MissingApplicationIcon': (
        'Ícone do Aplicativo Ausente',
        'O manifesto não declara um ícone de aplicativo. Isso causa exibição incorreta na tela '
        'inicial e pode ser rejeitado na Play Store.',
        'Adicione <code>android:icon="@mipmap/ic_launcher"</code> na tag '
        '<code>&lt;application&gt;</code> do manifesto.',
    ),
    'RtlEnabled': (
        'Suporte a RTL Não Configurado',
        'O projeto usa atributos direcionais (como <code>layout_gravity="end"</code>) mas não '
        'declara suporte a idiomas da direita para esquerda (árabe, hebraico) no manifesto.',
        'Adicione <code>android:supportsRtl="true"</code> na tag <code>&lt;application&gt;</code> '
        'do manifesto.',
    ),
    'UnknownNullness': (
        'Nulidade Não Declarada',
        'Métodos Java sem anotações <code>@Nullable</code> ou <code>@NonNull</code> dificultam a '
        'interoperabilidade com Kotlin e podem causar <code>NullPointerException</code> em '
        'tempo de execução.',
        'Adicione <code>@NonNull</code> ou <code>@Nullable</code> ao parâmetro ou retorno '
        'do método.',
    ),
    'ClickableViewAccessibility': (
        'Elemento Clicável sem Acessibilidade',
        'Elementos com <code>Modifier.clickable</code> devem declarar uma ação semântica '
        'para que leitores de tela consigam anunciar e ativar o elemento corretamente.',
        'Adicione <code>Modifier.semantics { role = Role.Button; onClick(label = "descrição") { true } }</code> '
        'ao elemento clicável.',
    ),
    'Overdraw': (
        'Sobreposição de Pintura (Overdraw)',
        'O elemento define uma cor de fundo que já é pintada pelo tema pai, fazendo o sistema '
        'renderizar a mesma região duas vezes — impacta performance em dispositivos mais lentos.',
        'Remova o <code>android:background</code> redundante ou use '
        '<code>android:background="@null"</code> para herdar do tema.',
    ),
}


def get_pt(issue_id):
    return PT.get(issue_id, (
        issue_id,
        'Consulte a documentação do Android Lint para mais detalhes sobre esta regra.',
        'Verifique as sugestões de correção no relatório original do Lint.',
    ))


def short_path(path):
    for marker in ('src/main/', 'src\\main\\'):
        if marker in path:
            return path[path.index(marker):]
    sep = '/' if '/' in path else '\\'
    return path.split(sep)[-1]


def severity_badge(severity):
    cfg = {
        'Error':   ('#ff4444', '#2a0808'),
        'Warning': ('#e3b341', '#2a1e00'),
        'Fatal':   ('#ff0000', '#1a0000'),
        'Information': ('#58a6ff', '#081a2a'),
    }
    color, bg = cfg.get(severity, ('#aaa', '#1a1a1a'))
    labels = {'Error': 'Erro', 'Warning': 'Aviso', 'Fatal': 'Fatal', 'Information': 'Info'}
    label = labels.get(severity, severity)
    return (f'<span class="badge" style="color:{color};background:{bg};'
            f'border:1px solid {color}40;">{label}</span>')


def category_pt(cat):
    return {
        'Accessibility': 'Acessibilidade',
        'Performance': 'Performance',
        'Usability': 'Usabilidade',
        'Usability:Icons': 'Usabilidade · Ícones',
        'Internationalization': 'Internacionalização',
        'Internationalization:Bidirectional Text': 'Internacionalização · RTL',
        'Interoperability:Kotlin Interoperability': 'Interoperabilidade · Kotlin',
        'Correctness': 'Corretude',
        'Security': 'Segurança',
    }.get(cat, cat)


def issue_card(issue, is_a11y=False):
    name, explanation, fix = get_pt(issue['id'])

    loc_html = ''
    if issue['locations']:
        loc = issue['locations'][0]
        path = esc.escape(short_path(loc['file']))
        line = f":{loc['line']}" if loc['line'] else ''
        loc_html = f'<div class="location">📄 {path}{line}</div>'

    code_html = ''
    if issue['errorLine1']:
        line1 = esc.escape(issue['errorLine1'])
        line2 = esc.escape(issue['errorLine2']) if issue['errorLine2'] else ''
        code_html = f'<pre class="snippet">{line1}{chr(10) + line2 if line2 else ""}</pre>'

    accent = '#ff7b72' if is_a11y else '#e3b341'
    extra_class = 'a11y-card' if is_a11y else ''

    return f'''
<div class="card {extra_class}" style="border-left-color:{accent}">
  <div class="card-header">
    <div class="card-title">
      <span class="issue-name">{esc.escape(name)}</span>
      <span class="issue-id">{esc.escape(issue["id"])}</span>
    </div>
    <div class="card-meta">
      {severity_badge(issue["severity"])}
      <span class="cat-tag">{esc.escape(category_pt(issue["category"]))}</span>
    </div>
  </div>
  {loc_html}
  {code_html}
  <div class="explain">
    <div class="block-title">O que é este problema?</div>
    <p>{explanation}</p>
  </div>
  <div class="fixbox">
    <div class="block-title fix-title">✔ Como corrigir</div>
    <p>{fix}</p>
  </div>
</div>'''


def generate(xml_path, out_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    issues = []
    for node in root.findall('issue'):
        locs = [{'file': l.get('file', ''), 'line': l.get('line', ''), 'column': l.get('column', '')}
                for l in node.findall('location')]
        issues.append({
            'id':         node.get('id', ''),
            'severity':   node.get('severity', 'Warning'),
            'message':    node.get('message', ''),
            'category':   node.get('category', ''),
            'summary':    node.get('summary', ''),
            'explanation': node.get('explanation', ''),
            'errorLine1': node.get('errorLine1', ''),
            'errorLine2': node.get('errorLine2', ''),
            'locations':  locs,
        })

    a11y   = [i for i in issues if i['id'] in ACCESSIBILITY_IDS]
    others = [i for i in issues if i['id'] not in ACCESSIBILITY_IDS]

    total    = len(issues)
    n_a11y   = len(a11y)
    n_errors = len([i for i in issues if i['severity'] in ('Error', 'Fatal')])
    n_warn   = len([i for i in issues if i['severity'] == 'Warning'])

    now = datetime.utcnow().strftime('%d/%m/%Y às %H:%M UTC')

    a11y_html   = '\n'.join(issue_card(i, True)  for i in a11y)   or '<p class="empty">Nenhum problema de acessibilidade encontrado ✅</p>'
    others_html = '\n'.join(issue_card(i, False) for i in others) or '<p class="empty">Nenhum outro problema encontrado ✅</p>'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lint · Relatório de Acessibilidade</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:14px;line-height:1.6}}
a{{color:#58a6ff}}
header{{background:#161b22;border-bottom:1px solid #30363d;padding:18px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
header h1{{font-size:18px;font-weight:600;color:#f0f6fc}}
header .sub{{color:#8b949e;font-size:12px;margin-top:3px}}
.agp-tag{{background:#1f6feb22;color:#58a6ff;border:1px solid #1f6feb55;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}}
.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;padding:24px 32px;max-width:1160px;margin:0 auto}}
.scard{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:18px;text-align:center}}
.scard .num{{font-size:38px;font-weight:700;line-height:1;margin-bottom:5px}}
.scard .lbl{{color:#8b949e;font-size:11px;text-transform:uppercase;letter-spacing:.6px}}
.s-total .num{{color:#58a6ff}}
.s-a11y{{border-color:#f8514955;background:linear-gradient(135deg,#1a080855,#161b22)}}
.s-a11y .num{{color:#ff7b72}}
.s-err .num{{color:#f85149}}
.s-warn .num{{color:#e3b341}}
main{{max-width:1160px;margin:0 auto;padding:0 32px 48px}}
.section{{margin-bottom:36px}}
.sec-header{{display:flex;align-items:center;gap:10px;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #30363d}}
.sec-header h2{{font-size:15px;font-weight:600;color:#f0f6fc}}
.a11y-section .sec-header h2{{color:#ff7b72}}
.sec-count{{background:#30363d;color:#c9d1d9;padding:2px 8px;border-radius:10px;font-size:11px}}
.a11y-section .sec-count{{background:#2a080855;color:#ff7b72;border:1px solid #f8514955}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:18px;margin-bottom:10px;border-left:3px solid #e3b341}}
.a11y-card{{background:linear-gradient(135deg,#1a0d0d 0%,#161b22 50%)}}
.card-header{{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:10px}}
.issue-name{{font-weight:600;font-size:14px;color:#f0f6fc}}
.issue-id{{color:#8b949e;font-size:11px;font-family:monospace;margin-left:6px}}
.card-meta{{display:flex;gap:6px;align-items:center;flex-wrap:wrap}}
.badge{{padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}}
.cat-tag{{color:#8b949e;font-size:10px;background:#21262d;padding:2px 7px;border-radius:4px}}
.location{{font-family:monospace;font-size:11px;color:#58a6ff;margin-bottom:8px}}
.snippet{{background:#010409;border:1px solid #30363d;border-radius:4px;padding:10px 12px;font-family:'Consolas','Monaco',monospace;font-size:12px;color:#e6edf3;overflow-x:auto;margin-bottom:12px;white-space:pre-wrap;word-break:break-all}}
.explain{{margin-bottom:8px}}
.block-title{{font-size:10px;font-weight:700;color:#8b949e;text-transform:uppercase;letter-spacing:.6px;margin-bottom:4px}}
.fix-title{{color:#3fb950}}
.fixbox{{border-top:1px solid #21262d;padding-top:10px;margin-top:10px}}
.explain p,.fixbox p{{font-size:13px;color:#c9d1d9}}
code{{background:#21262d;color:#79c0ff;padding:1px 4px;border-radius:3px;font-family:monospace;font-size:12px}}
.empty{{color:#8b949e;text-align:center;padding:32px;background:#161b22;border-radius:8px;border:1px dashed #30363d}}
footer{{text-align:center;color:#8b949e;font-size:11px;padding:20px;border-top:1px solid #21262d}}
@media(max-width:700px){{.summary{{grid-template-columns:repeat(2,1fr)}}header,main{{padding-left:16px;padding-right:16px}}.summary{{padding:16px}}}}
</style>
</head>
<body>
<header>
  <div>
    <h1>Android Lint — Relatório de Acessibilidade</h1>
    <div class="sub">Gerado em {now}</div>
  </div>
  <span class="agp-tag">AGP 8.3.0</span>
</header>

<div class="summary">
  <div class="scard s-total"><div class="num">{total}</div><div class="lbl">Total de Issues</div></div>
  <div class="scard s-a11y"><div class="num">{n_a11y}</div><div class="lbl">Acessibilidade</div></div>
  <div class="scard s-err"><div class="num">{n_errors}</div><div class="lbl">Erros</div></div>
  <div class="scard s-warn"><div class="num">{n_warn}</div><div class="lbl">Avisos</div></div>
</div>

<main>
  <section class="section a11y-section">
    <div class="sec-header">
      <h2>♿ Problemas de Acessibilidade</h2>
      <span class="sec-count">{n_a11y}</span>
    </div>
    {a11y_html}
  </section>

  <section class="section">
    <div class="sec-header">
      <h2>Outros Problemas</h2>
      <span class="sec-count">{len(others)}</span>
    </div>
    {others_html}
  </section>
</main>

<footer>Aula Prática · Android Lint para Acessibilidade · Relatório gerado automaticamente</footer>
</body>
</html>"""

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Dashboard gerado: {out_path}")


if __name__ == '__main__':
    xml_in  = sys.argv[1] if len(sys.argv) > 1 else '/project/app/build/reports/lint-results-debug.xml'
    html_out = sys.argv[2] if len(sys.argv) > 2 else '/reports/index.html'
    generate(xml_in, html_out)
