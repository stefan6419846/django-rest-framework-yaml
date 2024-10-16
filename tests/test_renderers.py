# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from decimal import Decimal
from io import BytesIO
from uuid import UUID

from django.test import TestCase

from rest_framework_yaml.compat import ErrorDetail, Hyperlink
from rest_framework_yaml.parsers import YAMLParser
from rest_framework_yaml.renderers import YAMLRenderer


class YAMLRendererTests(TestCase):
    """
    Tests specific to the YAML Renderer
    """

    def test_render(self):
        """
        Test basic YAML rendering.
        """
        _yaml_repr = "foo:\n- bar\n- baz\n"

        obj = {"foo": ["bar", "baz"]}

        renderer = YAMLRenderer()
        content = renderer.render(obj, "application/yaml")

        self.assertEqual(content.decode("utf-8"), _yaml_repr)

    def test_render_and_parse(self):
        """
        Test rendering and then parsing returns the original object.
        IE obj -> render -> parse -> obj.
        """
        obj = {"foo": ["bar", "baz"]}

        renderer = YAMLRenderer()
        parser = YAMLParser()

        content = renderer.render(obj, "application/yaml")
        data = parser.parse(BytesIO(content))
        self.assertEqual(obj, data)

    def test_render_decimal(self):
        """
        Test YAML decimal rendering.
        """
        renderer = YAMLRenderer()
        content = renderer.render(
            {"field": Decimal("111.2")}, "application/yaml"
        )
        self.assertYAMLContains(content.decode("utf-8"), "field: '111.2'")

    @unittest.skipUnless(Hyperlink, "Hyperlink is undefined")
    def test_render_hyperlink(self):
        """
        Test YAML Hyperlink rendering.
        """
        renderer = YAMLRenderer()
        content = renderer.render(
            {"field": Hyperlink("http://pépé.com?great-answer=42", "test")},
            "application/yaml",
        )
        self.assertYAMLContains(
            content.decode("utf-8"), "field: http://pépé.com?great-answer=42"
        )

    def test_render_uuid(self):
        """
        Test YAML UUID rendering.
        """
        renderer = YAMLRenderer()
        content = renderer.render(
            {"field": UUID(int=42)},
            "application/yaml",
        )
        self.assertYAMLContains(
            content.decode("utf-8"), f"field: {UUID(int=42)!s}"
        )

    @unittest.skipUnless(ErrorDetail, "ErrorDetail is undefined")
    def test_render_error_detail(self):
        renderer = YAMLRenderer()
        content = renderer.render(
            {"field": ErrorDetail("Some ErrorDetail test message")},
            "application/yaml",
        )
        self.assertYAMLContains(
            content.decode("utf-8"), "field: Some ErrorDetail test message"
        )

    def assertYAMLContains(self, content, string):
        self.assertTrue(string in content, "%r not in %r" % (string, content))

    def test_proper_encoding(self):
        _yaml_repr = "countries:\n- United Kingdom\n- France\n- España"
        obj = {"countries": ["United Kingdom", "France", "España"]}
        renderer = YAMLRenderer()
        content = renderer.render(obj, "application/yaml")
        self.assertEqual(content.strip(), _yaml_repr.encode("utf-8"))

    def test_render_none_type(self):
        """
        Test YAML rendering with None type
        """
        _yaml_repr = "foo:\n- bar\n- baz\nnull:\n- null\n"

        obj = {"foo": ["bar", "baz"], None: [None]}

        renderer = YAMLRenderer()
        content = renderer.render(obj, "application/yaml")

        self.assertEqual(_yaml_repr, content.decode("utf-8"))
