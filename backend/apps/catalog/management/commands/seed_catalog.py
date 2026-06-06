"""Popular o banco com um catálogo de demonstração (acessórios mobile/tech).

Útil para apresentar o portfólio com produtos, variações, marcas e categorias
plausíveis para uma loja NuvemShop genérica do nicho de acessórios.
"""

import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Categoria, Marca, Produto, Subcategoria, Variacao


MARCAS = [
    "Anker",
    "Baseus",
    "JBL",
    "Geonav",
    "ELG",
    "i2GO",
    "iWill",
    "Edifier",
]

# (categoria, [subcategorias])
ARVORE_CATEGORIAS = [
    ("Acessórios para Celular", ["Capas", "Películas", "Suportes"]),
    ("Áudio", ["Fones Bluetooth", "Fones com Fio", "Caixas de Som"]),
    ("Carregamento & Energia", ["Cabos", "Carregadores", "Power Banks"]),
    ("Smart Home", ["Iluminação Inteligente", "Tomadas Inteligentes"]),
]

# Cada produto: (nome, descrição_longa, categoria, subcategoria, marca, [variações])
# variação: (descrição, custo_base) — preço é derivado com margem aleatória.
PRODUTOS = [
    # ── Acessórios para Celular ─────────────────────────────────────────
    (
        "Capa Anti-Impacto Galaxy S24",
        "Capa com proteção militar MIL-STD-810G, bordas reforçadas e cantos com airbag.",
        "Acessórios para Celular", "Capas", "Baseus",
        [("Transparente", "28.50"), ("Preto", "28.50"), ("Azul-marinho", "31.00")],
    ),
    (
        "Capa Silicone Líquido iPhone 15",
        "Silicone líquido com toque aveludado e forro interno em microfibra.",
        "Acessórios para Celular", "Capas", "ELG",
        [("Branco", "34.90"), ("Preto", "34.90"), ("Vermelho", "36.50")],
    ),
    (
        "Capa Anti-Impacto iPhone 15 Pro",
        "Bordas elevadas para proteção da câmera e da tela, com tratamento antiamarelamento.",
        "Acessórios para Celular", "Capas", "Geonav",
        [("Transparente", "32.00"), ("Preto Fosco", "32.00")],
    ),
    (
        "Capa Magnética Compatível com MagSafe — iPhone 15",
        "Compatível com MagSafe, encaixe magnético firme e carregamento por indução.",
        "Acessórios para Celular", "Capas", "ELG",
        [("Preto", "45.00"), ("Bege", "45.00"), ("Verde", "47.50")],
    ),
    (
        "Película 3D de Vidro iPhone 15",
        "Vidro temperado 9H com cobertura total e oleofóbico anti-impressão digital.",
        "Acessórios para Celular", "Películas", "Baseus",
        [
            ("Compatível 15", "9.80"),
            ("Compatível 15 Plus", "10.50"),
            ("Compatível 15 Pro", "11.20"),
            ("Compatível 15 Pro Max", "12.00"),
        ],
    ),
    (
        "Película 3D Galaxy S24",
        "Cobertura total, sensível ao toque, com instalação assistida.",
        "Acessórios para Celular", "Películas", "ELG",
        [("S24", "9.50"), ("S24 Plus", "10.20"), ("S24 Ultra", "11.50")],
    ),
    (
        "Suporte Veicular Magnético",
        "Suporte para painel com base magnética N52, compatível com MagSafe.",
        "Acessórios para Celular", "Suportes", "Baseus",
        [("Único", "38.00")],
    ),
    (
        "Suporte de Mesa Ajustável",
        "Suporte articulado em alumínio com base antiderrapante.",
        "Acessórios para Celular", "Suportes", "i2GO",
        [("Branco", "29.90"), ("Preto", "29.90")],
    ),
    (
        "PopSocket Universal Adesivo",
        "Apoio retrátil adesivo, compatível com qualquer modelo.",
        "Acessórios para Celular", "Suportes", "i2GO",
        [("Preto", "12.00"), ("Transparente", "12.00")],
    ),
    # ── Áudio ───────────────────────────────────────────────────────────
    (
        "Fone Bluetooth TWS Pro",
        "Cancelamento ativo de ruído (ANC), 36h de bateria com estojo e Bluetooth 5.3.",
        "Áudio", "Fones Bluetooth", "i2GO",
        [("Branco", "82.00"), ("Preto", "82.00"), ("Rosa", "85.00")],
    ),
    (
        "Fone Bluetooth Esportivo Sport",
        "Resistência a suor IPX5, ganchos auriculares e 12h de autonomia.",
        "Áudio", "Fones Bluetooth", "JBL",
        [("Preto", "115.00"), ("Azul", "115.00")],
    ),
    (
        "Headphone Over-Ear Bluetooth",
        "Drivers de 40mm, dobrável, com almofadas em couro sintético.",
        "Áudio", "Fones Bluetooth", "Edifier",
        [("Preto", "189.00"), ("Branco", "189.00")],
    ),
    (
        "Fone com Fio P2 com Microfone",
        "Drivers de 10mm, cabo trançado de 1,2m e controle remoto em linha.",
        "Áudio", "Fones com Fio", "ELG",
        [("Único", "18.50")],
    ),
    (
        "Caixa de Som Bluetooth Portátil 10W",
        "10W RMS, IPX5, 8h de bateria e função handsfree.",
        "Áudio", "Caixas de Som", "JBL",
        [("Preto", "138.00"), ("Azul", "138.00"), ("Vermelho", "142.00")],
    ),
    (
        "Caixa de Som Bluetooth Compacta 5W",
        "Som 360°, alça em corda e Bluetooth 5.2.",
        "Áudio", "Caixas de Som", "JBL",
        [("Preto", "92.00"), ("Azul", "92.00")],
    ),
    (
        "Soundbar Bluetooth para TV",
        "Soundbar estéreo 30W com entrada óptica, HDMI ARC e Bluetooth.",
        "Áudio", "Caixas de Som", "Edifier",
        [("Único", "340.00")],
    ),
    # ── Carregamento & Energia ──────────────────────────────────────────
    (
        "Cabo USB-C para Lightning PD",
        "Suporta Power Delivery, malha trançada e MFi.",
        "Carregamento & Energia", "Cabos", "Anker",
        [("1m", "32.00"), ("2m", "39.00")],
    ),
    (
        "Cabo USB-A para USB-C 3A",
        "Malha trançada reforçada, 3A de corrente e transferência a 480Mbps.",
        "Carregamento & Energia", "Cabos", "Baseus",
        [("1m", "16.00"), ("1.5m", "18.00"), ("2m", "21.00")],
    ),
    (
        "Cabo Lightning para USB-A MFi",
        "Certificado MFi, capa em TPE e conector reforçado.",
        "Carregamento & Energia", "Cabos", "Geonav",
        [("1m", "28.00"), ("2m", "35.00")],
    ),
    (
        "Cabo USB-C para USB-C 100W",
        "Suporta Power Delivery até 100W com chip de identificação.",
        "Carregamento & Energia", "Cabos", "Anker",
        [("1m", "42.00"), ("2m", "52.00")],
    ),
    (
        "Carregador USB-C 20W Power Delivery",
        "Carga rápida PD 3.0 compatível com iPhone e Android.",
        "Carregamento & Energia", "Carregadores", "Anker",
        [("Branco", "48.00"), ("Preto", "48.00")],
    ),
    (
        "Carregador USB-C 30W PD GaN",
        "Tecnologia GaN, mais compacto, ideal para tablets e ultrabooks leves.",
        "Carregamento & Energia", "Carregadores", "Baseus",
        [("Branco", "78.00")],
    ),
    (
        "Carregador USB-A 12W Tomada",
        "Saída única USB-A de 12W, ideal para reposição.",
        "Carregamento & Energia", "Carregadores", "i2GO",
        [("Branco", "19.00")],
    ),
    (
        "Power Bank 10.000mAh com USB-C PD",
        "Saída PD 20W, entrada USB-C e display digital de bateria.",
        "Carregamento & Energia", "Power Banks", "Anker",
        [("Preto", "120.00"), ("Branco", "120.00")],
    ),
    (
        "Power Bank 20.000mAh PD 22.5W",
        "Capacidade alta, suporta carga rápida bidirecional.",
        "Carregamento & Energia", "Power Banks", "Baseus",
        [("Preto", "175.00")],
    ),
    (
        "Carregador Veicular Duplo USB",
        "Duas saídas USB-A, 24W totais, com proteção contra surto.",
        "Carregamento & Energia", "Carregadores", "ELG",
        [("Único", "26.00")],
    ),
    (
        "Carregador Sem Fio Magnético 15W",
        "Compatível com MagSafe, 15W, base antiderrapante.",
        "Carregamento & Energia", "Carregadores", "Geonav",
        [("Branco", "95.00"), ("Preto", "95.00")],
    ),
    # ── Smart Home ──────────────────────────────────────────────────────
    (
        "Lâmpada Inteligente Wi-Fi RGB E27",
        "Wi-Fi, 16 milhões de cores, controle por app e voz.",
        "Smart Home", "Iluminação Inteligente", "iWill",
        [("9W Bivolt", "39.00"), ("12W Bivolt", "48.00")],
    ),
    (
        "Lâmpada Inteligente Branca E27",
        "Branco quente/frio ajustável, com agendamento via app.",
        "Smart Home", "Iluminação Inteligente", "iWill",
        [("9W Bivolt", "32.00")],
    ),
    (
        "Tomada Inteligente Wi-Fi 10A",
        "Monitoramento de consumo e agendamentos via app.",
        "Smart Home", "Tomadas Inteligentes", "iWill",
        [("10A", "55.00"), ("16A", "72.00")],
    ),
    (
        "Sensor de Presença Wi-Fi",
        "Sensor PIR de presença, integrável a rotinas Alexa e Google.",
        "Smart Home", "Tomadas Inteligentes", "iWill",
        [("Único", "68.00")],
    ),
]


class Command(BaseCommand):
    help = "Popula o catálogo com produtos, variações, marcas e categorias de exemplo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga todo o catálogo (produtos/variações/marcas/categorias) antes de popular.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        if options["limpar"]:
            v = Variacao.objects.all().delete()
            p = Produto.objects.all().delete()
            sc = Subcategoria.objects.all().delete()
            c = Categoria.objects.all().delete()
            m = Marca.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f"Removidos: {v[0]} variações, {p[0]} produtos, "
                f"{sc[0]} subcategorias, {c[0]} categorias, {m[0]} marcas."
            ))

        marcas = {}
        for nome in MARCAS:
            obj, _ = Marca.objects.get_or_create(
                slug=slugify(nome),
                defaults={"nome": nome},
            )
            marcas[nome] = obj

        categorias = {}
        subcategorias = {}
        for nome_cat, nomes_sub in ARVORE_CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                slug=slugify(nome_cat),
                defaults={"nome": nome_cat},
            )
            categorias[nome_cat] = cat
            for nome_sub in nomes_sub:
                sub, _ = Subcategoria.objects.get_or_create(
                    categoria=cat,
                    slug=slugify(nome_sub),
                    defaults={"nome": nome_sub},
                )
                subcategorias[(nome_cat, nome_sub)] = sub

        produtos_criados = 0
        variacoes_criadas = 0
        sku_seq = 1000

        for nome, descricao, cat_nome, sub_nome, marca_nome, variacoes in PRODUTOS:
            produto, criado = Produto.objects.get_or_create(
                nome_site=nome,
                defaults={
                    "nome_gestaoclick": nome[:60],
                    "descricao_produto_site": descricao,
                    "descricao_produto_gestaoclick": descricao,
                    "marca": marcas[marca_nome],
                    "subcategoria": subcategorias[(cat_nome, sub_nome)],
                },
            )
            if criado:
                produtos_criados += 1

            for desc_var, custo_str in variacoes:
                custo = Decimal(custo_str)
                # Margem entre 70% e 130% sobre o custo (loja física)
                margem_loja = Decimal(str(round(random.uniform(0.70, 1.30), 2)))
                preco_loja = (custo * (Decimal("1") + margem_loja)).quantize(Decimal("0.01"))
                # Site geralmente ~10% mais barato que loja física
                preco_site = (preco_loja * Decimal("0.90")).quantize(Decimal("0.01"))
                # 30% das variações têm preço promocional (~12% off do site)
                preco_promo = None
                if random.random() < 0.30:
                    preco_promo = (preco_site * Decimal("0.88")).quantize(Decimal("0.01"))

                sku = f"SKU-{sku_seq:05d}"
                gestao_id = f"GC-{sku_seq:05d}"
                ean = self._gerar_ean13(sku_seq)
                sku_seq += 1

                status_site = "ATIVO" if random.random() < 0.92 else "INATIVO"
                status_int = "ATIVO" if random.random() < 0.95 else "INATIVO"

                _, criado_var = Variacao.objects.get_or_create(
                    produto=produto,
                    descricao=desc_var,
                    defaults={
                        "sku_nuvemshop": sku,
                        "id_gestaoclick": gestao_id,
                        "codigo_barras": ean,
                        "custo": custo,
                        "preco_loja": preco_loja,
                        "preco_site": preco_site,
                        "preco_promocional": preco_promo,
                        "status_nuvemshop": status_site,
                        "status_integracao": status_int,
                    },
                )
                if criado_var:
                    variacoes_criadas += 1

        self.stdout.write(self.style.SUCCESS(
            f"{produtos_criados} produtos e {variacoes_criadas} variações criados. "
            f"Marcas: {len(marcas)} · Categorias: {len(categorias)} · "
            f"Subcategorias: {len(subcategorias)}."
        ))

    @staticmethod
    def _gerar_ean13(seq: int) -> str:
        base = f"789{seq:09d}"[:12]
        soma = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(base))
        dv = (10 - soma % 10) % 10
        return base + str(dv)
