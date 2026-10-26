"""Guilherme"""
"""Jhonny"""

import tkinter as tk
from tkinter import ttk, messagebox

from sistema import SistemaSenhas, ESPECIALIDADES_PERMITIDAS, CATEGORIAS_PRIORIDADE

COR_FUNDO = "#f4f7fa"
COR_TITULO = "#1f4e79"
COR_BOTAO = "#2e75b6"
FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_TEXTO = ("Segoe UI", 11)
FONTE_GRANDE = ("Segoe UI", 36, "bold")


def rotulo_especialidade(item: dict) -> str:
    """Texto exibido nos menus suspensos, ex.: 'C1 — Clínica Geral'."""
    return f"{item['codigo']} — {item['nome']}"


def codigo_do_rotulo(rotulo: str) -> str:
    return rotulo.split(" — ")[0].strip()


def tipo_texto(tipo: str) -> str:
    return "Normal" if tipo == "N" else "Prioritário"


class Tela(tk.Frame):
    """Base de todas as telas: título, botão Voltar e método atualizar()."""

    titulo = ""

    def __init__(self, app: "App"):
        super().__init__(app.container, bg=COR_FUNDO)
        self.app = app
        self.sistema = app.sistema
        tk.Label(self, text=self.titulo, font=FONTE_TITULO,
                 bg=COR_FUNDO, fg=COR_TITULO).pack(pady=(20, 10))
        self.corpo = tk.Frame(self, bg=COR_FUNDO)
        self.corpo.pack(fill="both", expand=True, padx=30)
        tk.Button(self, text="← Voltar ao menu", font=FONTE_TEXTO,
                  command=lambda: app.mostrar("Menu")).pack(pady=15)

    def atualizar(self):
        """Chamado sempre que a tela é exibida ou os dados mudam."""

    def rotulos_especialidades(self) -> list[str]:
        return [rotulo_especialidade(e) for e in self.sistema.listar_especialidades()]

    def erro(self, exc: Exception):
        mensagem = exc.args[0] if exc.args else str(exc)
        messagebox.showerror("Operação inválida", str(mensagem))


# ---------------------------------------------------------------- Tela 1
class TelaMenu(Tela):
    titulo = "Sistema de Gerenciamento de Senhas — Clínica"

    def __init__(self, app):
        super().__init__(app)
        botoes = [
            ("1. Cadastro de especialidades", "Cadastro"),
            ("2. Emissão de senhas", "Emissao"),
            ("3. Gerenciamento das filas", "Filas"),
            ("4. Painel de atendimento", "Painel"),
            ("5. Tempo estimado de espera", "Tempo"),
        ]
        for texto, destino in botoes:
            tk.Button(self.corpo, text=texto, font=("Segoe UI", 13), width=34,
                      bg=COR_BOTAO, fg="white", pady=6,
                      command=lambda d=destino: app.mostrar(d)).pack(pady=6)
        tk.Button(self.corpo, text="Sair", font=("Segoe UI", 12), width=34,
                  command=app.destroy).pack(pady=(14, 0))


# ---------------------------------------------------------------- Tela 2
class TelaCadastro(Tela):
    titulo = "Cadastro de especialidades"

    def __init__(self, app):
        super().__init__(app)
        tk.Label(self.corpo, text="Escolha até 3 especialidades:",
                 font=FONTE_TEXTO, bg=COR_FUNDO).pack(pady=(5, 5))
        self.var = tk.StringVar()
        ttk.Combobox(self.corpo, textvariable=self.var, state="readonly",
                     values=ESPECIALIDADES_PERMITIDAS, width=30,
                     font=FONTE_TEXTO).pack()
        tk.Button(self.corpo, text="Cadastrar", font=FONTE_TEXTO,
                  bg=COR_BOTAO, fg="white", command=self.cadastrar).pack(pady=10)
        tk.Label(self.corpo, text="Especialidades cadastradas:",
                 font=FONTE_TEXTO, bg=COR_FUNDO).pack()
        self.lista = tk.Listbox(self.corpo, height=4, width=40, font=FONTE_TEXTO)
        self.lista.pack(pady=5)

    def cadastrar(self):
        try:
            self.sistema.cadastrar_especialidade(self.var.get())
        except (ValueError, KeyError) as exc:
            self.erro(exc)
            return
        self.var.set("")
        self.app.atualizar_tudo()

    def atualizar(self):
        self.lista.delete(0, "end")
        for r in self.rotulos_especialidades():
            self.lista.insert("end", r)


# ---------------------------------------------------------------- Tela 3
class TelaEmissao(Tela):
    titulo = "Emissão de senhas"

    def __init__(self, app):
        super().__init__(app)
        c = self.corpo
        tk.Label(c, text="Especialidade:", font=FONTE_TEXTO, bg=COR_FUNDO).pack()
        self.esp = ttk.Combobox(c, state="readonly", width=34, font=FONTE_TEXTO)
        self.esp.pack(pady=(0, 8))

        self.tipo = tk.StringVar(value="N")
        linha = tk.Frame(c, bg=COR_FUNDO)
        linha.pack()
        for texto, valor in (("Normal (N)", "N"), ("Prioritário (P)", "P")):
            tk.Radiobutton(linha, text=texto, value=valor, variable=self.tipo,
                           font=FONTE_TEXTO, bg=COR_FUNDO,
                           command=self.alternar_categoria).pack(side="left", padx=10)

        tk.Label(c, text="Categoria de prioridade:", font=FONTE_TEXTO,
                 bg=COR_FUNDO).pack(pady=(8, 0))
        self.cat = ttk.Combobox(c, state="disabled", width=40, font=FONTE_TEXTO,
                                values=CATEGORIAS_PRIORIDADE)
        self.cat.pack()

        tk.Button(c, text="Emitir senha", font=FONTE_TEXTO, bg=COR_BOTAO,
                  fg="white", command=self.emitir).pack(pady=12)
        self.resultado = tk.Label(c, text="", font=FONTE_GRANDE, bg=COR_FUNDO,
                                  fg=COR_TITULO)
        self.resultado.pack()
        self.detalhe = tk.Label(c, text="", font=FONTE_TEXTO, bg=COR_FUNDO)
        self.detalhe.pack()

    def alternar_categoria(self):
        if self.tipo.get() == "P":
            self.cat.config(state="readonly")
        else:
            self.cat.set("")
            self.cat.config(state="disabled")

    def emitir(self):
        rotulo = self.esp.get()
        if not rotulo:
            messagebox.showerror("Operação inválida", "Selecione uma especialidade.")
            return
        categoria = self.cat.get() if self.tipo.get() == "P" else None
        if self.tipo.get() == "P" and not categoria:
            messagebox.showerror("Operação inválida",
                                 "Selecione a categoria de prioridade.")
            return
        try:
            senha = self.sistema.emitir_senha(codigo_do_rotulo(rotulo),
                                              self.tipo.get(), categoria)
        except (ValueError, KeyError) as exc:
            self.erro(exc)
            return
        self.resultado.config(text=senha["senha"])
        extra = senha["categoria_prioridade"] or "Atendimento normal"
        self.detalhe.config(text=f"{senha['especialidade']} — {extra}")
        self.app.atualizar_tudo()

    def atualizar(self):
        valores = self.rotulos_especialidades()
        self.esp.config(values=valores)
        if self.esp.get() not in valores:
            self.esp.set(valores[0] if valores else "")


# Tela 4
class TelaFilas(Tela):
    titulo = "Gerenciamento das filas"

    def __init__(self, app):
        super().__init__(app)
        c = self.corpo
        topo = tk.Frame(c, bg=COR_FUNDO)
        topo.pack()
        tk.Label(topo, text="Especialidade:", font=FONTE_TEXTO,
                 bg=COR_FUNDO).pack(side="left", padx=5)
        self.esp = ttk.Combobox(topo, state="readonly", width=28, font=FONTE_TEXTO)
        self.esp.pack(side="left")
        self.esp.bind("<<ComboboxSelected>>", lambda e: self.atualizar())

        self.resumo = tk.Label(c, text="", font=FONTE_TEXTO, bg=COR_FUNDO)
        self.resumo.pack(pady=8)

        colunas = tk.Frame(c, bg=COR_FUNDO)
        colunas.pack()
        self.lista_normais = self._coluna(colunas, "Senhas normais")
        self.lista_prior = self._coluna(colunas, "Senhas prioritárias")
        self.lista_ordem = self._coluna(colunas, "Ordem prevista")

        tk.Button(c, text="Chamar próximo", font=FONTE_TEXTO, bg=COR_BOTAO,
                  fg="white", command=self.chamar).pack(pady=10)

    @staticmethod
    def _coluna(pai, titulo):
        quadro = tk.Frame(pai, bg=COR_FUNDO)
        quadro.pack(side="left", padx=8)
        tk.Label(quadro, text=titulo, font=("Segoe UI", 11, "bold"),
                 bg=COR_FUNDO).pack()
        lista = tk.Listbox(quadro, height=10, width=24, font=FONTE_TEXTO)
        lista.pack()
        return lista

    def chamar(self):
        rotulo = self.esp.get()
        if not rotulo:
            messagebox.showerror("Operação inválida", "Selecione uma especialidade.")
            return
        try:
            chamada = self.sistema.chamar_proximo(codigo_do_rotulo(rotulo))
        except (ValueError, KeyError) as exc:
            self.erro(exc)
            return
        if chamada is None:
            messagebox.showinfo("Fila vazia",
                                "Não há pacientes aguardando nesta especialidade.")
        else:
            messagebox.showinfo("Paciente chamado",
                                f"Senha chamada: {chamada['senha']}")
        self.app.atualizar_tudo()

    def atualizar(self):
        valores = self.rotulos_especialidades()
        self.esp.config(values=valores)
        if self.esp.get() not in valores:
            self.esp.set(valores[0] if valores else "")
        for lista in (self.lista_normais, self.lista_prior, self.lista_ordem):
            lista.delete(0, "end")
        if not self.esp.get():
            self.resumo.config(text="Nenhuma especialidade cadastrada.")
            return
        fila = self.sistema.consultar_fila(codigo_do_rotulo(self.esp.get()))
        self.resumo.config(
            text=(f"{fila['especialidade']} — aguardando: {fila['quantidade_aguardando']} "
                  f"(normais: {fila['quantidade_normais']}, "
                  f"prioritárias: {fila['quantidade_prioritarias']})"))
        for s in fila["senhas_normais"]:
            self.lista_normais.insert("end", s["senha"])
        for s in fila["senhas_prioritarias"]:
            self.lista_prior.insert("end", f"{s['senha']}  (nível {s['nivel_prioridade']})")
        for s in fila["ordem_atendimento"]:
            self.lista_ordem.insert("end", f"{s['posicao']}º  {s['senha']}")


# ---------------------------------------------------------------- Tela 5
class TelaPainel(Tela):
    titulo = "Painel de atendimento"

    def __init__(self, app):
        super().__init__(app)
        c = self.corpo
        tk.Label(c, text="SENHA CHAMADA", font=("Segoe UI", 14, "bold"),
                 bg=COR_FUNDO).pack(pady=(10, 0))
        self.senha = tk.Label(c, text="—", font=("Segoe UI", 54, "bold"),
                              bg=COR_FUNDO, fg=COR_TITULO)
        self.senha.pack()
        self.esp = tk.Label(c, text="Especialidade: —", font=("Segoe UI", 14),
                            bg=COR_FUNDO)
        self.esp.pack(pady=3)
        self.tipo = tk.Label(c, text="Tipo de atendimento: —", font=("Segoe UI", 14),
                             bg=COR_FUNDO)
        self.tipo.pack(pady=3)
        self.aguardando = tk.Label(c, text="", font=("Segoe UI", 14), bg=COR_FUNDO)
        self.aguardando.pack(pady=3)
        tk.Label(c, text="Aguardando por especialidade", font=("Segoe UI", 12, "bold"),
                 bg=COR_FUNDO).pack(pady=(12, 0))
        self.por_esp = tk.Label(c, text="", font=("Segoe UI", 13), bg=COR_FUNDO,
                                justify="left")
        self.por_esp.pack()
        self.total = tk.Label(c, text="", font=FONTE_TEXTO, bg=COR_FUNDO)
        self.total.pack(pady=3)

    def atualizar(self):
        painel = self.sistema.obter_painel()
        ultima = painel["ultima_senha_chamada"]
        if ultima is None:
            self.senha.config(text="—")
            self.esp.config(text="Especialidade: —")
            self.tipo.config(text="Tipo de atendimento: —")
            self.aguardando.config(text="Aguardando nesta especialidade: —")
        else:
            fila = self.sistema.consultar_fila(ultima["codigo_especialidade"])
            self.senha.config(text=ultima["senha"])
            self.esp.config(text=f"Especialidade: {ultima['especialidade']}")
            self.tipo.config(text=f"Tipo de atendimento: {tipo_texto(ultima['tipo'])}")
            self.aguardando.config(
                text=f"Aguardando nesta especialidade: {fila['quantidade_aguardando']}")
        linhas = [f"{e['codigo']} — {e['nome']}: {e['quantidade_aguardando']}"
                  for e in painel["especialidades"]]
        self.por_esp.config(text="\n".join(linhas) if linhas
                            else "Nenhuma especialidade cadastrada.")
        self.total.config(text=f"Total aguardando na clínica: {painel['total_aguardando']}")


# ---------------------------------------------------------------- Tela 6
class TelaTempo(Tela):
    titulo = "Tempo estimado de espera"

    def __init__(self, app):
        super().__init__(app)
        c = self.corpo
        tk.Label(c, text="Especialidade:", font=FONTE_TEXTO, bg=COR_FUNDO).pack()
        self.esp = ttk.Combobox(c, state="readonly", width=34, font=FONTE_TEXTO)
        self.esp.pack(pady=(0, 8))
        self.esp.bind("<<ComboboxSelected>>", lambda e: self.carregar_senhas())

        tk.Label(c, text="Senha (aguardando):", font=FONTE_TEXTO,
                 bg=COR_FUNDO).pack()
        self.senha = ttk.Combobox(c, width=20, font=FONTE_TEXTO)
        self.senha.pack()
        tk.Label(c, text="(escolha da lista ou digite, ex.: C1-N001)",
                 font=("Segoe UI", 9), bg=COR_FUNDO).pack()

        tk.Button(c, text="Consultar", font=FONTE_TEXTO, bg=COR_BOTAO, fg="white",
                  command=self.consultar).pack(pady=10)
        self.resultado = tk.Label(c, text="", font=("Segoe UI", 14), bg=COR_FUNDO,
                                  justify="left")
        self.resultado.pack()

    def carregar_senhas(self):
        self.senha.set("")
        if not self.esp.get():
            self.senha.config(values=[])
            return
        fila = self.sistema.consultar_fila(codigo_do_rotulo(self.esp.get()))
        self.senha.config(values=[s["senha"] for s in fila["ordem_atendimento"]])

    def consultar(self):
        if not self.esp.get():
            messagebox.showerror("Operação inválida", "Selecione uma especialidade.")
            return
        codigo = self.senha.get().strip()
        if not codigo:
            messagebox.showerror("Operação inválida", "Informe a senha a consultar.")
            return
        try:
            r = self.sistema.consultar_tempo_espera(codigo_do_rotulo(self.esp.get()),
                                                    codigo)
        except (ValueError, KeyError, LookupError) as exc:
            self.erro(exc)
            return
        self.resultado.config(text=(
            f"Senha {r['senha']} — {r['especialidade']}\n"
            f"Posição na fila: {r['posicao']}º\n"
            f"Pacientes à frente: {r['pacientes_a_frente']}\n"
            f"Tempo estimado: {r['pacientes_a_frente']} × 30 = "
            f"{r['tempo_estimado_minutos']} minutos"))

    def atualizar(self):
        valores = self.rotulos_especialidades()
        self.esp.config(values=valores)
        if self.esp.get() not in valores:
            self.esp.set(valores[0] if valores else "")
        self.carregar_senhas()
        self.resultado.config(text="")


# Aplicação
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gerenciamento de Senhas — Clínica")
        self.geometry("820x640")
        self.configure(bg=COR_FUNDO)
        # Uma única instância compartilhada por todas as telas.
        self.sistema = SistemaSenhas()

        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill="both", expand=True)
        self.telas: dict[str, Tela] = {}
        for nome, classe in (("Menu", TelaMenu), ("Cadastro", TelaCadastro),
                             ("Emissao", TelaEmissao), ("Filas", TelaFilas),
                             ("Painel", TelaPainel), ("Tempo", TelaTempo)):
            tela = classe(self)
            tela.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.telas[nome] = tela
        self.atual = "Menu"
        self.mostrar("Menu")
        self._atualizar_painel_periodicamente()

    def mostrar(self, nome: str):
        self.atual = nome
        self.telas[nome].atualizar()
        self.telas[nome].tkraise()

    def atualizar_tudo(self):
        for tela in self.telas.values():
            tela.atualizar()

    def _atualizar_painel_periodicamente(self):
        try:
            if self.atual == "Painel":
                self.telas["Painel"].atualizar()
        finally:
            self.after(1000, self._atualizar_painel_periodicamente)


if __name__ == "__main__":
    App().mainloop()
