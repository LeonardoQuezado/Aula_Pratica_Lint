#!/usr/bin/env python3
"""Interface web para rodar o Android Lint sobre código XML gerado por IA."""
from flask import Flask, request, redirect
import subprocess
import re
import os

KNOWN_DRAWABLES = {
    'ic_account','ic_add','ic_arrow_down','ic_arrow_left','ic_arrow_right','ic_arrow_up',
    'ic_back','ic_bank','ic_barcode','ic_bell','ic_calendar','ic_card','ic_cards','ic_cash',
    'ic_chat','ic_check','ic_close','ic_config','ic_copy','ic_credit_card','ic_debit_card',
    'ic_delete','ic_deposit','ic_edit','ic_extract','ic_eye','ic_eye_off','ic_favorite',
    'ic_filter','ic_help','ic_history','ic_home','ic_info','ic_insurance','ic_invest',
    'ic_investment','ic_loan','ic_loans','ic_lock','ic_market','ic_menu','ic_money',
    'ic_more','ic_notification','ic_payment','ic_person','ic_pix','ic_profile','ic_qr',
    'ic_qr_code','ic_receive','ic_refresh','ic_search','ic_security','ic_send',
    'ic_settings','ic_shopping','ic_sort','ic_star','ic_statement','ic_support',
    'ic_transfer','ic_transfer_money','ic_visibility','ic_visibility_off','ic_withdraw',
}

STRING_MAP = {
    'app_name':'Lint Prática','profile_photo':'Foto do perfil','edit_profile':'Editar perfil',
    'save_changes':'Salvar alterações','save':'Salvar','phone':'Telefone','about_me':'Sobre mim',
    'personal_information':'Informações pessoais','email':'E-mail','name':'Nome',
    'password':'Senha','login':'Entrar','register':'Cadastrar','username':'Usuário',
    'confirm_password':'Confirmar senha','forgot_password':'Esqueceu a senha?',
    'notifications':'Notificações','settings':'Configurações','search':'Buscar',
    'home':'Início','profile':'Perfil','logout':'Sair','cancel':'Cancelar',
    'confirm':'Confirmar','back':'Voltar','next':'Próximo','finish':'Concluir',
    'submit':'Enviar','close':'Fechar','delete':'Excluir','edit':'Editar',
    'add':'Adicionar','remove':'Remover','update':'Atualizar','send':'Enviar',
    'receive':'Receber','transfer':'Transferir','payment':'Pagamento','balance':'Saldo',
    'history':'Histórico','help':'Ajuda','about':'Sobre','contact':'Contato',
    'support':'Suporte','security':'Segurança','account':'Conta','address':'Endereço',
    'mark_all_read':'Marcar todas como lidas','no_notifications':'Nenhuma notificação',
    'clear_all':'Limpar tudo','filter':'Filtrar','title':'Título','description':'Descrição',
    'date':'Data','time':'Hora','amount':'Valor','total':'Total','status':'Status',
    'welcome':'Bem-vindo','continue':'Continuar','loading':'Carregando',
}

def snake_to_label(name):
    return name.replace('_', ' ').capitalize()

def preprocess_xml(code):
    def replace_string(m):
        name = m.group(1)
        return STRING_MAP.get(name, snake_to_label(name))

    def replace_drawable(m):
        name = m.group(1)
        return '@drawable/{}'.format(name if name in KNOWN_DRAWABLES else 'ic_account')

    code = re.sub(r'@string/(\w+)', replace_string, code)
    code = re.sub(r'@drawable/(\w+)', replace_drawable, code)
    code = re.sub(r'@mipmap/\w+', '@drawable/ic_account', code)
    return code

app = Flask(__name__)

PROJECT_DIR  = '/project'
LAYOUT_FILE  = os.path.join(PROJECT_DIR, 'app/src/main/res/layout/generated_layout.xml')
XML_REPORT   = os.path.join(PROJECT_DIR, 'app/build/reports/lint-results-debug.xml')
HTML_REPORT  = '/reports/index.html'

PLACEHOLDER = """\
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:gravity="center"
    android:orientation="vertical"
    android:padding="32dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Cole o código XML gerado pelo GPT na interface web"
        android:textSize="16sp"
        android:gravity="center" />

</LinearLayout>
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lint · Analisador de Acessibilidade</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0d1117;color:#c9d1d9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;display:flex;flex-direction:column}
header{background:#161b22;border-bottom:1px solid #30363d;padding:18px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
header h1{font-size:18px;font-weight:600;color:#f0f6fc}
header .sub{color:#8b949e;font-size:12px;margin-top:3px}
.tag{background:#1f6feb22;color:#58a6ff;border:1px solid #1f6feb55;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:600}
main{flex:1;display:flex;flex-direction:column;align-items:center;padding:36px 24px}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:32px;width:100%;max-width:880px}
.card h2{font-size:15px;font-weight:600;color:#f0f6fc;margin-bottom:8px}
.steps{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:16px 20px;margin-bottom:22px;font-size:13px;line-height:2.2}
.steps div span{background:#1f6feb;color:#fff;font-weight:700;font-size:11px;padding:2px 7px;border-radius:4px;margin-right:10px}
textarea{width:100%;height:380px;background:#010409;border:1px solid #30363d;border-radius:6px;color:#e6edf3;font-family:'Consolas','Monaco',monospace;font-size:13px;padding:14px;resize:vertical;outline:none;transition:border-color .2s;line-height:1.5}
textarea:focus{border-color:#1f6feb}
textarea::placeholder{color:#484f58}
.btn{display:block;width:100%;margin-top:14px;padding:13px;background:#238636;color:#fff;font-size:15px;font-weight:600;border:none;border-radius:6px;cursor:pointer;transition:background .2s}
.btn:hover{background:#2ea043}
.btn:disabled{background:#21262d;color:#8b949e;cursor:not-allowed}
.loading{display:none;text-align:center;margin-top:16px;color:#8b949e;font-size:13px;padding:12px;background:#161b22;border-radius:6px;border:1px solid #30363d}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #30363d;border-top-color:#58a6ff;border-radius:50%;animation:spin .8s linear infinite;margin-right:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}
footer{text-align:center;color:#8b949e;font-size:11px;padding:20px;border-top:1px solid #21262d}
</style>
</head>
<body>
<header>
  <div>
    <h1>Android Lint — Analisador de Acessibilidade</h1>
    <div class="sub">Cole o layout XML gerado pelo GPT e receba o relatório de acessibilidade</div>
  </div>
  <span class="tag">Android XML Layout</span>
</header>
<main>
  <div class="card">
    <h2>Como usar</h2>
    <div class="steps">
      <div><span>1</span>Acesse o GPT EstudoAcessibilidade e gere o código XML de uma tela</div>
      <div><span>2</span>Copie todo o código XML gerado</div>
      <div><span>3</span>Cole no campo abaixo e clique em Analisar</div>
      <div><span>4</span>Aguarde cerca de 30 segundos e veja o relatório</div>
    </div>
    <form method="POST" action="/analisar" onsubmit="return startLoading()">
      <textarea name="code" placeholder="Cole aqui o layout XML gerado pelo GPT EstudoAcessibilidade..."></textarea>
      <button class="btn" type="submit" id="btn">Analisar com Lint</button>
      <div class="loading" id="loading">
        <span class="spinner"></span>Rodando o Lint, aguarde cerca de 30 segundos...
      </div>
    </form>
  </div>
</main>
<footer>Aula Prática · Android Lint para Acessibilidade</footer>
<script>
function startLoading(){
  var code=document.querySelector('textarea[name=code]').value.trim();
  if(!code){alert('Cole o código XML antes de analisar.');return false;}
  document.getElementById('btn').disabled=true;
  document.getElementById('btn').textContent='Analisando...';
  document.getElementById('loading').style.display='block';
  return true;
}
</script>
</body>
</html>"""

ERROR_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Lint · Erro de Compilação</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0d1117;color:#c9d1d9;font-family:-apple-system,sans-serif;padding:40px 32px;max-width:900px;margin:0 auto}}
h2{{color:#f85149;font-size:18px;margin-bottom:12px}}
p{{color:#8b949e;font-size:13px;margin-bottom:20px;line-height:1.6}}
pre{{background:#010409;border:1px solid #f8514955;border-radius:6px;padding:16px;font-size:12px;color:#ffa198;overflow-x:auto;white-space:pre-wrap;max-height:400px;overflow-y:auto}}
a{{color:#58a6ff;font-size:14px;display:inline-block;margin-top:24px;text-decoration:none;border:1px solid #30363d;padding:8px 16px;border-radius:6px}}
a:hover{{border-color:#58a6ff}}
</style>
</head>
<body>
<h2>Erro de compilação</h2>
<p>O código XML colado não compilou. Verifique se o XML está bem formado e tente novamente.</p>
<pre>{output}</pre>
<a href="/">← Voltar e tentar novamente</a>
</body>
</html>"""


@app.route('/')
def index():
    return INDEX_HTML


@app.route('/analisar', methods=['POST'])
def analisar():
    code = request.form.get('code', '').strip()
    if not code:
        return redirect('/')

    code = preprocess_xml(code)
    os.makedirs(os.path.dirname(LAYOUT_FILE), exist_ok=True)
    with open(LAYOUT_FILE, 'w', encoding='utf-8') as f:
        f.write(code)

    if os.path.exists(XML_REPORT):
        os.remove(XML_REPORT)

    blame_dir = os.path.join(PROJECT_DIR, 'app/build/intermediates/merged_res_blame_folder')
    if os.path.exists(blame_dir):
        import shutil
        shutil.rmtree(blame_dir, ignore_errors=True)

    result = subprocess.run(
        ['gradle', 'lintDebug', '--no-daemon'],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if os.path.exists(XML_REPORT):
        subprocess.run(['python3', '/generate_dashboard.py', XML_REPORT, HTML_REPORT])
        return redirect('/relatorio')

    output = (result.stdout + result.stderr)[-4000:]
    return ERROR_HTML.format(output=output), 500


@app.route('/relatorio')
def relatorio():
    if os.path.exists(HTML_REPORT):
        with open(HTML_REPORT, 'r', encoding='utf-8') as f:
            content = f.read()
        back = ('<a href="/" style="position:fixed;top:18px;right:24px;color:#58a6ff;'
                'font-size:13px;text-decoration:none;background:#161b22;padding:7px 16px;'
                'border-radius:6px;border:1px solid #30363d;z-index:999">← Nova análise</a>')
        return content.replace('</header>', back + '</header>', 1)
    return redirect('/')


if __name__ == '__main__':
    if not os.path.exists(LAYOUT_FILE):
        os.makedirs(os.path.dirname(LAYOUT_FILE), exist_ok=True)
        with open(LAYOUT_FILE, 'w') as f:
            f.write(PLACEHOLDER)
    app.run(host='0.0.0.0', port=8080, debug=False)
