"""Regras de negócio da clínica (itens 3.1 a 4 do trabalho).

Este módulo não depende de Tkinter. A interface gráfica pode importar
SistemaSenhas e consumir os dicionários retornados por seus métodos.
"""

from especialidades import ESPECIALIDADES_PERMITIDAS, CATEGORIAS_PRIORIDADE
from filas import FilaAtendimento, Senha


class SistemaSenhas:
    MAX_ESPECIALIDADES = 3
    MINUTOS_POR_ATENDIMENTO = 30

    def __init__(self):
        self._filas: dict[str, FilaAtendimento] = {}
        self._ultima_chamada: Senha | None = None

    def cadastrar_especialidade(self, nome: str) -> dict:
        """Cadastra uma das cinco opções, até o máximo de três; devolve C1/C2/C3."""
        if not isinstance(nome, str):
            raise ValueError("Escolha uma especialidade válida.")
        nome = nome.strip()
        correspondencia = next(
            (permitida for permitida in ESPECIALIDADES_PERMITIDAS
             if permitida.casefold() == nome.casefold()),
            None,
        )
        if correspondencia is None:
            raise ValueError("Especialidade inválida. Escolha uma das cinco disponíveis.")
        if any(fila.especialidade == correspondencia for fila in self._filas.values()):
            raise ValueError("Esta especialidade já foi cadastrada.")
        if len(self._filas) >= self.MAX_ESPECIALIDADES:
            raise ValueError("Limite de três especialidades atingido.")

        codigo = f"C{len(self._filas) + 1}"
        self._filas[codigo] = FilaAtendimento(codigo, correspondencia)
        return {"codigo": codigo, "nome": correspondencia}

    def listar_especialidades(self) -> list[dict]:
        """Lista as opções cadastradas com identificadores e totais."""
        return [
            {
                "codigo": codigo,
                "nome": fila.especialidade,
                "quantidade_aguardando": fila.quantidade_total,
            }
            for codigo, fila in self._filas.items()
        ]

    def _obter_fila(self, especialidade: str) -> FilaAtendimento:
        """Aceita identificador (C1) ou nome (Clínica Geral)."""
        if not isinstance(especialidade, str):
            raise ValueError("Informe o código ou o nome da especialidade.")
        chave = especialidade.strip().casefold()
        for codigo, fila in self._filas.items():
            if codigo.casefold() == chave or fila.especialidade.casefold() == chave:
                return fila
        raise KeyError(f"Especialidade não cadastrada: {especialidade}")

    def emitir_senha(
        self,
        especialidade: str,
        tipo: str,
        categoria_prioridade: str | int | None = None,
    ) -> dict:
        """Emite uma senha N/P na especialidade escolhida.

        Para prioritária, categoria_prioridade deve ser 1..6 ou o texto
        exatamente correspondente a uma das seis categorias do enunciado.
        """
        fila = self._obter_fila(especialidade)
        return fila.emitir(tipo, categoria_prioridade).para_dict()

    def chamar_proximo(self, especialidade: str) -> dict | None:
        """Chama e REMOVE a primeira senha válida, ou retorna None se vazia."""
        fila = self._obter_fila(especialidade)
        senha = fila.chamar_proximo()
        if senha is None:
            return None
        self._ultima_chamada = senha
        return senha.para_dict()

    def consultar_fila(self, especialidade: str) -> dict:
        """Retorna fotografia atual das filas sem alterar o atendimento."""
        fila = self._obter_fila(especialidade)
        ordem = fila.ordem_prevista()
        return {
            "codigo_especialidade": fila.codigo_especialidade,
            "especialidade": fila.especialidade,
            "quantidade_aguardando": fila.quantidade_total,
            "quantidade_normais": fila.quantidade_normais,
            "quantidade_prioritarias": fila.quantidade_prioritarias,
            "senhas_normais": [s.para_dict() for s in fila.senhas_normais()],
            "senhas_prioritarias": [s.para_dict() for s in fila.senhas_prioritarias()],
            "ordem_atendimento": [
                {**s.para_dict(), "posicao": indice, "tempo_estimado_minutos":
                 (indice - 1) * self.MINUTOS_POR_ATENDIMENTO}
                for indice, s in enumerate(ordem, start=1)
            ],
        }

    def consultar_tempo_espera(self, especialidade: str, codigo_senha: str) -> dict:
        """Calcula a espera da senha segundo sua posição ATUAL na fila.

        Levanta LookupError quando a senha não está aguardando.
        """
        if not isinstance(codigo_senha, str):
            raise ValueError("Informe o código da senha a consultar.")
        resultado = self.consultar_fila(especialidade)
        for senha in resultado["ordem_atendimento"]:
            if senha["senha"].casefold() == codigo_senha.strip().casefold():
                a_frente = senha["posicao"] - 1
                return {
                    "senha": senha["senha"],
                    "especialidade": resultado["especialidade"],
                    "codigo_especialidade": resultado["codigo_especialidade"],
                    "posicao": senha["posicao"],
                    "pacientes_a_frente": a_frente,
                    "tempo_estimado_minutos": a_frente * self.MINUTOS_POR_ATENDIMENTO,
                }
        raise LookupError("A senha não está aguardando nesta especialidade.")

    def consultar_todas_filas(self) -> list[dict]:
        """Consultas independentes, uma por especialidade cadastrada."""
        return [self.consultar_fila(codigo) for codigo in self._filas]

    def obter_painel(self) -> dict:
        """Dados a exibir/atualizar no painel de atendimento do Tkinter."""
        return {
            "ultima_senha_chamada": (
                self._ultima_chamada.para_dict() if self._ultima_chamada else None
            ),
            "especialidades": self.listar_especialidades(),
            "total_aguardando": sum(f.quantidade_total for f in self._filas.values()),
        }


__all__ = ["SistemaSenhas", "ESPECIALIDADES_PERMITIDAS", "CATEGORIAS_PRIORIDADE"]
