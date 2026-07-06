"""Popular o banco com um catálogo de demonstração por nicho.

Nichos disponíveis: acessórios mobile/tech (padrão) e supermercado.
Útil para apresentar o portfólio com produtos, variações, marcas e categorias
plausíveis para uma loja NuvemShop do ramo da empresa.
"""

import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from accounts.models import Empresa
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

MARCAS_SUPERMERCADO = [
    "Nestlé",
    "Coca-Cola",
    "Italac",
    "Camil",
    "Seara",
    "Sadia",
    "OMO",
    "Ypê",
    "Colgate",
    "Gallo",
]

ARVORE_CATEGORIAS_SUPERMERCADO = [
    ("Mercearia", ["Grãos & Cereais", "Massas & Molhos", "Óleos & Azeites", "Biscoitos & Doces"]),
    ("Bebidas", ["Refrigerantes", "Sucos & Chás", "Águas"]),
    ("Frios & Laticínios", ["Leites", "Queijos & Frios", "Carnes & Congelados", "Iogurtes"]),
    ("Limpeza", ["Roupas", "Cozinha & Casa"]),
    ("Higiene & Beleza", ["Higiene Bucal", "Cuidados Corporais"]),
]

PRODUTOS_SUPERMERCADO = [
    # ── Mercearia ───────────────────────────────────────────────────────
    (
        "Arroz Branco Tipo 1",
        "Arroz branco polido tipo 1, grãos longos e soltos após o cozimento.",
        "Mercearia", "Grãos & Cereais", "Camil",
        [("1kg", "4.20"), ("5kg", "19.80")],
    ),
    (
        "Feijão Carioca Tipo 1",
        "Feijão carioca selecionado, cozimento rápido e caldo encorpado.",
        "Mercearia", "Grãos & Cereais", "Camil",
        [("1kg", "6.50")],
    ),
    (
        "Açúcar Refinado",
        "Açúcar refinado de dissolução rápida, ideal para o dia a dia.",
        "Mercearia", "Grãos & Cereais", "Camil",
        [("1kg", "3.90")],
    ),
    (
        "Aveia em Flocos Finos",
        "Aveia em flocos finos, fonte de fibras, para mingaus e receitas.",
        "Mercearia", "Grãos & Cereais", "Nestlé",
        [("200g", "4.10"), ("500g", "8.90")],
    ),
    (
        "Macarrão Espaguete nº 8",
        "Massa de sêmola com ovos, cozimento al dente em 8 minutos.",
        "Mercearia", "Massas & Molhos", "Camil",
        [("500g", "2.80")],
    ),
    (
        "Molho de Tomate Tradicional",
        "Molho de tomate pronto, receita tradicional sem conservantes.",
        "Mercearia", "Massas & Molhos", "Nestlé",
        [("300g", "2.40"), ("Sachê 340g", "2.10")],
    ),
    (
        "Azeite de Oliva Extra Virgem",
        "Azeite extra virgem, acidez máxima 0,5%, prensado a frio.",
        "Mercearia", "Óleos & Azeites", "Gallo",
        [("250ml", "18.50"), ("500ml", "32.00")],
    ),
    (
        "Óleo de Soja",
        "Óleo de soja refinado, rico em ômega 6 e vitamina E.",
        "Mercearia", "Óleos & Azeites", "Camil",
        [("900ml", "5.60")],
    ),
    (
        "Biscoito Recheado Chocolate",
        "Biscoito recheado sabor chocolate, pacote individual.",
        "Mercearia", "Biscoitos & Doces", "Nestlé",
        [("140g", "2.20")],
    ),
    (
        "Chocolate ao Leite",
        "Chocolate ao leite cremoso, tablete tradicional.",
        "Mercearia", "Biscoitos & Doces", "Nestlé",
        [("80g", "4.80"), ("165g", "8.90")],
    ),
    # ── Bebidas ─────────────────────────────────────────────────────────
    (
        "Refrigerante Cola",
        "Refrigerante sabor cola, gelado combina com qualquer refeição.",
        "Bebidas", "Refrigerantes", "Coca-Cola",
        [("Lata 350ml", "2.60"), ("600ml", "3.80"), ("2L", "6.90")],
    ),
    (
        "Refrigerante Guaraná",
        "Refrigerante sabor guaraná, leve e refrescante.",
        "Bebidas", "Refrigerantes", "Coca-Cola",
        [("Lata 350ml", "2.10"), ("2L", "4.50")],
    ),
    (
        "Suco de Laranja Integral",
        "Suco 100% fruta, sem adição de açúcar e sem conservantes.",
        "Bebidas", "Sucos & Chás", "Coca-Cola",
        [("1L", "6.80")],
    ),
    (
        "Néctar de Uva",
        "Néctar de uva com polpa selecionada, pronto para beber.",
        "Bebidas", "Sucos & Chás", "Coca-Cola",
        [("1L", "5.90")],
    ),
    (
        "Água Mineral sem Gás",
        "Água mineral natural de fonte, sem gás.",
        "Bebidas", "Águas", "Coca-Cola",
        [("500ml", "0.90"), ("1,5L", "1.80")],
    ),
    # ── Frios & Laticínios ──────────────────────────────────────────────
    (
        "Leite Integral UHT",
        "Leite integral longa vida, fonte de cálcio.",
        "Frios & Laticínios", "Leites", "Italac",
        [("1L", "3.95")],
    ),
    (
        "Leite Desnatado UHT",
        "Leite desnatado longa vida, menos gordura no dia a dia.",
        "Frios & Laticínios", "Leites", "Italac",
        [("1L", "3.95")],
    ),
    (
        "Creme de Leite",
        "Creme de leite UHT para receitas doces e salgadas.",
        "Frios & Laticínios", "Leites", "Italac",
        [("200g", "2.30")],
    ),
    (
        "Leite Condensado",
        "Leite condensado tradicional para sobremesas.",
        "Frios & Laticínios", "Leites", "Italac",
        [("395g", "5.40")],
    ),
    (
        "Queijo Mussarela Fatiado",
        "Mussarela fatiada, embalagem com atmosfera protetora.",
        "Frios & Laticínios", "Queijos & Frios", "Italac",
        [("150g", "6.20"), ("500g", "18.90")],
    ),
    (
        "Presunto Cozido Fatiado",
        "Presunto cozido sem capa de gordura, fatiado.",
        "Frios & Laticínios", "Queijos & Frios", "Sadia",
        [("200g", "5.80")],
    ),
    (
        "Linguiça Toscana",
        "Linguiça toscana suína para churrasco.",
        "Frios & Laticínios", "Carnes & Congelados", "Seara",
        [("700g", "14.20")],
    ),
    (
        "Peito de Frango Congelado",
        "Peito de frango congelado sem osso, bandeja.",
        "Frios & Laticínios", "Carnes & Congelados", "Sadia",
        [("1kg", "13.50")],
    ),
    (
        "Salsicha Hot Dog",
        "Salsicha tipo hot dog, pacote congelado.",
        "Frios & Laticínios", "Carnes & Congelados", "Seara",
        [("500g", "7.90")],
    ),
    (
        "Iogurte Natural Integral",
        "Iogurte natural integral, sem corantes e sem aromatizantes.",
        "Frios & Laticínios", "Iogurtes", "Nestlé",
        [("170g", "2.40")],
    ),
    # ── Limpeza ─────────────────────────────────────────────────────────
    (
        "Sabão em Pó Lavagem Perfeita",
        "Sabão em pó com remoção de manchas em uma lavagem.",
        "Limpeza", "Roupas", "OMO",
        [("800g", "9.80"), ("1,6kg", "18.50")],
    ),
    (
        "Amaciante Concentrado",
        "Amaciante concentrado, perfume de longa duração.",
        "Limpeza", "Roupas", "Ypê",
        [("500ml", "6.40")],
    ),
    (
        "Detergente Neutro",
        "Detergente líquido neutro, testado dermatologicamente.",
        "Limpeza", "Cozinha & Casa", "Ypê",
        [("500ml", "1.85")],
    ),
    (
        "Água Sanitária",
        "Água sanitária para limpeza pesada e desinfecção.",
        "Limpeza", "Cozinha & Casa", "Ypê",
        [("1L", "2.70"), ("2L", "4.90")],
    ),
    # ── Higiene & Beleza ────────────────────────────────────────────────
    (
        "Creme Dental Proteção Total",
        "Creme dental com flúor, proteção anticáries por 12 horas.",
        "Higiene & Beleza", "Higiene Bucal", "Colgate",
        [("90g", "3.20"), ("180g", "5.60")],
    ),
    (
        "Escova de Dentes Macia",
        "Escova dental com cerdas macias e cabo emborrachado.",
        "Higiene & Beleza", "Higiene Bucal", "Colgate",
        [("Única", "4.10")],
    ),
    (
        "Sabonete em Barra Neutro",
        "Sabonete em barra de uso diário, fragrância suave.",
        "Higiene & Beleza", "Cuidados Corporais", "Colgate",
        [("85g", "1.60")],
    ),
]

# Cada nicho define o sortimento e a política de margem típica do ramo.
NICHOS = {
    "tech": {
        "marcas": MARCAS,
        "arvore": ARVORE_CATEGORIAS,
        "produtos": PRODUTOS,
        # Margem entre 70% e 130% sobre o custo (loja física)
        "margem_loja": (0.70, 1.30),
        # Site geralmente ~10% mais barato que loja física
        "fator_site": Decimal("0.90"),
    },
    "supermercado": {
        "marcas": MARCAS_SUPERMERCADO,
        "arvore": ARVORE_CATEGORIAS_SUPERMERCADO,
        "produtos": PRODUTOS_SUPERMERCADO,
        # Varejo alimentar trabalha com margens bem menores
        "margem_loja": (0.18, 0.45),
        # Preço do site praticamente igual ao da gôndola
        "fator_site": Decimal("0.97"),
    },
}


class Command(BaseCommand):
    help = "Popula o catálogo com produtos, variações, marcas e categorias de exemplo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--empresa",
            required=True,
            help="ID ou nome da empresa dona do catálogo.",
        )
        parser.add_argument(
            "--nicho",
            choices=sorted(NICHOS.keys()),
            default="tech",
            help="Sortimento de produtos a gerar (padrão: tech).",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga o catálogo da empresa (produtos/variações/marcas/categorias) antes de popular.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        empresa = self._resolver_empresa(options["empresa"])
        if empresa is None:
            return
        nicho = NICHOS[options["nicho"]]
        self.stdout.write(
            f"Empresa: {empresa.nome} (id={empresa.pk}) · nicho: {options['nicho']}"
        )

        # Determinístico, mas diferente por empresa — evita dados idênticos entre tenants
        random.seed(42 + empresa.pk)

        if options["limpar"]:
            v = Variacao.objects.filter(produto__empresa=empresa).delete()
            p = Produto.objects.filter(empresa=empresa).delete()
            sc = Subcategoria.objects.filter(empresa=empresa).delete()
            c = Categoria.objects.filter(empresa=empresa).delete()
            m = Marca.objects.filter(empresa=empresa).delete()
            self.stdout.write(self.style.WARNING(
                f"Removidos: {v[0]} variações, {p[0]} produtos, "
                f"{sc[0]} subcategorias, {c[0]} categorias, {m[0]} marcas."
            ))

        marcas = {}
        for nome in nicho["marcas"]:
            obj, _ = Marca.objects.get_or_create(
                empresa=empresa,
                slug=slugify(nome),
                defaults={"nome": nome},
            )
            marcas[nome] = obj

        categorias = {}
        subcategorias = {}
        for nome_cat, nomes_sub in nicho["arvore"]:
            cat, _ = Categoria.objects.get_or_create(
                empresa=empresa,
                slug=slugify(nome_cat),
                defaults={"nome": nome_cat},
            )
            categorias[nome_cat] = cat
            for nome_sub in nomes_sub:
                sub, _ = Subcategoria.objects.get_or_create(
                    empresa=empresa,
                    categoria=cat,
                    slug=slugify(nome_sub),
                    defaults={"nome": nome_sub},
                )
                subcategorias[(nome_cat, nome_sub)] = sub

        produtos_criados = 0
        variacoes_criadas = 0
        sku_seq = 1000 * empresa.pk

        for nome, descricao, cat_nome, sub_nome, marca_nome, variacoes in nicho["produtos"]:
            produto, criado = Produto.objects.get_or_create(
                empresa=empresa,
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
                margem_min, margem_max = nicho["margem_loja"]
                margem_loja = Decimal(str(round(random.uniform(margem_min, margem_max), 2)))
                preco_loja = (custo * (Decimal("1") + margem_loja)).quantize(Decimal("0.01"))
                preco_site = (preco_loja * nicho["fator_site"]).quantize(Decimal("0.01"))
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

    def _resolver_empresa(self, ref: str) -> Empresa | None:
        empresa = Empresa.objects.filter(pk=ref).first() if str(ref).isdigit() else None
        if empresa is None:
            empresa = Empresa.objects.filter(nome__iexact=ref).first()
        if empresa is None:
            candidatas = list(Empresa.objects.filter(nome__icontains=ref)[:2])
            if len(candidatas) > 1:
                self.stdout.write(self.style.ERROR(
                    f"Mais de uma empresa contém '{ref}'; use o ID."
                ))
                return None
            empresa = candidatas[0] if candidatas else None
        if empresa is None:
            self.stdout.write(self.style.ERROR(f"Empresa '{ref}' não encontrada."))
        return empresa

    @staticmethod
    def _gerar_ean13(seq: int) -> str:
        base = f"789{seq:09d}"[:12]
        soma = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(base))
        dv = (10 - soma % 10) % 10
        return base + str(dv)
