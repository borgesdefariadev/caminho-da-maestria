"""
Teste visual com o Supabase: autentica, abre a tela principal e salva um
screenshot (nao altera dados).

    python teste_visual_login.py [saida.png] [email] [senha]
"""

import os
import sys
import time

from PIL import ImageGrab

import auth
from app_grandchase import GrandChaseApp

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "captura_login.png"
EMAIL = sys.argv[2] if len(sys.argv) > 2 else "teste@teste.com"
SENHA = sys.argv[3] if len(sys.argv) > 3 else "testeteste"


def main():
    sb, resp = auth.login(EMAIL, SENHA)
    user = getattr(resp, "user", None)
    if user is None:
        print("FALHA NO LOGIN:", resp)
        return
    print("logado como", user.email, user.id)
    auth.garantir_perfil(sb, user.id, username=(user.email or "").split("@")[0])

    app = GrandChaseApp(user=user, supabase=sb)
    app.attributes("-topmost", True)
    app.lift()
    app.update()
    time.sleep(2.0)
    app.update()
    x, y = app.winfo_rootx(), app.winfo_rooty()
    w, h = app.winfo_width(), app.winfo_height()
    caminho = os.path.abspath(SAIDA)
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(caminho)
    print(f"[tela] {caminho} ({w}x{h})")
    print("status:", app.status_var.get())
    for chave, valor in app.valores_dos_cards().items():
        print(f"   card {chave}: {valor}")
    for aba, ref in app.tree_refs.items():
        print(f"   aba {aba}: {len(ref['tree'].get_children())} linhas")
    app.destroy()


if __name__ == "__main__":
    main()
