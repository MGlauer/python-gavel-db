from unittest import TestCase

import gavel_db.dialects.db.structures as fol_db
from gavel.dialects.tptp.compiler import TPTPCompiler
from gavel.dialects.tptp.parser import TPTPParser


class TestProcessor(TPTPParser):
    compiler = TPTPCompiler()

    def parse(self, tree, *args, **kwargs):
        original = tree.getText()
        internal = self.visitor.visit(tree)
        if internal.logic != "thf":
            reconstructed = self.compiler.visit(internal)
            assert original.replace("(", "").replace(")", "") == reconstructed.replace(
                "(", ""
            ).replace(")", ""), (original, reconstructed)
            print(reconstructed)
        return internal


axioms = ["GRP001-0.ax"]

problems = ["ALG/ALG001-1.p", "NUN/NUN030^1.p"]


class TestParser(TestCase):

    def test_imports(self):
        pass


