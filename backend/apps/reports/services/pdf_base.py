"""Template base para PDFs do Controle Interno — {{COMPANY_NAME}}."""

from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

COR_PRIMARIA = colors.HexColor("#0A0A0A")
COR_DESTAQUE = colors.HexColor("#404040")
COR_TEXTO = colors.HexColor("#1F1F1F")
COR_CINZA_CLARO = colors.HexColor("#F4F4F5")


def _texto(valor: object) -> str:
    return escape(str(valor or "-"))


def cabecalho_rodape(canvas, doc):
    """Desenha cabeçalho e rodapé em cada página."""
    canvas.saveState()
    largura, altura = doc.pagesize

    canvas.setFillColor(COR_PRIMARIA)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(2 * cm, altura - 1.5 * cm, "{{COMPANY_NAME}} — ECOMMERCE CONTROL")

    canvas.setFillColor(COR_DESTAQUE)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(2 * cm, altura - 2 * cm, doc.subtitulo)

    canvas.setFillColor(COR_TEXTO)
    canvas.setFont("Helvetica", 8)
    gerado_em = timezone.localtime().strftime("%d/%m/%Y às %H:%M")
    canvas.drawRightString(largura - 2 * cm, altura - 1.5 * cm, f"Gerado em: {gerado_em}")

    canvas.setStrokeColor(COR_DESTAQUE)
    canvas.setLineWidth(1)
    canvas.line(2 * cm, altura - 2.3 * cm, largura - 2 * cm, altura - 2.3 * cm)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COR_TEXTO)
    canvas.drawString(2 * cm, 1 * cm, f"Página {doc.page} · Controle Interno — {{{{COMPANY_NAME}}}}")

    canvas.restoreState()


class RelatorioPDF:
    """Wrapper para gerar PDFs com layout consistente."""

    def __init__(self, subtitulo: str, orientacao: str = "landscape"):
        self.subtitulo = subtitulo
        self.buffer = BytesIO()
        self.pagesize = landscape(A4) if orientacao == "landscape" else A4
        self.elementos = []
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="SecaoTitulo",
                parent=self.styles["Heading2"],
                fontSize=12,
                leading=15,
                textColor=COR_PRIMARIA,
                fontName="Helvetica-Bold",
                spaceBefore=4,
                spaceAfter=8,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TextoRelatorio",
                parent=self.styles["Normal"],
                fontSize=9,
                leading=13,
                textColor=COR_TEXTO,
                spaceAfter=8,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="FiltroTitulo",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=COR_PRIMARIA,
                spaceAfter=4,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="FiltroItem",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=COR_TEXTO,
                leftIndent=10,
                spaceAfter=2,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="KpiLabel",
                parent=self.styles["Normal"],
                fontSize=7,
                leading=9,
                textColor=COR_DESTAQUE,
                fontName="Helvetica",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="KpiValor",
                parent=self.styles["Normal"],
                fontSize=13,
                leading=16,
                textColor=COR_PRIMARIA,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TabelaCabecalho",
                parent=self.styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=colors.white,
                fontName="Helvetica-Bold",
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TabelaCelula",
                parent=self.styles["Normal"],
                fontSize=7,
                leading=9,
                textColor=COR_TEXTO,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="TotaisLinha",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=COR_PRIMARIA,
                fontName="Helvetica-Bold",
                spaceAfter=4,
            )
        )

    def adicionar_filtros(self, filtros: dict[str, str]):
        if not filtros:
            return
        self.elementos.append(Paragraph("Filtros aplicados:", self.styles["FiltroTitulo"]))
        for chave, valor in filtros.items():
            if valor:
                self.elementos.append(
                    Paragraph(f"• {_texto(chave)}: {_texto(valor)}", self.styles["FiltroItem"])
                )
        self.elementos.append(Spacer(1, 0.35 * cm))

    def adicionar_secao(self, titulo: str):
        self.elementos.append(Paragraph(_texto(titulo), self.styles["SecaoTitulo"]))

    def adicionar_texto(self, texto: str):
        self.elementos.append(Paragraph(_texto(texto), self.styles["TextoRelatorio"]))

    def adicionar_kpis(self, kpis: list[tuple[str, str]]):
        if not kpis:
            return

        linhas = []
        linha = []
        for label, valor in kpis:
            linha.append(
                [
                    Paragraph(_texto(label).upper(), self.styles["KpiLabel"]),
                    Paragraph(_texto(valor), self.styles["KpiValor"]),
                ]
            )
            if len(linha) == 4:
                linhas.append(linha)
                linha = []
        if linha:
            while len(linha) < 4:
                linha.append(["", ""])
            linhas.append(linha)

        largura_util = self.pagesize[0] - (4 * cm)
        tabela = Table(linhas, colWidths=[largura_util / 4] * 4)
        tabela.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        self.elementos.append(tabela)
        self.elementos.append(Spacer(1, 0.35 * cm))

    def adicionar_grafico_barras(
        self,
        titulo: str,
        dados: list[tuple[str, float]],
        cor=COR_DESTAQUE,
        largura: float | None = None,
    ):
        dados = [(label, valor) for label, valor in dados if valor > 0]
        if not dados:
            return

        self.adicionar_secao(titulo)
        largura = largura or self.pagesize[0] - (4 * cm)
        altura = max(3.5 * cm, min(8 * cm, 0.65 * cm * len(dados) + 1.5 * cm))
        drawing = Drawing(largura, altura)
        margem_esquerda = 4.2 * cm
        margem_direita = 2.4 * cm
        area_barras = largura - margem_esquerda - margem_direita
        topo = altura - 0.8 * cm
        passo = (altura - 1.4 * cm) / max(len(dados), 1)
        maximo = max(valor for _, valor in dados)

        for index, (label, valor) in enumerate(dados):
            y = topo - index * passo
            largura_barra = area_barras * (valor / maximo if maximo else 0)
            drawing.add(
                String(
                    0,
                    y + 2,
                    label[:34],
                    fontName="Helvetica",
                    fontSize=7,
                    fillColor=COR_TEXTO,
                )
            )
            drawing.add(
                Rect(
                    margem_esquerda,
                    y,
                    largura_barra,
                    8,
                    fillColor=cor,
                    strokeColor=cor,
                )
            )
            drawing.add(
                String(
                    margem_esquerda + largura_barra + 4,
                    y + 2,
                    f"{valor:,.0f}".replace(",", "."),
                    fontName="Helvetica",
                    fontSize=7,
                    fillColor=COR_TEXTO,
                )
            )

        self.elementos.append(drawing)
        self.elementos.append(Spacer(1, 0.25 * cm))

    def adicionar_tabela(self, headers: list[str], linhas: list[list[str]]):
        dados = [
            [Paragraph(_texto(header), self.styles["TabelaCabecalho"]) for header in headers]
        ]
        dados.extend(
            [
                [Paragraph(_texto(celula), self.styles["TabelaCelula"]) for celula in linha]
                for linha in linhas
            ]
        )
        largura_util = self.pagesize[0] - (4 * cm)
        col_widths = [largura_util / len(headers)] * len(headers) if headers else None
        tabela = Table(dados, colWidths=col_widths, repeatRows=1)
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_CINZA_CLARO]),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        self.elementos.append(tabela)
        self.elementos.append(Spacer(1, 0.35 * cm))

    def adicionar_totais(self, linhas: list[str]):
        for linha in linhas:
            self.elementos.append(Paragraph(_texto(linha), self.styles["TotaisLinha"]))

    def gerar(self) -> bytes:
        doc = BaseDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=3 * cm,
            bottomMargin=2 * cm,
        )
        doc.subtitulo = self.subtitulo

        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
        template = PageTemplate(id="ecommerce", frames=frame, onPage=cabecalho_rodape)
        doc.addPageTemplates([template])
        doc.build(self.elementos)
        return self.buffer.getvalue()
