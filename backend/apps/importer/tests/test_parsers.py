from decimal import Decimal
from django.test import TestCase

from importer.services.parsers import (
    is_empty, parse_decimal, parse_sku, parse_status, parse_string,
)


class ParsersTestCase(TestCase):
    def test_is_empty(self):
        self.assertTrue(is_empty(None))
        self.assertTrue(is_empty(""))
        self.assertTrue(is_empty("   "))
        self.assertTrue(is_empty("______"))
        self.assertFalse(is_empty("ABC"))
        self.assertFalse(is_empty("0"))

    def test_parse_sku_string(self):
        self.assertEqual(parse_sku("20099680632090001"), "20099680632090001")

    def test_parse_sku_notacao_cientifica(self):
        self.assertEqual(parse_sku("2.001795505303E12"), "2001795505303")
        self.assertEqual(parse_sku(2.001795505303e12), "2001795505303")

    def test_parse_sku_vazio(self):
        self.assertEqual(parse_sku("______"), "")

    def test_parse_decimal(self):
        self.assertEqual(parse_decimal(68.41), Decimal("68.41"))
        self.assertEqual(parse_decimal("189.00"), Decimal("189.00"))
        self.assertIsNone(parse_decimal("______"))
        self.assertIsNone(parse_decimal(""))

    def test_parse_status(self):
        self.assertEqual(parse_status("ATIVO"), "ATIVO")
        self.assertEqual(parse_status("inativo"), "INATIVO")
        self.assertEqual(parse_status("______"), "ATIVO")

    def test_parse_string(self):
        self.assertEqual(parse_string("  hello  "), "hello")
        self.assertEqual(parse_string("______"), "")
        self.assertEqual(parse_string(None), "")
