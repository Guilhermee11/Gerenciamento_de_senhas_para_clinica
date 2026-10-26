"""Estruturas de dados reais: FIFO com deque e prioridade com heapq."""

from collections import deque
from dataclasses import dataclass
import heapq

from especialidades import identificar_prioridade


@dataclass(frozen=True)
class Senha:
    codigo: str
    codigo_especialidade: str
    especialidade: str
    tipo: str  # 'N' (normal) ou 'P' (prioritária)
    sequencia: int
    categoria_prioridade: str | None = None
    nivel_prioridade: int | None = None

    def para_dict(self) -> dict:
        """Representação independente das classes, adequada ao Tkinter."""
        return {
            "senha": self.codigo,
            "codigo_especialidade": self.codigo_especialidade,
            "especialidade": self.especialidade,
            "tipo": self.tipo,
            "sequencia": self.sequencia,
            "categoria_prioridade": self.categoria_prioridade,
            "nivel_prioridade": self.nivel_prioridade,
        }


class FilaAtendimento:
    """Uma fila isolada por especialidade médica.

    Prioritárias: heap por (nível de prioridade, ordem de chegada).
    Normais: deque, atendidas em FIFO após as prioritárias.
    """

    def __init__(self, codigo_especialidade: str, especialidade: str):
        self.codigo_especialidade = codigo_especialidade
        self.especialidade = especialidade
        self._contador = 0
        self._normais: deque[Senha] = deque()
        self._prioritarias: list[tuple[int, int, Senha]] = []

    def emitir(self, tipo: str, categoria_prioridade: str | int | None = None) -> Senha:
        """Valida, gera a senha e insere na fila apropriada."""
        if not isinstance(tipo, str) or tipo.strip().upper() not in ("N", "P"):
            raise ValueError("O tipo de atendimento deve ser N (normal) ou P (prioritário).")
        tipo = tipo.strip().upper()

        if tipo == "P":
            if categoria_prioridade is None:
                raise ValueError("Informe a categoria para o atendimento prioritário.")
            nivel, descricao = identificar_prioridade(categoria_prioridade)
        else:
            if categoria_prioridade is not None:
                raise ValueError("Senhas normais não recebem categoria de prioridade.")
            nivel, descricao = None, None

        # Um contador por especialidade, compartilhado entre normais e prioritárias.
        self._contador += 1
        senha = Senha(
            codigo=f"{self.codigo_especialidade}-{tipo}{self._contador:03d}",
            codigo_especialidade=self.codigo_especialidade,
            especialidade=self.especialidade,
            tipo=tipo,
            sequencia=self._contador,
            categoria_prioridade=descricao,
            nivel_prioridade=nivel,
        )
        if tipo == "P":
            heapq.heappush(self._prioritarias, (nivel, senha.sequencia, senha))
        else:
            self._normais.append(senha)
        return senha

    def chamar_proximo(self) -> Senha | None:
        """Remove e devolve a próxima senha; None significa fila vazia."""
        if self._prioritarias:
            return heapq.heappop(self._prioritarias)[2]
        if self._normais:
            return self._normais.popleft()
        return None

    def ordem_prevista(self) -> list[Senha]:
        """Consulta sem remover pacientes das estruturas de dados."""
        prioridades = [senha for _, _, senha in sorted(self._prioritarias)]
        return prioridades + list(self._normais)

    def senhas_normais(self) -> list[Senha]:
        return list(self._normais)

    def senhas_prioritarias(self) -> list[Senha]:
        return [senha for _, _, senha in sorted(self._prioritarias)]

    @property
    def quantidade_normais(self) -> int:
        return len(self._normais)

    @property
    def quantidade_prioritarias(self) -> int:
        return len(self._prioritarias)

    @property
    def quantidade_total(self) -> int:
        return self.quantidade_normais + self.quantidade_prioritarias
