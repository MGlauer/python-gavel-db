import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from gavel_db.dialects.db.connection import with_session, get_or_create, get_or_None
from gavel_db.dialects.db.compiler import JSONCompiler
from gavel.logic import problem as tptp_problem
from gavel.dialects.base.parser import ProofParser
from gavel.dialects.tptp.parser import _load_solution, parse_solution, TPTPProblemParser
from gavel.config import settings as settings
import os
import multiprocessing as mp

Base = declarative_base()


class Source(Base):
    __tablename__ = "source"
    id = sqla.Column(sqla.Integer, primary_key=True)
    path = sqla.Column(sqla.String, unique=True)
    complete = sqla.Column(sqla.Boolean, default=False)


class Formula(Base):
    __tablename__ = "formula"
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Text)
    source_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id), nullable=False)
    source = relationship(Source)
    logic = sqla.VARCHAR(4)
    json = sqla.Column(sqla.JSON)
    problem_id = sqla.Column(sqla.Integer, sqla.ForeignKey('problem.id'))
    conjecture_in_problem = relationship('Problem', back_populates="conjectures")


association_premises = sqla.Table(
    "association",
    Base.metadata,
    sqla.Column("left_id", sqla.Integer, sqla.ForeignKey("problem.id"), nullable=False),
    sqla.Column(
        "right_id", sqla.Integer, sqla.ForeignKey("formula.id"), nullable=False
    ),
)


association_problem_imports = sqla.Table(
    "problem_imports",
    Base.metadata,
    sqla.Column("problem_id", sqla.Integer, sqla.ForeignKey("problem.id"), nullable=False),
    sqla.Column(
        "source_id", sqla.Integer, sqla.ForeignKey("source.id"), nullable=False
    ),
)


class Problem(Base):
    __tablename__ = "problem"
    id = sqla.Column(sqla.Integer, primary_key=True)
    domain = sqla.Column(sqla.VARCHAR(4))
    source = relationship(Source)
    source_id = sqla.Column(sqla.Integer, sqla.ForeignKey(Source.id), nullable=False, unique=True)
    conjectures = relationship(Formula, back_populates="conjecture_in_problem")
    imports = relationship(Source, secondary=association_problem_imports)
    original_premises = relationship(Formula, secondary=association_premises)

    def create_problem_file(self, file):
        for premise in self.premises:
            file.write(premise.original)

    def all_premises(self, session):
        for p in self.original_premises:
            yield p
        for p in session.query(Formula).filter(Formula.source_id.in_([s.id for s in self.imports])):
            yield p


association_used_premises = sqla.Table(
    "solution_premises",
    Base.metadata,
    sqla.Column("solution_id", sqla.Integer, sqla.ForeignKey("solution.id"), nullable=False),
    sqla.Column(
        "formula_id", sqla.Integer, sqla.ForeignKey("formula.id"), nullable=False
    ),
)

class Solution(Base):
    __tablename__ = "solution"
    id = sqla.Column(sqla.Integer, primary_key=True)
    problem_id = sqla.Column(sqla.Integer, sqla.ForeignKey("problem.id"), nullable=False)
    problem = relationship(Problem)
    premises = relationship(Formula, secondary=association_used_premises)


def store_formula(
    source_name,
    struc: tptp_problem.AnnotatedFormula,
    session=None,
    source=None,
    skip_existence_check=False,
):
    created = skip_existence_check
    structure = None
    compiler = JSONCompiler()
    if source is None:
        source, created = get_or_create(session, Source, path=source_name)
    # If the source object was already in the database, the formula might
    # already be present, too. Check that before storing a second copy
    if not created and not skip_existence_check:
        structure = get_or_None(session, Formula, name=struc.name, source=source)
    if structure is None:
        structure = Formula(
            json=compiler.visit(struc.formula),
            name=compiler.visit(struc.name),
            logic=compiler.visit(struc.logic),
        )
        structure.source = source
    return structure


@with_session
def store_problem(parser, problem_path: str, session=None):
    fname = os.path.basename(problem_path)
    if (
        "=" not in fname
        and "^" not in fname
        and "_" not in fname
        and fname.endswith(".p")
    ):
        source_name = problem_path
        source, new_source = get_or_create(session, Source, path=source_name)
        if new_source:
            print(problem_path)
            print("Parse")
            imports = []
            problem = parser.parse_from_file(problem_path)
            print("Build database model")
            # A problem is created for each individual conjecture.
            # They all share premises and imports, so we have to import
            # those only once
            original_premises = [
                store_formula(source_name, premise, session=session, source=source, skip_existence_check=True)
                for premise in problem.premises
            ]
            conjectures = [store_formula(source_name, c, session=session, source=source) for c in problem.conjectures]
            if not imports:
                for imp in problem.imports:
                    sub, new_source = get_or_create(session, Source, path=imp.path)
                    if new_source:
                        store_file(
                            os.path.join(settings.TPTP_ROOT, imp.path),
                            parser.logic_parser,
                            JSONCompiler(),
                            session=session,
                        )
                    imports.append(sub)
            p = Problem(
                source=source,
                original_premises=original_premises,
                conjectures=conjectures,
                imports=imports,
            )
            print("Add")
            session.add(p)
        else:
            print("Skipping", problem_path)

@with_session
def store_all(path, parser, processor, compiler, **kwargs):
    if os.path.isdir(path):
        for sub_path in os.listdir(path):
            sub_path = os.path.join(path, sub_path)
            if os.path.isfile(sub_path):
                processor(parser, sub_path, **kwargs)
            else:
                store_all(sub_path, parser, processor, compiler, **kwargs)
    elif os.path.isfile(path):
        processor(parser, path, **kwargs)


def store_file(path, parser, compiler, session=None):
    fname = os.path.basename(path)
    if (
        "=" not in fname
        and "^" not in fname
        and "_" not in fname
        and fname[-2:] == ".p"
    ):
        source, created = get_or_create(session, Source, path=path)
        if not source.complete:
            i = 0
            for struc in parser.parse_from_file(path):
                i += 1
                store_formula(
                    path,
                    struc,
                    session=session,
                    source=source,
                    skip_existence_check=created,
                )
            mark_source_complete(path, session=session)
        else:
            skip = True
            skip_reason = "Already complete"
    else:
        skip = True
        skip_reason = "Not supported"


def mark_source_complete(source, session=None):
    session.query(Source).filter_by(path=source).update({"complete": True})


def is_source_complete(source, session=None):
    source_obj = get_or_None(session, Source, path=source)
    if source_obj is None:
        return False
    return source_obj.complete


@with_session
def store_all_solutions(proof_parser: ProofParser, session=None):
    for problem, sid in session.query(Problem, Solution.id).outerjoin(Solution).filter(Solution.id.is_(None), Problem.id > 5823):
        pname = os.path.basename(problem.source.path)[:-2]
        print(problem.id, pname)
        domain = pname[:3]
        if domain != "SYN":
            solution = parse_solution(_load_solution(domain, pname))
            if solution is not None:
                print("Store solution")
                axiom_names = [ax.name for ax in solution.used_axioms]
                available_premises = list(problem.all_premises(session))
                s = Solution(problem=problem, premises=[a for a in available_premises if a.name in axiom_names])
                session.add(s)
            else:
                print("No solution found")
