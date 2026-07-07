"""
Builder de PDF com layout "rico" (banner, KPI cards, funil, leituras, recomendações).

Usado pelos relatórios de Visão Geral e Financeiro para manter um visual consistente.
Tudo em A4 retrato. Os métodos acrescentam flowables na story; `gerar()` devolve os bytes.
"""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# Paleta
NAVY = colors.HexColor("#1E1B3C")
NAVY_SOFT = colors.HexColor("#3B3766")
ORANGE = colors.HexColor("#EA580C")
PURPLE = colors.HexColor("#6D28D9")
PURPLE_SOFT = colors.HexColor("#8B5CF6")
GREEN = colors.HexColor("#15966B")
INK = colors.HexColor("#1F2937")
MUTED = colors.HexColor("#6B7280")
TRACK = colors.HexColor("#ECECEE")
BORDER = colors.HexColor("#E5E7EB")
SOFT_BG = colors.HexColor("#FAFAFA")
CALLOUT_BG = colors.HexColor("#FDF3EE")
WHITE = colors.white


def fmt_int(valor) -> str:
    try:
        return f"{int(round(float(valor))):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def fmt_brl(valor) -> str:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return "R$ 0,00"
    sinal = "-" if v < 0 else ""
    texto = f"R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{texto}"


def fmt_pct(valor) -> str:
    try:
        return f"{float(valor):.1f}%".replace(".", ",")
    except (TypeError, ValueError):
        return "0,0%"


def ratio_pct(num, den) -> float:
    return (num / den * 100) if den else 0.0


def _esc(texto) -> str:
    return escape(str(texto if texto is not None else ""))


class RichReport:
    def __init__(self, *, accent=ORANGE, banner_bg=NAVY, banner_soft=NAVY_SOFT):
        self.buffer = BytesIO()
        self.pagesize = A4
        self.left = 1.6 * cm
        self.right = 1.6 * cm
        self.top = 1.2 * cm
        self.bottom = 1.4 * cm
        self.width = self.pagesize[0] - self.left - self.right
        self.story = []
        self.accent = accent
        self.banner_bg = banner_bg
        self.banner_soft = banner_soft
        self.page_footer_left = None
        self._build_styles()

    def _build_styles(self):
        base = getSampleStyleSheet()
        self.s = {}

        def add(name, **kw):
            self.s[name] = ParagraphStyle(name, parent=base["Normal"], **kw)

        add("wordmark", fontName="Helvetica-Bold", fontSize=15, leading=17, textColor=WHITE)
        add("kicker_white", fontName="Helvetica-Bold", fontSize=7, leading=11, textColor=colors.HexColor("#A9A7C7"))
        add("title_white", fontName="Helvetica-Bold", fontSize=19, leading=22, textColor=WHITE)
        add("subtitle_white", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#C7C9DC"))
        add("meta_white", fontName="Helvetica", fontSize=8, leading=12, textColor=colors.HexColor("#C7C9DC"), alignment=2)
        add("badge", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=WHITE)
        add("section", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=self.accent)
        add("card_label", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=MUTED)
        add("card_value", fontName="Helvetica-Bold", fontSize=16, leading=19, textColor=INK)
        add("card_value_md", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=INK)
        add("card_value_sm", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK)
        add("flabel", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=INK)
        add("fsub", fontName="Helvetica", fontSize=6.5, leading=8, textColor=MUTED)
        add("pct_big", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=INK, alignment=2)
        add("pct_sub", fontName="Helvetica", fontSize=6.5, leading=8, textColor=MUTED, alignment=2)
        add("callout", fontName="Helvetica", fontSize=8.5, leading=12, textColor=INK)
        add("panel_title", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK)
        add("panel_label", fontName="Helvetica", fontSize=8.5, leading=12, textColor=INK)
        add("panel_value", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=INK, alignment=2)
        add("panel_value_sm", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=INK, alignment=2)
        add("conv_pct", fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=PURPLE)
        add("conv_label", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=INK)
        add("conv_sub", fontName="Helvetica", fontSize=7, leading=9, textColor=MUTED)
        add("note", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED)
        add("num", fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=self.accent)
        add("stat_value", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK)
        add("th", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=MUTED)
        add("th_r", fontName="Helvetica-Bold", fontSize=7, leading=9, textColor=MUTED, alignment=2)
        add("td", fontName="Helvetica", fontSize=7.5, leading=10, textColor=INK)
        add("td_r", fontName="Helvetica-Bold", fontSize=7.5, leading=10, textColor=INK, alignment=2)
        add("insight", fontName="Helvetica", fontSize=8.5, leading=12, textColor=INK)
        add("footer", fontName="Helvetica", fontSize=7.5, leading=10, textColor=MUTED)
        add("footer_r", fontName="Helvetica", fontSize=7.5, leading=10, textColor=MUTED, alignment=2)

    # ---- estrutura ----------------------------------------------------------

    def spacer(self, h=0.4):
        self.story.append(Spacer(1, h * cm))

    def page_break(self):
        self.story.append(PageBreak())

    def header_band(self, *, wordmark, kicker, title, subtitle, badge, meta_lines):
        left_cell = [
            Paragraph(_esc(wordmark), self.s["wordmark"]),
            Spacer(1, 0.15 * cm),
            Paragraph(_esc(kicker), self.s["kicker_white"]),
            Spacer(1, 0.25 * cm),
            Paragraph(_esc(title), self.s["title_white"]),
            Spacer(1, 0.1 * cm),
            Paragraph(_esc(subtitle), self.s["subtitle_white"]),
        ]
        if badge:
            pill = Table([[Paragraph(_esc(badge), self.s["badge"])]])
            pill.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), self.banner_soft),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            left_cell.append(Spacer(1, 0.3 * cm))
            left_cell.append(pill)

        right_cell = [Paragraph(linha, self.s["meta_white"]) for linha in meta_lines]

        band = Table(
            [[left_cell, right_cell]],
            colWidths=[self.width * 0.64, self.width * 0.36],
        )
        band.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.banner_bg),
                    ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                    ("VALIGN", (1, 0), (1, 0), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 18),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                    ("TOPPADDING", (0, 0), (-1, -1), 18),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
                ]
            )
        )
        self.story.append(band)
        self.spacer(0.5)

    def section(self, titulo):
        self.story.append(Paragraph(_esc(titulo).upper(), self.s["section"]))
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=3, spaceAfter=8))

    # ---- KPI cards ----------------------------------------------------------

    def kpi_cards(self, cards):
        """cards: lista de (label, valor, cor_accent)."""
        celulas = []
        for label, valor, cor in cards:
            # Valores longos (ex.: R$ 231.268,15) não cabem em 16pt na largura
            # do card — reduz a fonte para evitar quebra em duas linhas.
            n = len(str(valor))
            estilo_valor = (
                self.s["card_value"]
                if n <= 11
                else self.s["card_value_md"] if n <= 14 else self.s["card_value_sm"]
            )
            inner = Table(
                [
                    [Paragraph(_esc(label).upper(), self.s["card_label"])],
                    [Paragraph(_esc(valor), estilo_valor)],
                ]
            )
            inner.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("LINEBELOW", (0, 1), (-1, 1), 2.2, cor),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (0, 0), 9),
                        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                        ("TOPPADDING", (0, 1), (0, 1), 2),
                        ("BOTTOMPADDING", (0, 1), (0, 1), 11),
                    ]
                )
            )
            celulas.append(inner)

        self._grid_de_cards(celulas, n_por_linha=4)

    def stat_cards(self, cards, n_por_linha=5):
        """cards: lista de (label, valor). Cards compactos com fundo cinza."""
        celulas = []
        for label, valor in cards:
            inner = Table(
                [
                    [Paragraph(_esc(label).upper(), self.s["card_label"])],
                    [Paragraph(_esc(valor), self.s["stat_value"])],
                ]
            )
            inner.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 9),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                        ("TOPPADDING", (0, 0), (0, 0), 8),
                        ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                        ("TOPPADDING", (0, 1), (0, 1), 2),
                        ("BOTTOMPADDING", (0, 1), (0, 1), 9),
                    ]
                )
            )
            celulas.append(inner)

        self._grid_de_cards(celulas, n_por_linha=n_por_linha)

    def conversion_cards(self, cards, accent=None):
        """cards: lista de (pct_texto, label, sublabel). accent muda a cor do percentual."""
        pct_style = self.s["conv_pct"]
        if accent is not None:
            pct_style = ParagraphStyle("convtmp", parent=pct_style, textColor=accent)
        celulas = []
        for pct, label, sub in cards:
            inner = Table(
                [
                    [Paragraph(_esc(pct), pct_style)],
                    [Paragraph(_esc(label).upper(), self.s["conv_label"])],
                    [Paragraph(_esc(sub), self.s["conv_sub"])],
                ]
            )
            inner.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 11),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                        ("TOPPADDING", (0, 0), (0, 0), 11),
                        ("BOTTOMPADDING", (0, 0), (0, 0), 3),
                        ("TOPPADDING", (0, 1), (0, 1), 2),
                        ("BOTTOMPADDING", (0, 1), (0, 1), 1),
                        ("TOPPADDING", (0, 2), (0, 2), 1),
                        ("BOTTOMPADDING", (0, 2), (0, 2), 11),
                    ]
                )
            )
            celulas.append(inner)

        self._grid_de_cards(celulas, n_por_linha=3)

    def _grid_de_cards(self, celulas, n_por_linha):
        gap = 0.3 * cm
        cw = (self.width - gap * (n_por_linha - 1)) / n_por_linha
        # monta linhas com colunas de gap entre cards
        linha = []
        col_widths = []
        for idx, cel in enumerate(celulas):
            if idx % n_por_linha != 0:
                linha.append("")
                col_widths.append(gap)
            linha.append(cel)
            col_widths.append(cw)
        # completa a última linha
        while (len(linha) + 1) // 2 < n_por_linha and len(linha) % 2 == 1:
            linha.append("")
            col_widths.append(gap)
            linha.append("")
            col_widths.append(cw)
        tabela = Table([linha], colWidths=col_widths)
        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        self.story.append(KeepTogether(tabela))
        self.spacer(0.4)

    # ---- funil --------------------------------------------------------------

    def _bar(self, frac, valor_texto, cor):
        largura = self.width * 0.46
        altura = 0.62 * cm
        d = Drawing(largura, altura)
        d.add(Rect(0, 0, largura, altura, fillColor=TRACK, strokeColor=None))
        col_w = max(largura * max(0.0, min(frac, 1.0)), 0.85 * cm)
        d.add(Rect(0, 0, col_w, altura, fillColor=cor, strokeColor=None))
        d.add(
            String(
                col_w / 2,
                altura / 2 - 3,
                _esc(valor_texto),
                fontName="Helvetica-Bold",
                fontSize=8,
                fillColor=WHITE,
                textAnchor="middle",
            )
        )
        return d

    def funnel(self, passos):
        """passos: lista de dict {label, sub, valor, frac, pct, pct_sub, cor}."""
        linhas = []
        for p in passos:
            label_cell = [
                Paragraph(_esc(p["label"]), self.s["flabel"]),
                Paragraph(_esc(p["sub"]), self.s["fsub"]),
            ]
            pct_cell = [
                Paragraph(_esc(p["pct"]), self.s["pct_big"]),
                Paragraph(_esc(p["pct_sub"]), self.s["pct_sub"]),
            ]
            linhas.append([label_cell, self._bar(p["frac"], p["valor"], p["cor"]), pct_cell])

        tabela = Table(
            linhas,
            colWidths=[self.width * 0.30, self.width * 0.48, self.width * 0.22],
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        self.story.append(tabela)
        self.spacer(0.3)

    def bars(self, itens):
        """itens: lista de (label, valor_num, valor_texto, cor). Barras simples."""
        itens = [i for i in itens if i[1] is not None]
        if not itens:
            return
        maximo = max(abs(i[1]) for i in itens) or 1
        linhas = []
        for label, valor, texto, cor in itens:
            frac = abs(valor) / maximo
            linhas.append(
                [
                    Paragraph(_esc(label), self.s["flabel"]),
                    self._bar(frac, texto, cor),
                ]
            )
        tabela = Table(linhas, colWidths=[self.width * 0.26, self.width * 0.74])
        tabela.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        self.story.append(tabela)
        self.spacer(0.3)

    def two_bar_panels(self, left, right):
        """left/right: (titulo, itens); itens: lista de (label, valor_int, frac, cor).

        Dois painéis lado a lado com barras horizontais e o valor à direita,
        fora da barra (para contagens pequenas continuarem legíveis).
        """
        gap = 0.4 * cm
        painel_w = (self.width - gap) / 2
        bar_w = painel_w * 0.52
        bar_h = 0.38 * cm

        def barra(frac, cor):
            d = Drawing(bar_w, bar_h)
            d.add(Rect(0, 0, bar_w, bar_h, fillColor=TRACK, strokeColor=None))
            col_w = max(bar_w * max(0.0, min(frac, 1.0)), 0.16 * cm)
            d.add(Rect(0, 0, col_w, bar_h, fillColor=cor, strokeColor=None))
            return d

        def painel(titulo, itens):
            dados = [[Paragraph(_esc(titulo), self.s["panel_title"]), "", ""]]
            for label, valor, frac, cor in itens:
                dados.append(
                    [
                        Paragraph(_esc(label), self.s["panel_label"]),
                        barra(frac, cor),
                        Paragraph(_esc(fmt_int(valor)), self.s["panel_value"]),
                    ]
                )
            t = Table(
                dados,
                colWidths=[painel_w * 0.26, painel_w * 0.56, painel_w * 0.18],
            )
            t.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("SPAN", (0, 0), (2, 0)),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("LEFTPADDING", (1, 1), (1, -1), 0),
                        ("RIGHTPADDING", (1, 1), (1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ]
                )
            )
            return t

        wrapper = Table(
            [[painel(*left), "", painel(*right)]],
            colWidths=[painel_w, gap, painel_w],
        )
        wrapper.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        self.story.append(KeepTogether(wrapper))
        self.spacer(0.4)

    # ---- tabela de dados ----------------------------------------------------

    def data_table(self, headers, rows, fracs=None, aligns=None):
        """Tabela de listagem com cabeçalho repetido a cada página.

        fracs: frações da largura por coluna (normalizadas). aligns: "L"/"R".
        """
        n = len(headers)
        aligns = aligns or ["L"] * n
        fracs = fracs or [1] * n
        soma = sum(fracs)
        col_widths = [self.width * f / soma for f in fracs]

        head = [
            Paragraph(_esc(h).upper(), self.s["th_r" if aligns[i] == "R" else "th"])
            for i, h in enumerate(headers)
        ]
        corpo = [
            [
                Paragraph(_esc(cel), self.s["td_r" if aligns[i] == "R" else "td"])
                for i, cel in enumerate(linha)
            ]
            for linha in rows
        ]

        t = Table([head] + corpo, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("LINEBELOW", (0, 0), (-1, 0), 0.7, INK),
                    ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#F1F1F3")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        self.story.append(t)
        self.spacer(0.2)

    def totals_line(self, itens):
        """itens: lista de (label, valor). Linha de totais abaixo de uma tabela."""
        markup = "&nbsp;&nbsp;&nbsp;&nbsp;".join(
            f'{_esc(label)}: <b>{_esc(valor)}</b>' for label, valor in itens
        )
        self.story.append(
            HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=2, spaceAfter=6)
        )
        self.story.append(Paragraph(markup, self.s["note"]))
        self.spacer(0.3)

    # ---- caixas -------------------------------------------------------------

    def callout(self, texto, accent=ORANGE, bg=CALLOUT_BG):
        cell = Paragraph(f'<b>!</b>&nbsp;&nbsp;{_esc(texto)}', self.s["callout"])
        tabela = Table([[cell]], colWidths=[self.width])
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("LINEBEFORE", (0, 0), (0, -1), 2.5, accent),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            )
        )
        self.story.append(KeepTogether(tabela))
        self.spacer(0.4)

    def note(self, texto, accent=ORANGE):
        cell = Paragraph(_esc(texto), self.s["note"])
        tabela = Table([[cell]], colWidths=[self.width])
        estilo = [
            ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]
        if accent is not None:
            estilo.append(("LINEBEFORE", (0, 0), (0, -1), 2.5, accent))
        tabela.setStyle(TableStyle(estilo))
        self.story.append(KeepTogether(tabela))
        self.spacer(0.4)

    def box_text(self, texto):
        """Caixa branca com borda para um parágrafo corrido."""
        cell = Paragraph(_esc(texto), self.s["callout"])
        tabela = Table([[cell]], colWidths=[self.width])
        tabela.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        self.story.append(KeepTogether(tabela))
        self.spacer(0.4)

    def filters_box(self, pares):
        """pares: lista de (label, valor). Caixa cinza com 'Label: valor' em linha."""
        markup = "&nbsp;&nbsp;&nbsp;&nbsp;".join(
            f'{_esc(label)}: <b>{_esc(valor)}</b>' for label, valor in pares
        )
        cell = Paragraph(markup, self.s["callout"])
        tabela = Table([[cell]], colWidths=[self.width])
        tabela.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            )
        )
        self.story.append(KeepTogether(tabela))
        self.spacer(0.4)

    def two_panels(self, left_title, left_rows, right_title, right_rows):
        """rows: lista de (label, valor_texto) ou (label, anotacao, valor_texto)."""

        def painel(titulo, rows):
            dados = [[Paragraph(_esc(titulo), self.s["panel_title"]), ""]]
            for row in rows:
                if len(row) == 3:
                    label, anot, valor = row
                    esquerda = Paragraph(
                        f'{_esc(label)} &nbsp;<font color="#9CA3AF" size="7">{_esc(anot)}</font>',
                        self.s["panel_label"],
                    )
                else:
                    label, valor = row
                    esquerda = Paragraph(_esc(label), self.s["panel_label"])
                # Valores longos (ex.: R$ 109.104,77) não cabem em 9pt na coluna
                # do valor — reduz a fonte para evitar quebra em duas linhas.
                estilo_valor = (
                    self.s["panel_value"]
                    if len(str(valor)) <= 12
                    else self.s["panel_value_sm"]
                )
                dados.append([esquerda, Paragraph(_esc(valor), estilo_valor)])

            t = Table(dados, colWidths=[self.width * 0.30, self.width * 0.18])
            estilo = [
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("SPAN", (0, 0), (1, 0)),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 1), (-1, -2), 0.4, colors.HexColor("#F1F1F3")),
            ]
            t.setStyle(TableStyle(estilo))
            return t

        gap = 0.4 * cm
        col = (self.width - gap) / 2
        wrapper = Table(
            [[painel(left_title, left_rows), "", painel(right_title, right_rows)]],
            colWidths=[col, gap, col],
        )
        wrapper.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        self.story.append(wrapper)
        self.spacer(0.4)

    def numbered_list(self, itens, accent=ORANGE):
        """itens: lista de (lead_bold, resto)."""
        num_style = ParagraphStyle(
            "numtmp", parent=self.s["num"], textColor=accent
        )
        for idx, (lead, resto) in enumerate(itens, start=1):
            num = Paragraph(f"{idx:02d}", num_style)
            texto = Paragraph(f"<b>{_esc(lead)}</b> {_esc(resto)}", self.s["insight"])
            t = Table([[num, texto]], colWidths=[1.35 * cm, self.width - 1.35 * cm])
            t.setStyle(
                TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 11),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                        ("TOPPADDING", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                    ]
                )
            )
            self.story.append(KeepTogether(t))
            self.spacer(0.18)

    def footer_note(self, esquerda, direita):
        self.story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=6, spaceAfter=8))
        t = Table(
            [[Paragraph(_esc(esquerda), self.s["footer"]), Paragraph(_esc(direita), self.s["footer_r"])]],
            colWidths=[self.width * 0.6, self.width * 0.4],
        )
        t.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        self.story.append(t)

    # ---- build --------------------------------------------------------------

    def set_page_footer(self, texto_esquerda):
        """Ativa rodapé em todas as páginas: texto à esquerda + 'Página N de M'."""
        self.page_footer_left = texto_esquerda

    def gerar(self) -> bytes:
        doc = BaseDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            leftMargin=self.left,
            rightMargin=self.right,
            topMargin=self.top,
            bottomMargin=self.bottom,
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
        doc.addPageTemplates([PageTemplate(id="rico", frames=frame)])
        if self.page_footer_left is None:
            doc.build(self.story)
        else:
            doc.build(self.story, canvasmaker=self._footer_canvas())
        return self.buffer.getvalue()

    def _footer_canvas(self):
        """Canvas que desenha o rodapé com 'Página N de M' (precisa do total, daí o 2º passe)."""
        relatorio = self

        class FooterCanvas(canvas.Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._paginas = []

            def showPage(self):
                self._paginas.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                total = len(self._paginas)
                for estado in self._paginas:
                    self.__dict__.update(estado)
                    self.setFont("Helvetica", 7)
                    self.setFillColor(MUTED)
                    self.drawString(relatorio.left, 0.55 * cm, relatorio.page_footer_left)
                    self.drawRightString(
                        relatorio.pagesize[0] - relatorio.right,
                        0.55 * cm,
                        f"Página {self._pageNumber} de {total}",
                    )
                    super().showPage()
                super().save()

        return FooterCanvas
