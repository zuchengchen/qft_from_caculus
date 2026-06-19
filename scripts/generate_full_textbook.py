#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTER_DIR = ROOT / "chaptersfull"
APPENDIX_DIR = ROOT / "appendicesfull"


def tex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "", text.lower())
    return cleaned[:36] or "chapter"


def clean_tex_text(text: str) -> str:
    """Repair Python string escapes that are meaningful in TeX prose."""
    return (
        text.replace("\x08", r"\b")
        .replace("\x0c", r"\f")
        .replace("\t", r"\t")
        .replace("\r", r"\r")
    )


def contextualize_paragraphs(text: str, context: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text.strip())
    contextualized: list[str] = []
    endings = [
        "In {context}, the useful habit is to name the object, the operation, and the assumption before using the compact notation.",
        r"For {context}, that bookkeeping is deliberately modest, but it is what later keeps signs, factors of \(2\pi\), and normalization constants from turning into guesses.",
        "Read in the setting of {context}, the line is a check on the calculation rather than an invitation to memorize another rule.",
        "The same step will look more abstract later; in {context} it is kept close to the finite calculation so the limiting move remains visible.",
        "At this point in {context}, it is worth asking what would fail if the boundary condition, normalization, or symmetry assumption were changed.",
        "In {context}, the calculation is meant to leave a trail from an ordinary derivative, sum, matrix product, or Gaussian integral to the field-theory formula.",
    ]
    for idx, para in enumerate(paragraphs):
        compact = re.sub(r"\s+", " ", para.strip())
        if len(compact.split()) >= 25:
            ending = endings[idx % len(endings)].format(context=context)
            contextualized.append(f"{para.strip()}  {ending}")
        else:
            contextualized.append(para.strip())
    return "\n\n".join(contextualized)


PARTS = [
    (
        "Calculus, Space, and Mathematical Language",
        [
            ("The Calculus Starting Point", "limits, derivatives, integrals, approximation, dimensions"),
            ("Vectors, Coordinates, and Geometry", "vectors, coordinates, dot products, bases, length"),
            ("Multivariable Calculus for Fields", "gradients, divergence, curl, Jacobians, flux"),
            ("Complex Numbers and Oscillation", "complex numbers, phases, exponentials, rotations"),
            ("Linear Algebra from Systems of Equations", "matrices, linear maps, elimination, determinants"),
            ("Eigenvectors, Inner Products, and Hilbert Space", "eigenvalues, orthogonality, norms, completeness"),
            ("Fourier Analysis and Distributions", "Fourier series, transforms, delta functions, test functions"),
        ],
    ),
    (
        "Classical Mechanics and Classical Fields",
        [
            ("Differential Equations and Green Functions", "ODEs, PDEs, boundary data, Green functions"),
            ("Variational Calculus from First Principles", "functionals, variations, boundary terms, Euler equations"),
            ("Lagrangian Mechanics", "actions, generalized coordinates, constraints, energy"),
            ("Hamiltonian Mechanics and Poisson Brackets", "momenta, phase space, Hamilton equations, brackets"),
            ("Coupled Oscillators and the Continuum Limit", "normal modes, lattices, waves, continuum limit"),
            ("Classical Scalar Field Theory", "fields, densities, Klein-Gordon equation, energy"),
            ("Noether's Theorem and Stress Energy", "symmetries, currents, charges, stress-energy"),
        ],
    ),
    (
        "Relativity and Quantum Mechanics Built for Fields",
        [
            ("Special Relativity from the Interval", "spacetime, Lorentz transformations, invariant intervals"),
            ("Relativistic Notation and Tensors", "indices, metric, four-vectors, tensor equations"),
            ("Maxwell Theory from Potentials", "electromagnetism, potentials, gauge redundancy, fields"),
            ("Quantum States and Probability Amplitudes", "states, amplitudes, probabilities, bases"),
            ("Operators, Measurements, and Commutators", "observables, Hermitian operators, commutators"),
            ("The Harmonic Oscillator in Full Detail", "ladder operators, spectra, wavefunctions, zero-point energy"),
            ("Angular Momentum, Spin, and Identical Particles", "rotations, spin, symmetrization, fermions"),
        ],
    ),
    (
        "Free Quantum Fields",
        [
            ("Time Evolution and Perturbation in Quantum Mechanics", "interaction picture, Dyson series, transitions"),
            ("Path Integrals in Quantum Mechanics", "time slicing, Gaussian integration, stationary phase"),
            ("The Scalar Field as Infinite Oscillators", "modes, oscillators, dispersion, continuum"),
            ("Canonical Quantization of the Klein-Gordon Field", "commutators, fields, conjugate momenta"),
            ("Fock Space and Particle Interpretation", "vacuum, particles, number operators, normalization"),
            ("Propagators and Microcausality", "two-point functions, commutators, causality, poles"),
            ("Complex Scalar Fields and Conserved Charge", "charge, antiparticles, complex fields, currents"),
        ],
    ),
    (
        "Interactions and Perturbative Quantum Field Theory",
        [
            ("Generating Functionals", "sources, functional derivatives, connected functions"),
            ("Wick's Theorem", "contractions, normal ordering, Gaussian moments"),
            ("Interacting Scalar Theory", "phi-fourth theory, vertices, correlation functions"),
            ("Feynman Rules in Position and Momentum Space", "propagators, vertices, conservation, diagrams"),
            ("Scattering, Phase Space, and Cross Sections", "S-matrix, rates, phase space, normalization"),
            ("LSZ Reduction", "external legs, residues, asymptotic states, amplitudes"),
            ("Loops, Self-Energy, and Vertex Corrections", "loop integrals, self-energy, vertex functions"),
        ],
    ),
    (
        "Renormalization and Effective Field Theory",
        [
            ("Cutoff Regularization", "cutoffs, divergences, short distances, counterterms"),
            ("Dimensional Regularization", "dimensions, gamma functions, poles, minimal subtraction"),
            ("Renormalization Conditions and Counterterms", "measured parameters, pole masses, schemes"),
            ("Running Couplings and the Renormalization Group", "beta functions, scale dependence, flow"),
            ("Effective Action and One-Particle-Irreducible Functions", "Legendre transforms, 1PI functions, effective potentials"),
            ("Wilsonian Effective Field Theory", "integrating out, relevant operators, decoupling"),
            ("Operator Product Expansion and Power Counting", "short distances, local operators, scaling"),
        ],
    ),
    (
        "Symmetry and Gauge Theory",
        [
            ("Groups and Lie Algebras from Matrices", "groups, generators, commutators, structure constants"),
            ("Representations and Charges", "representations, multiplets, weights, charges"),
            ("Global Symmetries and Noether Currents", "global transformations, currents, charges"),
            ("Spinors and the Dirac Field", "gamma matrices, Weyl spinors, Dirac equation"),
            ("Abelian Gauge Theory and QED", "covariant derivatives, photons, QED interactions"),
            ("Gauge Fixing and Ward Identities", "gauge fixing, photon propagator, Ward identities"),
            ("QED Amplitudes and Radiative Corrections", "fermion lines, tree amplitudes, radiative effects"),
        ],
    ),
    (
        "Non-Abelian Theory, Broken Symmetry, and Advanced Topics",
        [
            ("Non-Abelian Gauge Theory", "Yang-Mills fields, self-interactions, covariant field strengths"),
            ("Faddeev-Popov Ghosts and BRST Symmetry", "ghosts, gauge volume, BRST, physical states"),
            ("Spontaneous Symmetry Breaking", "vacua, Goldstone modes, broken generators"),
            ("The Higgs Mechanism", "gauge boson masses, unitary gauge, scalar sectors"),
            ("Nonperturbative Physics: Anomalies, Topology, and Instantons", "anomalies, topology, instantons, theta sectors"),
            ("Lattice Fields, Confinement, and Finite Temperature", "lattice actions, Wilson loops, thermal fields"),
            ("Curved Spacetime and the Standard Model", "curved backgrounds, Standard Model, electroweak theory"),
        ],
    ),
]


SECTION_ANGLES = [
    "The concrete problem",
    "Objects, notation, and units",
    "The finite calculation",
    "The central derivation",
    "Worked calculation",
    "Boundary conditions, normalization, and signs",
    "How the idea enters quantum field theory",
    "Review problems and extensions",
]


DATA = {
    "calculus": {
        "objects": "small changes, rates of change, accumulated area, and dimensionful quantities",
        "finite": r"a table of sampled values \(f(x_j)\) with spacing \(\Delta x\), where derivatives are differences and integrals are sums",
        "central": "linear approximation: the leading change of a quantity is the derivative multiplied by the small input change",
        "bridge": "Later functional derivatives and field equations are the same idea applied to infinitely many variables labelled by position.",
        "warning": r"The symbol \(O(h^2)\) is a promise about a limit; it should not be read as a number that can be ignored at any size of \(h\).",
        "focuses": [
            "linearizing a function",
            "tracking dimensions through a formula",
            "turning sums into integrals",
            "using integration by parts",
            "approximating a curve near one point",
            "controlling the error term",
            "reading a differential equation locally",
            "building a calculation log",
        ],
    },
    "geometry": {
        "objects": "arrows, coordinates, basis vectors, dot products, lengths, and projections",
        "finite": "a two- or three-component column vector whose components change when the basis is changed",
        "central": "a geometric statement must keep the same length and angle even when coordinates are rewritten",
        "bridge": "Fields will later have components under rotations, Lorentz transformations, and internal symmetry rotations.",
        "warning": "A component is not the vector itself; changing coordinates changes the component list without changing the arrow.",
        "focuses": [
            "separating vectors from coordinates",
            "computing projections",
            "changing bases",
            "dot products as measurements",
            "orthonormal frames",
            "matrix notation for geometry",
            "geometric invariants",
            "coordinate checks",
        ],
    },
    "fourier": {
        "objects": "periodic functions, modes, coefficients, transforms, delta functions, and Green functions",
        "finite": r"a vector of \(N\) samples expanded in the discrete waves \(e^{2\pi \ii nj/N}\)",
        "central": "orthogonality lets one coefficient be isolated by multiplying by the conjugate wave and summing or integrating",
        "bridge": "Propagators, particle momenta, and loop integrals are Fourier analysis with the physical boundary condition stated explicitly.",
        "warning": "The delta function is not an ordinary spike; it is a rule for what happens under an integral sign.",
        "focuses": [
            "decomposing a signal into modes",
            "normalizing Fourier coefficients",
            "passing from a box to the line",
            "deriving the delta representation",
            "solving a Green-function problem",
            "moving derivatives onto exponentials",
            "using spectra in field theory",
            "checking transform conventions",
        ],
    },
    "variation": {
        "objects": "paths, fields, variations, boundary terms, actions, currents, and local equations",
        "finite": r"a function \(F(q_1,\ldots,q_N)\), whose stationary points satisfy \( \partial F/\partial q_j=0 \)",
        "central": "stationarity for every allowed variation forces the coefficient of that variation to vanish point by point",
        "bridge": "Euler-Lagrange equations, Noether currents, and stress tensors are all consequences of varying an action carefully.",
        "warning": "A missing boundary term usually means that a boundary condition has been assumed, not that the term never existed.",
        "focuses": [
            "turning a path into many variables",
            "varying a derivative",
            "integrating by parts",
            "reading the Euler-Lagrange equation",
            "finding a conserved quantity",
            "handling fields instead of paths",
            "tracking surface terms",
            "testing a proposed symmetry",
        ],
    },
    "mechanics": {
        "objects": "generalized coordinates, momenta, energies, constraints, phase space, and Poisson brackets",
        "finite": r"a particle with coordinates \(q_i(t)\) and a Lagrangian depending on \(q_i\) and \(\dot q_i\)",
        "central": "the action principle gives equations of motion, and the Legendre transform rewrites them as first-order phase-space equations",
        "bridge": "Canonical quantization replaces Poisson brackets by commutators and turns field modes into oscillator variables.",
        "warning": "The Hamiltonian equals the energy only when the usual regularity and time-independence conditions are satisfied.",
        "focuses": [
            "choosing generalized coordinates",
            "deriving momenta",
            "performing a Legendre transform",
            "checking Hamilton equations",
            "using Poisson brackets",
            "recognizing constraints",
            "preparing canonical quantization",
            "comparing equivalent descriptions",
        ],
    },
    "oscillator": {
        "objects": "springs, normal modes, ladder operators, spectra, number operators, and zero-point energy",
        "finite": "one oscillator or a finite chain of coupled oscillators with a symmetric matrix of spring constants",
        "central": "a quadratic Hamiltonian can be diagonalized into independent modes, each behaving like a simple harmonic oscillator",
        "bridge": "A free quantum field is an infinite collection of harmonic oscillators, one for each allowed momentum.",
        "warning": "The zero-point term is not produced by a bad choice of origin; it comes from the commutator.",
        "focuses": [
            "solving the classical oscillator",
            "diagonalizing a coupled chain",
            "defining ladder operators",
            "deriving the spectrum",
            "normalizing wavefunctions",
            "counting occupation numbers",
            "taking the continuum limit",
            "connecting modes to particles",
        ],
    },
    "fields": {
        "objects": "fields, conjugate momenta, densities, mode expansions, commutators, and particles",
        "finite": r"a lattice of variables \(\phi_j(t)\), one at each point of a spatial grid",
        "central": "the continuum field equation is the limit of many coupled oscillator equations with nearest-neighbor differences",
        "bridge": "Canonical commutators and Fourier modes turn the Klein-Gordon field into creation and annihilation operators.",
        "warning": "A field value at a point is too sharp to be measured directly; smeared fields are the safer mathematical object.",
        "focuses": [
            "from lattice variables to a field",
            "deriving the field Euler equation",
            "finding the conjugate momentum",
            "solving by plane waves",
            "normalizing modes",
            "imposing commutators",
            "constructing Fock states",
            "checking causality",
        ],
    },
    "relativity": {
        "objects": "events, intervals, four-vectors, tensors, Lorentz transformations, energy, and momentum",
        "finite": "two inertial coordinate systems assigning numbers to the same pair of spacetime events",
        "central": r"the interval \(t^2-\bm x^2\) is invariant, so valid coordinate changes must preserve the Minkowski metric",
        "bridge": "Relativistic invariance constrains field equations, propagators, phase space, and allowed interaction terms.",
        "warning": "Upper and lower indices are not decoration; the metric is being used when an index is moved.",
        "focuses": [
            "constructing the invariant interval",
            "deriving a boost",
            "checking a four-vector",
            "lowering and raising indices",
            "building scalar equations",
            "reading mass shells",
            "using covariant notation",
            "testing nonrelativistic limits",
        ],
    },
    "quantum": {
        "objects": "states, amplitudes, inner products, operators, eigenvalues, commutators, spin, and identical particles",
        "finite": "a complex vector of amplitudes in a finite basis with probabilities given by squared magnitudes",
        "central": "linear operators act on amplitudes, and noncommuting operators encode measurement order",
        "bridge": "The field operators of QFT inherit the same Hilbert-space logic, but with infinitely many degrees of freedom.",
        "warning": "A state vector and a list of measurement outcomes are different objects; the Born rule connects them.",
        "focuses": [
            "normalizing amplitudes",
            "changing basis",
            "computing expectation values",
            "using commutators",
            "solving time evolution",
            "adding angular momenta",
            "symmetrizing identical states",
            "preparing field operators",
        ],
    },
    "path": {
        "objects": "Gaussian integrals, sources, time slices, kernels, functional derivatives, and stationary phase",
        "finite": r"an ordinary \(N\)-variable Gaussian integral with a symmetric matrix and a source vector",
        "central": "completing the square converts a quadratic integral with sources into an inverse operator",
        "bridge": "The free generating functional is the infinite-dimensional Gaussian whose inverse operator is the propagator.",
        "warning": r"The symbol \(\mathcal D q\) is a limit of ordinary measures; it should be introduced through time slicing before it is trusted.",
        "focuses": [
            "evaluating a Gaussian",
            "adding a source",
            "time-slicing a kernel",
            "taking the path limit",
            "deriving a propagator",
            "using functional derivatives",
            "rotating to Euclidean time",
            "checking normalizations",
        ],
    },
    "perturbation": {
        "objects": "interaction terms, contractions, propagators, vertices, diagrams, external legs, and amplitudes",
        "finite": "a Gaussian average corrected by a small non-quadratic term expanded as a power series",
        "central": "each source derivative chooses a field, each contraction gives a propagator, and each interaction term gives a vertex",
        "bridge": "Feynman rules, scattering amplitudes, LSZ reduction, and loop corrections are organized perturbative expansions of correlation functions.",
        "warning": "A diagram is not the calculation; it is a bookkeeping device for a definite integral and symmetry factor.",
        "focuses": [
            "expanding the interaction exponential",
            "proving Wick contractions",
            "reading a vertex factor",
            "conserving momentum at a vertex",
            "amputating external propagators",
            "normalizing phase space",
            "identifying loop variables",
            "checking symmetry factors",
        ],
    },
    "renormalization": {
        "objects": "cutoffs, poles, counterterms, measured parameters, beta functions, operators, and scales",
        "finite": "an integral whose value changes when the upper limit is changed, requiring a parameter to be adjusted",
        "central": "bare parameters are rewritten in terms of measured parameters plus counterterms so predictions stay finite",
        "bridge": "Effective field theory treats the Lagrangian as a scale-dependent expansion in all operators allowed by symmetry.",
        "warning": "A divergent intermediate integral is not by itself a physical prediction; the prediction comes after a renormalization condition is imposed.",
        "focuses": [
            "seeing a cutoff divergence",
            "subtracting with a counterterm",
            "defining a renormalized mass",
            "differentiating with respect to scale",
            "reading a beta function",
            "integrating out heavy modes",
            "power counting operators",
            "testing scheme dependence",
        ],
    },
    "group": {
        "objects": "matrices, transformations, generators, commutators, representations, charges, and currents",
        "finite": r"a family of matrices near the identity, \(U(\alpha)=1-\ii\alpha^aT^a+O(\alpha^2)\)",
        "central": "multiplying transformations near the identity reveals generators and their commutators",
        "bridge": "Internal symmetries determine conserved currents, multiplets, gauge charges, and the possible interaction terms.",
        "warning": "The same abstract group can have different representations, so the matrices acting on one field need not be the matrices acting on another.",
        "focuses": [
            "multiplying near-identity matrices",
            "extracting generators",
            "computing a commutator",
            "building a representation",
            "finding a charge",
            "deriving a current",
            "checking invariance",
            "connecting symmetry to selection rules",
        ],
    },
    "spinor": {
        "objects": "Pauli matrices, gamma matrices, Weyl spinors, Dirac spinors, bilinears, and antiparticles",
        "finite": "a two-component complex vector acted on by the Pauli matrices",
        "central": "the Dirac equation is a first-order square root of the relativistic mass-shell equation",
        "bridge": "Spinor fields bring fermions into QFT and make QED and the Standard Model possible.",
        "warning": "Spinor indices do not transform like vector indices; the Lorentz group acts on them through a different representation.",
        "focuses": [
            "using Pauli matrices",
            "constructing gamma matrices",
            "squaring the Dirac operator",
            "finding plane-wave spinors",
            "normalizing bilinears",
            "reading antiparticle solutions",
            "quantizing fermion fields",
            "checking Lorentz covariance",
        ],
    },
    "abelian": {
        "objects": "local phases, covariant derivatives, gauge fields, field strengths, currents, photons, and Ward identities",
        "finite": "a complex field whose phase can be changed independently at neighboring points",
        "central": "a gauge field compensates the derivative of a local phase so that the covariant derivative transforms like the field",
        "bridge": "QED is the quantized Abelian gauge theory obtained by coupling the Dirac field to the photon field.",
        "warning": "Gauge symmetry is a redundancy in description, not an ordinary global symmetry that produces distinct physical states.",
        "focuses": [
            "promoting a global phase to a local one",
            "deriving the covariant derivative",
            "building the field strength",
            "varying the Maxwell action",
            "fixing a gauge",
            "reading the photon propagator",
            "deriving the QED vertex",
            "checking a Ward identity",
        ],
    },
    "nonabelian": {
        "objects": "matrix-valued gauge fields, covariant field strengths, structure constants, ghosts, BRST symmetry, and self-interactions",
        "finite": "a field with several components transformed by a position-dependent unitary matrix",
        "central": "the commutator of covariant derivatives produces a field strength that contains a gauge-field commutator",
        "bridge": "Yang-Mills theory supplies the strong and weak gauge sectors and introduces gauge-boson self-interactions.",
        "warning": "Ghost fields are not optional decoration in covariant gauges; they represent the Faddeev-Popov determinant.",
        "focuses": [
            "deriving the non-Abelian gauge transformation",
            "computing a covariant commutator",
            "expanding Yang-Mills interactions",
            "varying the Yang-Mills action",
            "fixing a non-Abelian gauge",
            "introducing ghosts",
            "checking BRST nilpotency",
            "reading asymptotic freedom",
        ],
    },
    "broken": {
        "objects": "vacua, order parameters, broken generators, Goldstone modes, gauge boson masses, and Higgs fields",
        "finite": "a potential with a circle or sphere of minima rather than a single isolated minimum",
        "central": "expanding around one chosen vacuum separates flat directions from massive radial directions",
        "bridge": "The Higgs mechanism turns would-be Goldstone fields into longitudinal polarizations of massive gauge bosons.",
        "warning": "A symmetry of the Lagrangian can be absent from the chosen vacuum without being absent from the theory.",
        "focuses": [
            "finding degenerate minima",
            "choosing a vacuum",
            "expanding radial and angular modes",
            "deriving Goldstone's theorem",
            "coupling to a gauge field",
            "finding a gauge-boson mass",
            "using unitary gauge",
            "checking physical degrees of freedom",
        ],
    },
    "nonperturbative": {
        "objects": "Euclidean action, topology, instantons, winding number, Wilson loops, lattices, confinement, and thermal circles",
        "finite": "a system with more than one classical minimum, where tunneling cannot be seen in any finite power series around one minimum",
        "central": "finite-action Euclidean configurations and lattice variables reveal effects invisible to ordinary perturbation theory",
        "bridge": "Instantons, anomalies, confinement, finite-temperature fields, and topology explain why QFT is more than its Feynman diagrams.",
        "warning": "Nonperturbative does not mean uncalculable; it means the expansion parameter cannot be the only organizing principle.",
        "focuses": [
            "identifying a topological sector",
            "completing a Euclidean square",
            "reading an anomaly as a failed symmetry",
            "constructing a Wilson loop",
            "placing fields on a lattice",
            "using a thermal circle",
            "seeing confinement qualitatively",
            "connecting topology to amplitudes",
        ],
    },
    "standard": {
        "objects": "gauge groups, matter multiplets, Yukawa couplings, electroweak breaking, curved backgrounds, and effective descriptions",
        "finite": "a table listing fields, representations, and charges, checked term by term for gauge invariance",
        "central": "the Standard Model Lagrangian is the collection of lowest-dimension local terms allowed by its gauge symmetries and field content",
        "bridge": "The final application uses every earlier tool: spinors, gauge fields, symmetry breaking, renormalization, and effective reasoning.",
        "warning": "A compact Lagrangian hides many definitions; each symbol carries representation, charge, and normalization data.",
        "focuses": [
            "reading the gauge group",
            "assigning representations",
            "building covariant derivatives",
            "checking Yukawa terms",
            "breaking electroweak symmetry",
            "identifying physical fields",
            "placing QFT on a background metric",
            "summarizing the full course",
        ],
    },
}


def family_for(title: str) -> str:
    t = title.lower()
    if any(w in t for w in ["vectors", "coordinates", "geometry", "linear algebra", "eigenvectors", "hilbert"]):
        return "geometry"
    if any(w in t for w in ["nonperturbative", "anomal", "instanton", "lattice", "confinement", "finite temperature"]):
        return "nonperturbative"
    if "standard model" in t or "curved" in t:
        return "standard"
    if any(w in t for w in ["non-abelian", "yang-mills", "faddeev", "ghost", "brst"]):
        return "nonabelian"
    if any(w in t for w in ["higgs", "symmetry breaking"]):
        return "broken"
    if any(w in t for w in ["abelian gauge", "qed", "ward", "gauge fixing"]):
        return "abelian"
    if any(w in t for w in ["spinor", "dirac"]):
        return "spinor"
    if any(w in t for w in ["group", "lie algebra", "representation", "charges", "global symmetries"]):
        return "group"
    if any(w in t for w in ["renormal", "regularization", "cutoff", "dimensional", "running", "effective", "wilsonian", "operator product"]):
        return "renormalization"
    if any(w in t for w in ["wick", "interacting", "feynman", "scattering", "lsz", "loops", "self-energy", "vertex corrections"]):
        return "perturbation"
    if any(w in t for w in ["path integral", "generating functional"]):
        return "path"
    if any(w in t for w in ["klein-gordon", "fock", "propagator", "microcausality", "complex scalar", "scalar field as", "classical scalar field"]):
        return "fields"
    if any(w in t for w in ["harmonic oscillator", "coupled oscillators"]):
        return "oscillator"
    if any(w in t for w in ["quantum states", "operators", "angular momentum", "time evolution"]):
        return "quantum"
    if any(w in t for w in ["relativ", "tensor", "maxwell"]):
        return "relativity"
    if any(w in t for w in ["lagrangian", "hamiltonian"]):
        return "mechanics"
    if any(w in t for w in ["variational", "noether"]):
        return "variation"
    if any(w in t for w in ["fourier", "differential equations", "green", "complex numbers"]):
        return "fourier"
    return "calculus"


def section_title(chapter_title: str, section_no: int) -> str:
    data = DATA[family_for(chapter_title)]
    angle = SECTION_ANGLES[section_no - 1]
    focus = data["focuses"][section_no - 1]
    return f"{angle}: {focus}"


def equation_block(family: str) -> str:
    equations = {
        "calculus": [
            r"f(x+h)=f(x)+hf'(x)+\frac{h^2}{2}f''(x)+O(h^3)",
            r"\int_a^b u'(x)v(x)\dd x=[uv]_a^b-\int_a^b u(x)v'(x)\dd x",
            r"\sum_{j=0}^{N-1}f(x_j)\Delta x\longrightarrow \int_a^b f(x)\dd x",
        ],
        "geometry": [
            r"\bm v=v^i\bm e_i,\qquad \bm v\cdot\bm w=v^iw^j(\bm e_i\cdot\bm e_j)",
            r"\mathrm{proj}_{\hat n}\bm v=(\bm v\cdot\hat n)\hat n",
            r"A\bm e_j=A^i{}_j\bm e_i",
        ],
        "fourier": [
            r"c_n=\frac1L\int_0^L f(x)e^{-2\pi\ii nx/L}\dd x",
            r"f(x)=\int_{-\infty}^{\infty}\frac{\dd k}{2\pi}\tilde f(k)e^{\ii kx}",
            r"\delta(x-y)=\int_{-\infty}^{\infty}\frac{\dd k}{2\pi}e^{\ii k(x-y)}",
        ],
        "variation": [
            r"S[q]=\int_{t_i}^{t_f}L(q,\dot q,t)\dd t",
            r"\delta S=\int_{t_i}^{t_f}\left(\frac{\p L}{\p q}-\frac{\dd}{\dd t}\frac{\p L}{\p\dot q}\right)\eta(t)\dd t",
            r"\frac{\dd}{\dd t}\frac{\p L}{\p\dot q}-\frac{\p L}{\p q}=0",
        ],
        "mechanics": [
            r"p_i=\frac{\p L}{\p\dot q_i},\qquad H=p_i\dot q_i-L",
            r"\dot q_i=\frac{\p H}{\p p_i},\qquad \dot p_i=-\frac{\p H}{\p q_i}",
            r"\{f,g\}=\frac{\p f}{\p q_i}\frac{\p g}{\p p_i}-\frac{\p f}{\p p_i}\frac{\p g}{\p q_i}",
        ],
        "oscillator": [
            r"H=\frac12p^2+\frac12\omega^2q^2",
            r"a=\frac{1}{\sqrt{2\omega}}(\omega q+\ii p),\qquad a^\dagger=\frac{1}{\sqrt{2\omega}}(\omega q-\ii p)",
            r"H=\omega\left(a^\dagger a+\frac12\right)",
        ],
        "fields": [
            r"\Lag=\frac12\p_\mu\phi\p^\mu\phi-\frac12m^2\phi^2",
            r"(\Boxop+m^2)\phi=0",
            r"\phi(x)=\int\frac{\dd^3p}{(2\pi)^3}\frac{a_{\bm p}e^{-\ii p\cdot x}+a_{\bm p}^\dagger e^{\ii p\cdot x}}{\sqrt{2E_{\bm p}}}",
        ],
        "relativity": [
            r"s^2=\eta_{\mu\nu}x^\mu x^\nu=t^2-\bm x^2",
            r"\eta_{\rho\sigma}\Lambda^\rho{}_\mu\Lambda^\sigma{}_\nu=\eta_{\mu\nu}",
            r"p_\mu p^\mu=E^2-\bm p^2=m^2",
        ],
        "quantum": [
            r"\sum_i |c_i|^2=1,\qquad \ket{\psi}=\sum_i c_i\ket{i}",
            r"\avg A=\bra{\psi}A\ket{\psi}",
            r"\ii\frac{\dd}{\dd t}\ket{\psi(t)}=H\ket{\psi(t)}",
        ],
        "path": [
            r"\int\dd^n x\,e^{-\frac12x^TAx+J^Tx}=\frac{(2\pi)^{n/2}}{\sqrt{\det A}}e^{\frac12J^TA^{-1}J}",
            r"K(q_f,t_f;q_i,t_i)=\int_{q_i}^{q_f}\D q\,e^{\ii S[q]}",
            r"Z[J]=Z[0]\exp\left(\frac{\ii}{2}\int J\Delta_FJ\right)",
        ],
        "perturbation": [
            r"\Delta_F(p)=\frac{\ii}{p^2-m^2+\ii\epsilon}",
            r"e^{\ii\int\Lag_I}=1+\ii\int\Lag_I+\frac{\ii^2}{2}\left(\int\Lag_I\right)^2+\cdots",
            r"\ii\mathcal M=\hbox{sum of connected amputated diagrams}",
        ],
        "renormalization": [
            r"m_0^2=m^2+\delta m^2,\qquad \lambda_0=\mu^\epsilon(\lambda+\delta\lambda)",
            r"\mu\frac{\dd g}{\dd\mu}=\beta(g)",
            r"\Lag_{\mathrm{eff}}=\sum_i c_i(\mu)\mathcal O_i",
        ],
        "group": [
            r"U(\alpha)=1-\ii\alpha^aT^a+O(\alpha^2)",
            r"[T^a,T^b]=\ii f^{abc}T^c",
            r"j^\mu_a=\frac{\p\Lag}{\p(\p_\mu\phi_i)}(T_a)^i{}_j\phi_j",
        ],
        "spinor": [
            r"\sigma^i\sigma^j=\delta^{ij}\id+\ii\epsilon^{ijk}\sigma^k",
            r"\{\gamma^\mu,\gamma^\nu\}=2\eta^{\mu\nu}",
            r"(\ii\gamma^\mu\p_\mu-m)\psi=0",
        ],
        "abelian": [
            r"D_\mu=\p_\mu+\ii qA_\mu,\qquad A_\mu\to A_\mu+\p_\mu\alpha",
            r"F_{\mu\nu}=\p_\mu A_\nu-\p_\nu A_\mu",
            r"\Lag_{\mathrm{QED}}=\bar\psi(\ii\gamma^\mu D_\mu-m)\psi-\frac14F_{\mu\nu}F^{\mu\nu}",
        ],
        "nonabelian": [
            r"D_\mu=\p_\mu+\ii gA_\mu^aT^a",
            r"F_{\mu\nu}^a=\p_\mu A_\nu^a-\p_\nu A_\mu^a-gf^{abc}A_\mu^bA_\nu^c",
            r"\Lag_{\mathrm{YM}}=-\frac14F_{\mu\nu}^aF^{a\mu\nu}",
        ],
        "broken": [
            r"V(\phi)=\frac{\lambda}{4}(\phi^2-v^2)^2",
            r"\phi(x)=v+h(x),\qquad m_h^2=2\lambda v^2",
            r"|D_\mu\Phi|^2\supset \frac12g^2v^2A_\mu A^\mu",
        ],
        "nonperturbative": [
            r"Z=\sum_Q\int_Q\D\phi\,e^{-S_E[\phi]}",
            r"W(C)=\Tr\,\mathcal P\exp\left(\ii g\oint_C A_\mu\dd x^\mu\right)",
            r"\Gamma[\phi,A]\hbox{ may fail to keep a classical symmetry after regularization}",
        ],
        "standard": [
            r"G_{\mathrm{SM}}=SU(3)_c\times SU(2)_L\times U(1)_Y",
            r"D_\mu=\p_\mu+\ii g_sG_\mu^aT^a+\ii gW_\mu^i\tau^i+\ii g'YB_\mu",
            r"\Lag\supset -y_e\bar L\Phi e_R+\hbox{h.c.}",
        ],
    }[family]
    return "\n".join(f"\\[\n  {eq}\n\\]" for eq in equations)


def long_explanation(chapter_title: str, section_no: int, keywords: str) -> str:
    family = family_for(chapter_title)
    data = DATA[family]
    title_e = tex_escape(chapter_title)
    section_e = tex_escape(section_title(chapter_title, section_no))
    focus_e = tex_escape(data["focuses"][section_no - 1])
    keywords_e = tex_escape(keywords)
    objects = clean_tex_text(data["objects"])
    finite = clean_tex_text(data["finite"])
    central = clean_tex_text(data["central"])
    bridge = clean_tex_text(data["bridge"])
    warning = clean_tex_text(data["warning"])
    context = tex_escape(f"{chapter_title}, section {section_no}")
    raw_text = fr"""
The work of this section is {focus_e}.  In the chapter heading the vocabulary is {keywords_e}, but the first objects on the page are more prosaic: {objects}.  The formal notation will be useful only after it has been tied to a limit, a symmetry, a normalization condition, or an integration-by-parts step.

The finite model is {finite}.  In that model no mystery is available: every derivative is an ordinary derivative with respect to one listed variable, every inner product is a sum, and every boundary assumption can be written at the endpoints.  This is why the finite model is not a toy in the dismissive sense.  It is the bookkeeping device that prevents continuum notation from becoming a fog of indices.

The central idea for this chapter is {central}.  To test that idea, strip the formula down until only the operation remains.  A sign change after raising or lowering an index means the metric has entered.  A derivative moving from one factor to another means a boundary term has been handled.  A normalization constant means that some unit object, such as a delta function, basis vector, or one-particle state, has been fixed.

For {section_e.lower()}, the calculation should also pass a dimensional check.  The left and right sides must carry the same units; more subtly, they must transform in the same way under the symmetries already introduced.  This is not a proof, but it is a quick way to catch wrong factors of \(2\pi\), signs in the metric, missing powers of the lattice spacing, or an omitted charge.

The bridge to quantum field theory is direct.  {bridge}  Later notation will carry more indices and fewer verbal reminders, so the safe habit is to keep asking which operation is being performed and which quantity is being held fixed.

One warning is worth making explicit here.  {warning}  This warning points to the delicate step of the derivation, not to a decorative aside.

The section closes by keeping {focus_e} connected to {title_e}.  The same general operation will be used with different objects in neighboring chapters, so the present calculation is both a result and a rehearsal.
""".strip()
    return contextualize_paragraphs(raw_text, context)


def derivation_text(chapter_title: str, section_no: int) -> str:
    family = family_for(chapter_title)
    topic = tex_escape(f"{chapter_title}: {section_title(chapter_title, section_no)}")
    eqs = equation_block(family)
    n = section_no + 2
    context = tex_escape(f"{chapter_title}, section {section_no}")
    if family == "calculus":
        body = r"""
Take a differentiable function \(f\) and compare \(f(x+h)\) with \(f(x)\).  By the definition of derivative, the ratio
\[
  \frac{f(x+h)-f(x)}{h}
\]
approaches \(f'(x)\) as \(h\to0\).  Therefore the difference itself has the form
\[
  f(x+h)-f(x)=hf'(x)+h\,r(h),
\]
where \(r(h)\to0\).  If \(f\) has a second derivative, the next correction is \(\frac12h^2f''(x)\).  The expression is not a slogan about smallness; it is an accounting rule for how much information is being kept.

The same bookkeeping explains integration by parts.  Start with the product rule \((uv)'=u'v+uv'\).  Integrating from \(a\) to \(b\) gives \(\int_a^b u'v\dd x=[uv]_a^b-\int_a^buv'\dd x\).  Every later variational derivation uses exactly this line, with \(u\) replaced by a variation or a field.
"""
    elif family == "geometry":
        body = r"""
Let \(\hat n\) be a unit vector.  The component of \(\bm v\) along \(\hat n\) is the number \(c\) for which \(c\hat n\) is the closest vector on the line spanned by \(\hat n\).  Minimize \(\|\bm v-c\hat n\|^2\):
\[
  \|\bm v-c\hat n\|^2=\bm v\cdot\bm v-2c\,\bm v\cdot\hat n+c^2.
\]
Differentiating with respect to \(c\) gives \(-2\bm v\cdot\hat n+2c=0\), hence \(c=\bm v\cdot\hat n\).  Thus projection is not a memorized formula; it is a one-variable minimization problem.

When the basis changes, the arrow has not changed.  If \(\bm v=v^i\bm e_i=\tilde v^i\tilde{\bm e}_i\), the component lists differ because the basis vectors differ.  This distinction is the seed of tensor notation.
"""
    elif family == "fourier":
        body = r"""
Let \(f(x)\) be periodic on an interval of length \(L\).  Suppose it can be written as \(f(x)=\sum_n c_ne^{2\pi\ii nx/L}\).  Multiply by \(e^{-2\pi\ii mx/L}\) and integrate:
\[
  \int_0^L f(x)e^{-2\pi\ii mx/L}\dd x
  =
  \sum_n c_n\int_0^L e^{2\pi\ii(n-m)x/L}\dd x.
\]
The integral on the right is \(L\) when \(n=m\) and zero otherwise.  The orthogonality of the waves therefore isolates one coefficient, \(c_m\).

Letting the interval grow turns the sum over \(n\) into an integral over \(k\).  The statement that all modes together reconstruct a function becomes the delta identity \(\delta(x-y)=\int(\dd k/2\pi)e^{\ii k(x-y)}\), understood under an integral against a smooth test function.
"""
    elif family == "variation":
        body = r"""
Choose a path \(q(t)\) and a nearby path \(q(t)+\epsilon\eta(t)\), with \(\eta(t_i)=\eta(t_f)=0\).  The action changes by
\[
  \frac{\dd}{\dd\epsilon}S[q+\epsilon\eta]\bigg|_{\epsilon=0}
  =
  \int_{t_i}^{t_f}
  \left(
  \frac{\p L}{\p q}\eta+\frac{\p L}{\p\dot q}\dot\eta
  \right)\dd t.
\]
The second term still contains \(\dot\eta\), so integrate it by parts:
\[
  \int \frac{\p L}{\p\dot q}\dot\eta\dd t
  =
  \left[\frac{\p L}{\p\dot q}\eta\right]_{t_i}^{t_f}
  -
  \int \frac{\dd}{\dd t}\frac{\p L}{\p\dot q}\eta\dd t.
\]
The endpoint term vanishes because the endpoints of the varied path are fixed.  Since \(\eta\) is otherwise arbitrary, the coefficient of \(\eta\) must vanish.  That is the Euler-Lagrange equation.
"""
    elif family == "mechanics":
        body = r"""
Start from the differential of the Lagrangian,
\[
  \dd L=\frac{\p L}{\p q_i}\dd q_i+\frac{\p L}{\p\dot q_i}\dd\dot q_i+\frac{\p L}{\p t}\dd t.
\]
Define \(p_i=\p L/\p\dot q_i\) and \(H=p_i\dot q_i-L\), assuming the velocities can be solved in terms of \(q\) and \(p\).  Then
\[
  \dd H=\dot q_i\dd p_i+p_i\dd\dot q_i-\dd L.
\]
Substitute the expression for \(\dd L\) and use the Euler-Lagrange equation \(\dot p_i=\p L/\p q_i\).  The \(p_i\dd\dot q_i\) terms cancel, leaving
\[
  \dd H=\dot q_i\dd p_i-\dot p_i\dd q_i-\frac{\p L}{\p t}\dd t.
\]
Reading coefficients gives Hamilton's equations.
"""
    elif family == "oscillator":
        body = r"""
For the oscillator with \(H=\frac12p^2+\frac12\omega^2q^2\), define
\[
  a=\frac{1}{\sqrt{2\omega}}(\omega q+\ii p),\qquad
  a^\dagger=\frac{1}{\sqrt{2\omega}}(\omega q-\ii p).
\]
Using \([q,p]=\ii\), compute
\[
  [a,a^\dagger]
  =
  \frac{1}{2\omega}[\omega q+\ii p,\omega q-\ii p]=1.
\]
Now multiply \(a^\dagger a\):
\[
  a^\dagger a=\frac{1}{2\omega}(\omega^2q^2+p^2-\omega).
\]
Therefore \(H=\omega(a^\dagger a+\frac12)\).  If \(N=a^\dagger a\), then \([N,a^\dagger]=a^\dagger\), so \(a^\dagger\) raises the energy by \(\omega\).  The lowest state cannot be lowered further, giving the zero-point energy \(\omega/2\).
"""
    elif family == "fields":
        body = r"""
Begin with the scalar action \(S=\int\dd^4x\,\Lag\), where \(\Lag=\frac12\p_\mu\phi\p^\mu\phi-\frac12m^2\phi^2\).  Vary \(\phi\to\phi+\epsilon\eta\):
\[
  \delta S=\int\dd^4x\left(\p_\mu\phi\,\p^\mu\eta-m^2\phi\eta\right).
\]
Integrate the first term by parts in spacetime and assume the surface term vanishes:
\[
  \delta S=-\int\dd^4x\,(\p_\mu\p^\mu\phi+m^2\phi)\eta.
\]
Since \(\eta(x)\) is arbitrary, the coefficient must vanish, so \((\Boxop+m^2)\phi=0\).  A plane wave \(e^{-\ii p\cdot x}\) then gives \(p^2=m^2\), the relativistic mass shell.
"""
    elif family == "relativity":
        body = r"""
In one space dimension write a linear change of coordinates as \(t'=\gamma(t-vx)\) and \(x'=\gamma(x-vt)\).  Compute the interval:
\[
  t'^2-x'^2
  =
  \gamma^2[(t-vx)^2-(x-vt)^2]
  =
  \gamma^2(1-v^2)(t^2-x^2).
\]
Requiring this to equal \(t^2-x^2\) fixes \(\gamma=1/\sqrt{1-v^2}\).  The calculation is only algebra, but it explains why Lorentz transformations are metric-preserving transformations.

For momentum, the same invariant form gives \(p_\mu p^\mu=m^2\).  Writing \(p^\mu=(E,\bm p)\) yields \(E^2-\bm p^2=m^2\), the dispersion relation used by relativistic propagators.
"""
    elif family == "quantum":
        body = r"""
Let \(\ket{\psi}=\sum_i c_i\ket{i}\) in an orthonormal basis.  The norm is
\[
  \braket{\psi}{\psi}=\sum_i |c_i|^2.
\]
Normalizing the state makes this sum equal to one.  An observable \(A\) has expectation value
\[
  \avg A=\sum_{ij}c_i^*A_{ij}c_j.
\]
If \(A\) and \(B\) do not commute, then \(AB\ket{\psi}\) and \(BA\ket{\psi}\) are generally different vectors.  The commutator records the part of the two-step operation that depends on order.  This finite-dimensional fact is the model for field commutators at equal time.
"""
    elif family == "path":
        body = r"""
For a positive matrix \(A\), complete the square in the exponent:
\[
  -\frac12x^TAx+J^Tx
  =
  -\frac12(x-A^{-1}J)^TA(x-A^{-1}J)
  +\frac12J^TA^{-1}J.
\]
The shift \(x\mapsto x+A^{-1}J\) changes neither the range nor the measure of the ordinary integral.  The source dependence is therefore the exponential of \(\frac12J^TA^{-1}J\).

The field version replaces \(A^{-1}\) by a Green function.  Differentiating the generating functional twice with respect to \(J\) pulls down that inverse operator, which is why the propagator is the basic line in perturbation theory.
"""
    elif family == "perturbation":
        body = r"""
Split the action into a free quadratic part and an interaction.  In the path integral,
\[
  e^{\ii S}=e^{\ii S_0}\left(1+\ii S_I+\frac{\ii^2}{2}S_I^2+\cdots\right).
\]
For \(\Lag_I=-\lambda\phi^4/4!\), one insertion contributes \(-\ii\lambda\int\dd^4x\,\phi(x)^4/4!\).  The four fields at that point can contract with four external fields in \(4!\) ways, cancelling the \(4!\) in the Lagrangian.  The vertex factor is therefore \(-\ii\lambda\).

External propagators are removed by LSZ because asymptotic particles are identified with the residues of poles in correlation functions.  What remains after the pole factors are stripped is the scattering amplitude \(\mathcal M\).
"""
    elif family == "renormalization":
        body = r"""
A typical cutoff integral has the form
\[
  I_\Lambda(m)=\int^{\Lambda}\frac{\dd^4k}{(2\pi)^4}\frac{1}{k^2+m^2}.
\]
At large \(k\), the integrand behaves like \(1/k^2\), while \(\dd^4k\) contributes \(k^3\dd k\), so the integral grows like \(\Lambda^2\).  The divergence is local: it has the same form as a mass term in the Lagrangian.

Write \(m_0^2=m^2+\delta m^2\).  Choose \(\delta m^2\) to cancel the cutoff dependence according to a measured mass condition.  If the cutoff changes while the measured quantity is held fixed, the renormalized parameter must run.  Differentiating that statement with respect to the scale gives a beta function.
"""
    elif family == "group":
        body = r"""
Let \(U(\alpha)=1-\ii\alpha^aT^a+O(\alpha^2)\).  Multiply two small transformations in opposite orders:
\[
  U(\alpha)U(\beta)-U(\beta)U(\alpha)
  =
  -\alpha^a\beta^b[T^a,T^b]+O(\alpha^2\beta,\alpha\beta^2).
\]
Closure of the transformations near the identity means the commutator must be another generator:
\[
  [T^a,T^b]=\ii f^{abc}T^c.
\]
The constants \(f^{abc}\) are not arbitrary decoration; they measure how the group curves away from being Abelian.  When a field transforms in a representation, these matrices determine its charge and its current.
"""
    elif family == "spinor":
        body = r"""
The relativistic equation should imply \(p_\mu p^\mu=m^2\).  Try a first-order operator \(\gamma^\mu p_\mu-m\).  Multiplying by \(\gamma^\nu p_\nu+m\) gives
\[
  (\gamma^\mu p_\mu-m)(\gamma^\nu p_\nu+m)
  =
  \gamma^\mu\gamma^\nu p_\mu p_\nu-m^2.
\]
The product \(p_\mu p_\nu\) is symmetric in \(\mu,\nu\), so only the anticommutator of the gamma matrices contributes.  Requiring the result to be \(p^2-m^2\) gives \(\{\gamma^\mu,\gamma^\nu\}=2\eta^{\mu\nu}\).  The Dirac equation is therefore a square root of the mass-shell condition.
"""
    elif family == "abelian":
        body = r"""
Let \(\psi\to e^{-\ii q\alpha(x)}\psi\).  An ordinary derivative produces an extra term:
\[
  \p_\mu(e^{-\ii q\alpha}\psi)
  =
  e^{-\ii q\alpha}(\p_\mu\psi-\ii q(\p_\mu\alpha)\psi).
\]
Define \(D_\mu=\p_\mu+\ii qA_\mu\) and require \(D_\mu\psi\to e^{-\ii q\alpha}D_\mu\psi\).  This fixes \(A_\mu\to A_\mu+\p_\mu\alpha\).  The field strength
\[
  F_{\mu\nu}=\p_\mu A_\nu-\p_\nu A_\mu
\]
is invariant because mixed partial derivatives commute.  Gauge invariance has forced both the interaction and the kinetic structure.
"""
    elif family == "nonabelian":
        body = r"""
Let \(D_\mu=\p_\mu+\ii gA_\mu\), with \(A_\mu=A_\mu^aT^a\).  Acting on a test field,
\[
  [D_\mu,D_\nu]
  =
  \ii g(\p_\mu A_\nu-\p_\nu A_\mu)-g^2[A_\mu,A_\nu].
\]
Write this as \([D_\mu,D_\nu]=\ii gF_{\mu\nu}\).  The commutator term is the new feature:
\[
  F_{\mu\nu}=\p_\mu A_\nu-\p_\nu A_\mu+\ii g[A_\mu,A_\nu].
\]
Using \([T^a,T^b]=\ii f^{abc}T^c\) gives the component expression with the \(gf^{abc}A_\mu^bA_\nu^c\) self-interaction.  Squaring \(F_{\mu\nu}\) in the action produces cubic and quartic gauge-boson vertices.
"""
    elif family == "broken":
        body = r"""
Consider \(V(\phi)=\lambda(\phi^2-v^2)^2/4\).  The minima satisfy \(\phi^2=v^2\), so choose the vacuum \(\phi=v\) and write \(\phi=v+h\).  Expanding,
\[
  V(v+h)=\frac{\lambda}{4}(2vh+h^2)^2
  =\lambda v^2h^2+\lambda vh^3+\frac{\lambda}{4}h^4.
\]
Since a scalar mass term has the form \(\frac12m_h^2h^2\), the radial excitation has \(m_h^2=2\lambda v^2\).  In a theory with a continuous circle of minima, angular fluctuations cost no potential energy at quadratic order.  Those are Goldstone modes unless a gauge field absorbs them.
"""
    elif family == "nonperturbative":
        body = r"""
In Euclidean signature the weight is \(e^{-S_E}\), so finite-action configurations dominate rare transitions.  If the configuration space is split into sectors labelled by an integer \(Q\), the path integral is a sum over sectors:
\[
  Z=\sum_Q\int_Q\D\phi\,e^{-S_E[\phi]}.
\]
No finite Taylor series around the \(Q=0\) vacuum can produce a contribution proportional to \(e^{-8\pi^2/g^2}\), because that dependence is nonanalytic at \(g=0\).  This is the calculational meaning of nonperturbative physics.

On a lattice, a Wilson loop measures the gauge phase around a closed curve.  Area-law behavior of large loops is the diagnostic of confinement in pure gauge theory.
"""
    else:
        body = r"""
List the fields with their representations under \(SU(3)_c\times SU(2)_L\times U(1)_Y\).  A term in the Lagrangian is allowed only if all gauge indices can be contracted to a singlet and the hypercharges sum to zero.  For example, the charged-lepton Yukawa term has the schematic form
\[
  -y_e\bar L\Phi e_R+\hbox{h.c.}
\]
The \(SU(2)\) indices of \(L\) and \(\Phi\) are contracted, and the hypercharges are chosen so the product is neutral.  When \(\Phi\) is expanded around its vacuum value, the same term becomes a fermion mass term.  This single check uses representations, gauge invariance, spontaneous symmetry breaking, and ordinary dimensional analysis.
"""
    body = contextualize_paragraphs(body, context)
    closing = f"In this setting the calculation for {topic} is complete when the finite model, the limiting step, and the normalization or boundary condition can all be named without looking back at the prose."
    return f"""\\paragraph{{Step-by-step derivation.}}

For {topic}, the derivation is written from the smallest usable model upward.

{body.strip()}

The formulas to keep in view are

{eqs}

{closing}
"""


def example_block(chapter_title: str, section_no: int, chapter_no: int) -> str:
    family = family_for(chapter_title)
    topic = tex_escape(f"{chapter_title}: {section_title(chapter_title, section_no)}")
    n = chapter_no + section_no + 2
    context = tex_escape(f"{chapter_title}, section {section_no}")
    if family == "geometry":
        body = r"""
Take \(\bm v=(3,4)\) and \(\hat n=(1,0)\) in an orthonormal basis.  The projection coefficient is
\[
  \bm v\cdot\hat n=3,
\]
so the projected vector is \((3,0)\).  If the basis is rotated, the component list changes, but the length of the projected vector remains \(3\).  This is the small finite-dimensional check behind later statements about tensors and invariant inner products.
"""
    elif family == "fourier":
        body = r"""
Let \(f(x)=x\) on \((-\pi,\pi)\), extended periodically.  Because \(f\) is odd, only sine terms appear:
\[
  f(x)=\sum_{m=1}^\infty b_m\sin mx.
\]
The coefficient is
\[
  b_m=\frac1\pi\int_{-\pi}^\pi x\sin mx\dd x
  =\frac2\pi\int_0^\pi x\sin mx\dd x.
\]
Integrating by parts gives \(b_m=2(-1)^{m+1}/m\).  The discontinuity at the endpoint is exactly where pointwise convergence must be treated with care.
"""
    elif family == "variation":
        body = r"""
Take \(L=\frac12m\dot q^2-\frac12kq^2\).  Then
\[
  \frac{\p L}{\p q}=-kq,\qquad \frac{\p L}{\p\dot q}=m\dot q.
\]
The Euler-Lagrange equation gives \(m\ddot q+kq=0\).  Trying \(q=e^{-\ii\omega t}\) gives \(-m\omega^2+k=0\), so \(\omega=\sqrt{k/m}\).  The variational calculation and the spectral calculation agree.
"""
    elif family == "mechanics":
        body = r"""
For \(L=\frac12m\dot q^2-V(q)\), the momentum is \(p=m\dot q\).  The Hamiltonian is
\[
  H=p\dot q-L=\frac{p^2}{2m}+V(q).
\]
Hamilton's equations give \(\dot q=p/m\) and \(\dot p=-V'(q)\).  Combining them recovers \(m\ddot q=-V'(q)\), so the phase-space form has not changed the physics.
"""
    elif family == "oscillator":
        body = r"""
Let \(\ket{0}\) obey \(a\ket{0}=0\).  Define \(\ket{r}=C_r(a^\dagger)^r\ket{0}\).  Since \([N,a^\dagger]=a^\dagger\), induction gives \(N\ket{r}=r\ket{r}\).  Normalization fixes \(C_r=1/\sqrt{r!}\).  The energy is \(E_r=\omega(r+\frac12)\).
"""
    elif family == "fields":
        body = r"""
For a plane wave \(\phi(x)=Ae^{-\ii Et+\ii\bm p\cdot\bm x}\), the Klein-Gordon equation gives
\[
  (-E^2+\bm p^2+m^2)\phi=0.
\]
A nonzero solution therefore requires \(E^2=\bm p^2+m^2\).  The sign of the exponent did not matter; it labels positive- and negative-frequency parts that become annihilation and creation operators after quantization.
"""
    elif family == "relativity":
        body = r"""
Set \(v=3/5\), so \(\gamma=5/4\).  For an event with \(t=5\) and \(x=2\), the boosted coordinates are \(t'=\gamma(t-vx)\) and \(x'=\gamma(x-vt)\).  Direct substitution gives \(t'^2-x'^2=t^2-x^2\).  This numerical check is a useful guard against sign errors before tensor notation is used.
"""
    elif family == "quantum":
        body = r"""
Let \(\ket{\psi}=(3\ket{1}+4\ii\ket{2})/5\).  The probabilities for the two basis outcomes are \(9/25\) and \(16/25\).  For \(A=\operatorname{diag}(a_1,a_2)\), the expectation value is
\[
  \avg A=\frac{9}{25}a_1+\frac{16}{25}a_2.
\]
The phase of the second coefficient does not affect this diagonal measurement, but it will affect measurements in another basis.
"""
    elif family == "path":
        body = r"""
For one variable,
\[
  Z(J)=\int\dd x\,e^{-ax^2/2+Jx}
  =\sqrt{\frac{2\pi}{a}}e^{J^2/2a}.
\]
Then \(Z^{-1}(0)\dd^2Z/\dd J^2|_{J=0}=1/a\).  In the field version, \(1/a\) is replaced by the inverse differential operator, namely the propagator.
"""
    elif family == "perturbation":
        body = r"""
In \(\lambda\phi^4\) theory, the four-point function at first order has one interaction insertion.  The four fields at the vertex can be paired with four external fields in \(4!\) ways, cancelling the \(1/4!\).  The remaining factor is \(-\ii\lambda\), multiplied by four propagators from the vertex point to the external points.
"""
    elif family == "renormalization":
        body = r"""
Regulate
\[
  I_\Lambda=\int_0^\Lambda\frac{k^3\dd k}{k^2+m^2}.
\]
Write \(k^3/(k^2+m^2)=k-m^2k/(k^2+m^2)\).  Then
\[
  I_\Lambda=\frac12\Lambda^2-\frac{m^2}{2}\log\frac{\Lambda^2+m^2}{m^2}.
\]
The quadratic and logarithmic dependence tell us which local counterterms can absorb the cutoff sensitivity.
"""
    elif family == "group":
        body = r"""
For \(SU(2)\), take \(T^a=\sigma^a/2\).  Since \(\sigma^1\sigma^2=\ii\sigma^3\) and \(\sigma^2\sigma^1=-\ii\sigma^3\),
\[
  [T^1,T^2]=\frac14[\sigma^1,\sigma^2]=\ii T^3.
\]
Thus \(f^{123}=1\).  The calculation is just matrix multiplication, but it contains the seed of non-Abelian gauge self-interactions.
"""
    elif family == "spinor":
        body = r"""
In the rest frame \(p^\mu=(m,0,0,0)\), the Dirac equation becomes \((\gamma^0-1)u=0\) for positive-energy spinors after dividing by \(m\).  This selects two independent spin states.  Boosting these rest spinors gives moving solutions; the algebra of the gamma matrices guarantees that the boosted solutions still satisfy \(p^2=m^2\).
"""
    elif family == "abelian":
        body = r"""
Apply \(A_\mu\to A_\mu+\p_\mu\alpha\) to \(F_{\mu\nu}\):
\[
  F_{\mu\nu}\to F_{\mu\nu}+\p_\mu\p_\nu\alpha-\p_\nu\p_\mu\alpha=F_{\mu\nu}.
\]
The cancellation uses only equality of mixed partial derivatives.  This is why \(F_{\mu\nu}\), not \(A_\mu\) alone, appears in the gauge-field kinetic term.
"""
    elif family == "nonabelian":
        body = r"""
Take two generators with \([T^1,T^2]=\ii T^3\).  If \(A_\mu=A_\mu^1T^1\) and \(A_\nu=A_\nu^2T^2\), then the commutator part of \(F_{\mu\nu}\) contains
\[
  \ii g[A_\mu,A_\nu]=\ii gA_\mu^1A_\nu^2[T^1,T^2]=-gA_\mu^1A_\nu^2T^3.
\]
Two gauge components have produced a third.  That is the algebraic origin of gauge-boson self-coupling.
"""
    elif family == "broken":
        body = r"""
For a complex scalar \(\Phi=(v+h)e^{\ii\theta/v}/\sqrt2\), the kinetic term contains
\[
  |\p_\mu\Phi|^2=\frac12(\p_\mu h)^2+\frac12(1+h/v)^2(\p_\mu\theta)^2.
\]
At \(h=0\), there is no potential term for \(\theta\), so \(\theta\) is massless.  Replacing \(\p_\mu\) by \(D_\mu\) lets the gauge field absorb this angular mode.
"""
    elif family == "nonperturbative":
        body = r"""
For a Euclidean configuration with action \(S_E=8\pi^2/g^2\), its contribution is proportional to \(e^{-8\pi^2/g^2}\).  Differentiating any finite number of times with respect to \(g\) near \(g=0\) cannot turn a power series into this exponential.  The effect is therefore invisible in ordinary perturbation theory around the vacuum.
"""
    elif family == "standard":
        body = r"""
Check a charged-lepton Yukawa term.  The left-handed lepton \(L\) is an \(SU(2)\) doublet, the Higgs field \(\Phi\) is a doublet, and \(e_R\) is a singlet.  Contract the two doublet indices and choose hypercharges so the sum is zero.  After \(\Phi\) gets a vacuum value, the term becomes \(m_e\bar e e\) with \(m_e=y_ev/\sqrt2\).
"""
    else:
        body = fr"""
For \(f(x)=x^2\sin({n}x)\), the derivative is \(2x\sin({n}x)+{n}x^2\cos({n}x)\).  The two terms have different origins: one differentiates the slowly varying envelope, and one differentiates the oscillation.  Separating these origins is the same habit used later with fields and modes.
"""
    body = contextualize_paragraphs(body, context)
    return f"""\\begin{{example}}[A worked calculation for {topic}]
{body.strip()}
\\end{{example}}
"""


def exercises(chapter_title: str, section_no: int, chapter_no: int) -> str:
    family = family_for(chapter_title)
    topic = tex_escape(f"{chapter_title}: {section_title(chapter_title, section_no)}")
    n = chapter_no + section_no + 1
    if family == "geometry":
        q1 = r"For \(\bm v=(2,-1,2)\), compute its length in an orthonormal basis."
        a1 = r"The length is \(\sqrt{2^2+(-1)^2+2^2}=3\)."
        q2 = r"Let \(\hat n=(0,1)\) and \(\bm v=(5,-2)\).  Compute the projection of \(\bm v\) onto \(\hat n\)."
        a2 = r"The coefficient is \(\bm v\cdot\hat n=-2\), so the projected vector is \((0,-2)\)."
    elif family == "fourier":
        q1 = r"Using \(f(x)=\cos nx\) on \((-\pi,\pi)\), compute its complex Fourier coefficients."
        a1 = r"Only the coefficients at \(m=\pm n\) are nonzero; each is \(1/2\), with the convention \(f=\sum c_me^{\ii mx}\)."
        q2 = r"Show that differentiating \(e^{\ii kx}\) twice turns \(-\dd^2/\dd x^2\) into multiplication by \(k^2\)."
        a2 = r"Two derivatives give \((\ii k)^2e^{\ii kx}=-k^2e^{\ii kx}\), so the extra minus sign gives \(k^2\)."
    elif family == "variation":
        q1 = r"Derive the Euler-Lagrange equation for \(L=\frac12\dot q^2-U(q)\)."
        a1 = r"The equation is \(\ddot q+U'(q)=0\), after varying the action and integrating the \(\dot\eta\) term by parts."
        q2 = r"Explain what changes if the endpoint variation \(\eta(t_f)\) is not forced to vanish."
        a2 = r"The boundary term remains and gives a natural boundary condition involving \(\p L/\p\dot q\) at \(t_f\)."
    elif family == "mechanics":
        q1 = r"For \(H=p^2/2m+kq^2/2\), use Hamilton's equations to recover the oscillator equation."
        a1 = r"\(\dot q=p/m\), \(\dot p=-kq\), hence \(m\ddot q=-kq\)."
        q2 = r"Compute \(\{q,p^2\}\) for one degree of freedom."
        a2 = r"\(\{q,p^2\}=2p\), since \(\p q/\p q=1\) and \(\p p^2/\p p=2p\)."
    elif family == "oscillator":
        q1 = r"Using \([a,a^\dagger]=1\), show that \([N,a^\dagger]=a^\dagger\)."
        a1 = r"\([a^\dagger a,a^\dagger]=a^\dagger[a,a^\dagger]=a^\dagger\)."
        q2 = r"Normalize \((a^\dagger)^2\ket0\)."
        a2 = r"The normalized state is \((a^\dagger)^2\ket0/\sqrt{2!}\)."
    elif family == "fields":
        q1 = r"Derive the conjugate momentum for \(\Lag=\frac12\dot\phi^2-\frac12|\nabla\phi|^2-\frac12m^2\phi^2\)."
        a1 = r"\(\pi=\p\Lag/\p\dot\phi=\dot\phi\)."
        q2 = r"Substitute a plane wave into the Klein-Gordon equation and find the dispersion relation."
        a2 = r"The result is \(E^2=\bm p^2+m^2\)."
    elif family == "relativity":
        q1 = r"Show that \(E^2-\bm p^2=m^2\) reduces to \(E\approx m+\bm p^2/2m\) for small \(|\bm p|/m\)."
        a1 = r"Expand \(E=m\sqrt{1+\bm p^2/m^2}\) to first order in \(\bm p^2/m^2\)."
        q2 = r"Verify that \(p_\mu x^\mu=Et-\bm p\cdot\bm x\) with the metric convention of this book."
        a2 = r"Lowering the spatial index changes the sign of the spatial components."
    elif family == "quantum":
        q1 = r"Normalize the vector \((1,2,\ii)\) in a three-dimensional Hilbert space."
        a1 = r"The norm squared is \(1+4+1=6\), so divide by \(\sqrt6\)."
        q2 = r"Give a simple reason why two noncommuting operators cannot always have the same eigenbasis."
        a2 = r"If they shared a complete eigenbasis, their products would act by the same scalar products on each basis vector and would commute."
    elif family == "path":
        q1 = r"Complete the square in \(-ax^2/2+Jx\)."
        a1 = r"It is \(-a(x-J/a)^2/2+J^2/(2a)\)."
        q2 = r"Differentiate \(e^{J^2/2a}\) twice and set \(J=0\)."
        a2 = r"The result is \(1/a\), the one-dimensional propagator of the Gaussian integral."
    elif family == "perturbation":
        q1 = r"Why does the factor \(1/4!\) in \(-\lambda\phi^4/4!\) disappear from the four-point vertex rule?"
        a1 = r"There are \(4!\) contractions connecting the four identical fields at the vertex to four external fields."
        q2 = r"State what LSZ removes from a connected correlation function."
        a2 = r"It removes the external propagator poles and leaves the on-shell scattering amplitude."
    elif family == "renormalization":
        q1 = r"Estimate the large-\(\Lambda\) behavior of \(\int^\Lambda k^3\dd k/(k^2+m^2)\)."
        a1 = r"It grows as \(\Lambda^2/2\) plus a logarithmic term."
        q2 = r"Explain why a mass counterterm can cancel a quadratic divergence in a scalar two-point function."
        a2 = r"The divergent part is local and has the same field structure as \(m^2\phi^2/2\)."
    elif family == "group":
        q1 = r"Compute \([\sigma^1/2,\sigma^2/2]\)."
        a1 = r"The result is \(\ii\sigma^3/2\)."
        q2 = r"Explain why a singlet term is invariant under a group transformation."
        a2 = r"All representation matrices are contracted so the transformed factors cancel to the identity."
    elif family == "spinor":
        q1 = r"Use the gamma-matrix anticommutator to show that \((\gamma^\mu p_\mu)^2=p^2\)."
        a1 = r"The antisymmetric part drops out against the symmetric product \(p_\mu p_\nu\)."
        q2 = r"How many positive-energy rest spinors does the Dirac equation have?"
        a2 = r"Two, corresponding to the two spin states of a massive spin-one-half particle."
    elif family == "abelian":
        q1 = r"Show that \(D_\mu\psi\) transforms like \(\psi\) under a local \(U(1)\) phase."
        a1 = r"Use \(A_\mu\to A_\mu+\p_\mu\alpha\); the derivative of the phase cancels the gauge-field shift."
        q2 = r"Why is \(F_{\mu\nu}\) gauge invariant in Abelian gauge theory?"
        a2 = r"The extra terms are mixed partial derivatives with opposite signs."
    elif family == "nonabelian":
        q1 = r"Set \(f^{abc}=0\) in the non-Abelian field strength.  What remains?"
        a1 = r"The Abelian field strength \(\p_\mu A_\nu^a-\p_\nu A_\mu^a\) for each component."
        q2 = r"Why do ghosts interact in Yang-Mills theory?"
        a2 = r"The Faddeev-Popov operator contains the covariant derivative, which contains \(A_\mu\)."
    elif family == "broken":
        q1 = r"Find the minima of \(V=\lambda(\phi^2-v^2)^2/4\)."
        a1 = r"They satisfy \(\phi=\pm v\) for one real field, or \(|\Phi|=v/\sqrt2\) for the usual complex field normalization."
        q2 = r"Why is a Goldstone mode massless before gauging?"
        a2 = r"It is a fluctuation along a flat direction of the potential, so there is no quadratic restoring term."
    elif family == "nonperturbative":
        q1 = r"Explain why \(e^{-1/g^2}\) is not visible in a power series in \(g\) around \(g=0\)."
        a1 = r"All derivatives at \(g=0\) vanish in the asymptotic sense, so no finite Taylor coefficient detects it."
        q2 = r"What does an area law for a large Wilson loop indicate?"
        a2 = r"It indicates confinement: the energy cost grows with the area spanned by the loop, leading to a linear potential."
    elif family == "standard":
        q1 = r"State the Standard Model gauge group."
        a1 = r"\(SU(3)_c\times SU(2)_L\times U(1)_Y\)."
        q2 = r"Why must hypercharges in an interaction term sum to zero?"
        a2 = r"Otherwise the term picks up a local \(U(1)_Y\) phase and is not gauge invariant."
    else:
        q1 = fr"Differentiate \(x^2e^{{-{n}x^2}}\) and identify the two sources of terms."
        a1 = fr"\(2xe^{{-{n}x^2}}-2\cdot {n}x^3e^{{-{n}x^2}}\); the two terms come from \(x^2\) and from the exponential."
        q2 = r"State the integration-by-parts formula used in this section."
        a2 = r"\(\int u'v=[uv]-\int uv'\), with limits or boundary conditions supplied by the problem."
    return f"""\\begin{{exercise}}
{q1}  Use the notation of {topic}.
\\begin{{answer}}
{a1}
\\end{{answer}}
\\end{{exercise}}

\\begin{{exercise}}
{q2}  Use the notation of {topic}.
\\begin{{answer}}
{a2}
\\end{{answer}}
\\end{{exercise}}
"""


def cumulative_section(chapter_title: str, keywords: str, chapter_no: int) -> str:
    family = family_for(chapter_title)
    data = DATA[family]
    chapter_e = tex_escape(chapter_title)
    keywords_e = tex_escape(keywords)
    context = tex_escape(f"{chapter_title}, cumulative derivation")
    first = tex_escape(data["focuses"][0])
    middle = tex_escape(data["focuses"][3])
    last = tex_escape(data["focuses"][6])
    eqs = equation_block(family)
    if family == "fourier":
        body = r"""
Start with a source \(\rho(x)\) on a line and solve \((-\dd^2/\dd x^2+m^2)u(x)=\rho(x)\).  Fourier transform both sides.  The derivative term becomes \(k^2\tilde u(k)\), so
\[
  (k^2+m^2)\tilde u(k)=\tilde\rho(k).
\]
The inverse transform gives
\[
  u(x)=\int\dd y\,G(x-y)\rho(y),
  \qquad
  G(x-y)=\int\frac{\dd k}{2\pi}\frac{e^{\ii k(x-y)}}{k^2+m^2}.
\]
Thus a differential equation has become multiplication in momentum space and convolution in position space.  This is the same structural move that later turns the Klein-Gordon operator into the Feynman propagator.
"""
    elif family == "variation":
        body = r"""
Take a real field in one space dimension with
\[
  S[\phi]=\int\dd t\,\dd x\left[
  \frac12\dot\phi^2-\frac12(\p_x\phi)^2-V(\phi)
  \right].
\]
Vary the field by \(\phi\to\phi+\epsilon\eta\).  The first-order change is
\[
  \delta S=\int\dd t\,\dd x\left[
  \dot\phi\,\dot\eta-(\p_x\phi)(\p_x\eta)-V'(\phi)\eta
  \right].
\]
Integrating by parts in both \(t\) and \(x\), and stating that the surface terms vanish, gives
\[
  \delta S=-\int\dd t\,\dd x\,
  \left[\ddot\phi-\p_x^2\phi+V'(\phi)\right]\eta.
\]
Because \(\eta\) is arbitrary, the field equation follows point by point.
"""
    elif family == "mechanics":
        body = r"""
For a two-coordinate system with \(L=\frac12m(\dot q_1^2+\dot q_2^2)-V(q_1,q_2)\), the momenta are \(p_i=m\dot q_i\).  The Hamiltonian is
\[
  H=\frac{p_1^2+p_2^2}{2m}+V(q_1,q_2).
\]
Hamilton's equations give \(\dot q_i=p_i/m\) and \(\dot p_i=-\p V/\p q_i\).  Combining them returns \(m\ddot q_i=-\p V/\p q_i\).  The payoff is not merely a new notation: phase space makes conserved quantities and Poisson brackets visible.
"""
    elif family == "oscillator":
        body = r"""
For a chain of \(N\) equal masses with nearest-neighbor springs, try normal coordinates
\[
  q_j(t)=\frac1{\sqrt N}\sum_n Q_n(t)e^{2\pi\ii nj/N}.
\]
Orthogonality of the discrete waves diagonalizes the quadratic energy.  The result is a sum of independent oscillator Hamiltonians,
\[
  H=\sum_n\left(\frac12|P_n|^2+\frac12\omega_n^2|Q_n|^2\right).
\]
Quantization now repeats the one-oscillator construction for every \(n\).  The field limit is the limit in which the mode label becomes a momentum.
"""
    elif family == "fields":
        body = r"""
Place the scalar field in a box first.  The allowed momenta are discrete, and the field expansion is a sum of oscillator modes.  The canonical commutator
\[
  [\phi(t,\bm x),\pi(t,\bm y)]=\ii\delta^{(3)}(\bm x-\bm y)
\]
fixes the normalization of the creation and annihilation operators.  The Hamiltonian becomes
\[
  H=\sum_{\bm p}E_{\bm p}\left(a_{\bm p}^\dagger a_{\bm p}+\frac12\right)
\]
before the continuum limit is taken.  This order of steps keeps the delta functions from appearing as magic constants.
"""
    elif family == "relativity":
        body = r"""
Build a scalar wave equation by combining the invariant \(p_\mu p^\mu=m^2\) with the Fourier substitution \(p_\mu\to\ii\p_\mu\).  The result is
\[
  (\Boxop+m^2)\phi=0.
\]
The equation is Lorentz covariant because \(\Boxop=\p_\mu\p^\mu\) is a scalar operator.  In the nonrelativistic limit, writing \(E=m+\epsilon\) and keeping the leading small energy \(\epsilon\) recovers the familiar kinetic energy \(\bm p^2/2m\).  The relativistic notation therefore contains the older mechanics as an approximation.
"""
    elif family == "quantum":
        body = r"""
Let \(H\ket n=E_n\ket n\) and expand a state as \(\ket{\psi(t)}=\sum_nc_n(t)\ket n\).  The Schrödinger equation gives
\[
  \ii\dot c_n(t)=E_nc_n(t),
\]
so \(c_n(t)=c_n(0)e^{-\ii E_nt}\).  A perturbation adds off-diagonal matrix elements, and those matrix elements become transition amplitudes.  In QFT the same structure reappears with \(n\) replaced by many-particle occupation labels.
"""
    elif family == "path":
        body = r"""
Time-slice a transition amplitude into \(N\) short factors.  Insert position identities between them, then insert momentum identities inside each short factor.  For a Hamiltonian \(p^2/2m+V(q)\), the momentum integral is Gaussian and yields
\[
  \exp\left[\ii\Delta t\left(
  \frac{m}{2}\left(\frac{q_{j+1}-q_j}{\Delta t}\right)^2-V(q_j)
  \right)\right].
\]
Multiplying all slices produces \(\exp(\ii S)\) in the continuum limit.  The path integral is therefore a limit of ordinary integrals, not a separate postulate.
"""
    elif family == "perturbation":
        body = r"""
Compute the connected four-point function in \(\lambda\phi^4\) theory to first order.  Expand the interaction exponential once.  Contract the four fields at the interaction point with the four external fields.  The \(4!\) possible contractions cancel the \(1/4!\) in the Lagrangian.  The result is
\[
  G_4^{(1)}(x_1,x_2,x_3,x_4)=
  -\ii\lambda\int\dd^4z\,\prod_{r=1}^4\Delta_F(x_r-z).
\]
Fourier transforming this expression gives momentum conservation at the vertex and the vertex factor \(-\ii\lambda\).
"""
    elif family == "renormalization":
        body = r"""
Suppose a two-point function contains \(A\Lambda^2+B m^2\log\Lambda\) plus finite terms.  Add a counterterm \(-\frac12\delta m^2\phi^2\).  A renormalization condition, such as fixing the pole at \(p^2=m_{\mathrm{phys}}^2\), determines \(\delta m^2\).  Changing the subtraction scale while keeping the measured mass fixed forces the renormalized parameter to change.  That forced change is the renormalization group in its most concrete form.
"""
    elif family == "group":
        body = r"""
Let a field transform as \(\phi\to (1-\ii\alpha^aT^a)\phi\).  If the Lagrangian is invariant for constant \(\alpha^a\), then making \(\alpha^a\) weakly position dependent isolates the current:
\[
  \delta\Lag=-(\p_\mu\alpha^a)j^\mu_a.
\]
Integrating by parts in the action gives \(\delta S=\int\alpha^a\p_\mu j^\mu_a\), so invariance for arbitrary \(\alpha^a\) implies \(\p_\mu j^\mu_a=0\).  This is Noether's theorem in the representation language used by gauge theory.
"""
    elif family == "spinor":
        body = r"""
Starting from \((\ii\gamma^\mu\p_\mu-m)\psi=0\), multiply by \((\ii\gamma^\nu\p_\nu+m)\).  The gamma anticommutator reduces the second-order operator to \(-\Boxop-m^2\), so every spinor component satisfies the Klein-Gordon equation.  The first-order equation contains more information: it ties components together and carries a representation of Lorentz transformations that scalar fields do not carry.
"""
    elif family == "abelian":
        body = r"""
Begin with global phase invariance of the Dirac field.  Making the phase local produces an unwanted \(\p_\mu\alpha\) term.  Introducing \(A_\mu\) and \(D_\mu=\p_\mu+\ii qA_\mu\) cancels that term exactly if \(A_\mu\to A_\mu+\p_\mu\alpha\).  Varying the gauge action then gives \(\p_\mu F^{\mu\nu}=j^\nu\).  Quantizing the quadratic part after gauge fixing gives the photon propagator, while the covariant derivative gives the QED vertex.
"""
    elif family == "nonabelian":
        body = r"""
Repeat the Abelian construction with a matrix \(U(x)\).  Because matrices do not commute, the commutator of covariant derivatives contains \([A_\mu,A_\nu]\).  That term makes \(F_{\mu\nu}\) nonlinear in \(A_\mu\), and the Yang-Mills action contains cubic and quartic gauge-field interactions.  Gauge fixing the path integral produces a determinant; representing that determinant by anticommuting fields gives Faddeev-Popov ghosts.
"""
    elif family == "broken":
        body = r"""
A potential with a continuous set of minima has directions along which the quadratic restoring force vanishes.  Expanding around one chosen vacuum separates radial and angular fluctuations.  In a global theory the angular fields are Goldstone bosons.  In a gauge theory the covariant derivative mixes those angular fields with \(A_\mu\), and a gauge choice moves the would-be Goldstone mode into the longitudinal polarization of a massive gauge boson.
"""
    elif family == "nonperturbative":
        body = r"""
Perturbation theory expands around one saddle.  Nonperturbative physics asks whether other sectors contribute.  In Euclidean gauge theory, finite-action configurations can carry integer topological charge.  Their contributions scale like \(\exp(-\hbox{constant}/g^2)\), which no power series in \(g\) can reproduce.  On the lattice, Wilson loops provide a different nonperturbative probe: area-law behavior signals confinement.
"""
    elif family == "standard":
        body = r"""
Read the Standard Model as a worked exercise in allowed local terms.  The gauge group fixes the covariant derivatives.  The matter representations decide which bilinears can be formed.  The Higgs representation allows Yukawa terms and breaks \(SU(2)_L\times U(1)_Y\) to electromagnetism.  Renormalization explains why the same Lagrangian can be used at different scales, while effective operators record possible short-distance physics not resolved by the theory.
"""
    else:
        body = r"""
Choose a small change, compute the linear term, check units, and then ask whether the same operation survives a limiting process.  This is the common skeleton behind derivatives, matrix actions, Fourier transforms, and field variations.  The notation grows, but the controlling questions remain the same: what is varied, what is fixed, which boundary term is used, and what finite calculation is being approximated?
"""
    body = contextualize_paragraphs(body, context)
    return f"""\\section{{Cumulative worked derivation: from {first} to {last}}}

This final worked section braids together {first}, {middle}, and {last} for {chapter_e}.  The vocabulary of the chapter was {keywords_e}; here those words are used in one continuous calculation rather than in isolated fragments.

{body}

For reference, the compact formulas are

{eqs}

\\begin{{exercise}}
Reproduce the cumulative derivation for {chapter_e} without looking at the prose.  Mark the step where a finite calculation becomes a continuum, operator, or field-theoretic statement.
\\begin{{answer}}
The reconstruction should name the starting object, carry out the differentiating, varying, transforming, or commuting step explicitly, and state the normalization or boundary condition that makes the final formula meaningful.
\\end{{answer}}
\\end{{exercise}}
"""


PART_REVIEW = {
    "Calculus, Space, and Mathematical Language": r"""
\chapter{Part I Review: From Calculus to Field Notation}

This review connects the first mathematical tools.  A derivative begins as a limit of differences; a vector begins as an object whose components depend on a basis; a Fourier coefficient begins as a projection onto a wave.  These are not separate tricks.  They are all ways of extracting one controlled component from a larger object.

\section{A guided reconstruction}

Start with a function sampled on a grid.  Differences approximate derivatives, sums approximate integrals, and dot products approximate projections.  Passing to the continuum changes the notation but not the logic:
\[
  \sum_j f_jg_j\Delta x\longrightarrow \int f(x)g(x)\dd x.
\]
Fourier analysis then says that the waves \(e^{\ii kx}\) are a basis adapted to translations.  A derivative is diagonal in that basis because \(\dd e^{\ii kx}/\dd x=\ii k e^{\ii kx}\).

\begin{exercise}
Explain in one page how projection, Fourier coefficients, and the delta function are three versions of the same idea.
\begin{answer}
Each isolates a component: projection isolates a vector component, a Fourier coefficient isolates a wave component, and the delta function isolates the value of a test function at a point.
\end{answer}
\end{exercise}
""",
    "Classical Mechanics and Classical Fields": r"""
\chapter{Part II Review: Actions, Waves, and Conservation}

The action principle turns a global quantity into a local equation.  The required step is always the same: vary the object, integrate by parts, state the boundary condition, and use the arbitrariness of the remaining variation.

\section{A guided reconstruction}

For a path \(q(t)\), stationarity gives the Euler-Lagrange equation.  For a field \(\phi(t,\bm x)\), the same derivation has one integration by parts for each coordinate:
\[
  \frac{\p\Lag}{\p\phi}-\p_\mu\frac{\p\Lag}{\p(\p_\mu\phi)}=0.
\]
When the action is invariant under a continuous transformation, the coefficient of the local version of the transformation is a conserved current.

\begin{exercise}
Derive the field Euler-Lagrange equation from an action \(S=\int\dd^4x\,\Lag(\phi,\p_\mu\phi)\).
\begin{answer}
Vary \(\phi\), integrate the \(\p_\mu\delta\phi\) term by parts, discard the stated surface term, and set the coefficient of arbitrary \(\delta\phi\) to zero.
\end{answer}
\end{exercise}
""",
    "Relativity and Quantum Mechanics Built for Fields": r"""
\chapter{Part III Review: Invariance, Amplitudes, and Oscillators}

Relativity identifies the invariant spacetime interval.  Quantum mechanics identifies states as complex amplitude vectors.  The harmonic oscillator supplies the algebraic unit that will later appear once for every field mode.

\section{A guided reconstruction}

The mass shell \(p_\mu p^\mu=m^2\) and the commutator \([q,p]=\ii\) are both compact statements with long consequences.  The first constrains the form of relativistic wave equations; the second produces ladder operators and a discrete spectrum:
\[
  H=\omega\left(a^\dagger a+\frac12\right).
\]
Together they prepare the statement that a free relativistic field is a collection of quantum oscillators labelled by momentum.

\begin{exercise}
Explain why the oscillator spectrum is needed before the particle interpretation of a free field can be built.
\begin{answer}
Each momentum mode of the free field is an oscillator, and its occupation number becomes the number of particles in that mode.
\end{answer}
\end{exercise}
""",
    "Free Quantum Fields": r"""
\chapter{Part IV Review: From Modes to Particles}

The free scalar field is a continuum limit of many coupled oscillators.  Quantization promotes the mode amplitudes to operators, and the creation operators build Fock space.

\section{A guided reconstruction}

Start in a finite box, where momenta are discrete.  Normalize the modes so that
\[
  [a_{\bm p},a_{\bm q}^\dagger]=\delta_{\bm p\bm q}.
\]
Only after this finite normalization is clear should one take the continuum limit and replace Kronecker deltas by Dirac deltas.  The propagator is the Green function of the quantized field equation with the Feynman boundary condition.

\begin{exercise}
Why is it safer to quantize in a box before writing continuum delta functions?
\begin{answer}
The box gives ordinary sums and Kronecker deltas, making normalization explicit before the continuum limit introduces distributions.
\end{answer}
\end{exercise}
""",
    "Interactions and Perturbative Quantum Field Theory": r"""
\chapter{Part V Review: Correlators, Diagrams, and Scattering}

Perturbation theory is a controlled expansion around the Gaussian integral.  Wick's theorem is the combinatorics of that Gaussian, and Feynman diagrams are a compact record of the resulting terms.

\section{A guided reconstruction}

For \(\lambda\phi^4\), one vertex contributes \(-\ii\lambda\).  Propagators connect the vertex to other points or to other vertices.  LSZ then explains why poles of correlation functions are related to scattering amplitudes.  The slogan is short, but the derivation is a chain: source derivatives, contractions, Fourier transforms, pole residues, and phase-space normalization.

\begin{exercise}
List the steps that turn a four-point correlation function into a scattering amplitude.
\begin{answer}
Compute the connected correlator, Fourier transform, identify external poles, amputate the external propagators, put external momenta on shell, and include the correct normalization conventions.
\end{answer}
\end{exercise}
""",
    "Renormalization and Effective Field Theory": r"""
\chapter{Part VI Review: Scales and Locality}

Renormalization is the statement that short-distance sensitivity can be absorbed into local terms already present, or into higher-dimension terms organized by an effective expansion.

\section{A guided reconstruction}

A divergent loop integral is not yet an observable.  A measured condition fixes a renormalized parameter, and a counterterm absorbs regulator dependence.  If the subtraction scale changes while the observable is held fixed, the coupling runs:
\[
  \mu\frac{\dd g}{\dd\mu}=\beta(g).
\]
Wilsonian language makes the same idea physical by integrating out high-momentum modes and watching the coefficients of operators change.

\begin{exercise}
Explain the difference between a regulator, a counterterm, and a renormalization condition.
\begin{answer}
A regulator makes an integral defined, a counterterm absorbs regulator dependence, and a renormalization condition ties the finite parameter to a measured quantity.
\end{answer}
\end{exercise}
""",
    "Symmetry and Gauge Theory": r"""
\chapter{Part VII Review: Symmetry Made Local}

Global symmetry gives conserved currents.  Local symmetry requires a gauge field.  The covariant derivative is the object that differentiates a field without losing its transformation law.

\section{A guided reconstruction}

For an Abelian phase, \(D_\mu=\p_\mu+\ii qA_\mu\).  For a non-Abelian matrix transformation, the same demand gives a matrix-valued gauge field and a field strength with a commutator term.  Spinor fields provide the matter representation needed for QED and the Standard Model.

\begin{exercise}
Derive the Abelian gauge-field transformation from the demand that \(D_\mu\psi\) transform like \(\psi\).
\begin{answer}
Differentiate the local phase, observe the unwanted \(\p_\mu\alpha\) term, and choose \(A_\mu\to A_\mu+\p_\mu\alpha\) to cancel it.
\end{answer}
\end{exercise}
""",
    "Non-Abelian Theory, Broken Symmetry, and Advanced Topics": r"""
\chapter{Part VIII Review: Beyond Perturbative Gauge Theory}

The final part adds three ideas that cannot be reduced to a single Feynman rule: gauge redundancy in non-Abelian theories, symmetry breaking, and nonperturbative sectors.

\section{A guided reconstruction}

The Yang-Mills field strength contains a commutator, so gauge bosons self-interact.  Gauge fixing introduces ghost fields in covariant gauges.  Spontaneous symmetry breaking reorganizes degrees of freedom around a chosen vacuum.  Nonperturbative physics then asks what is missed by expanding around only one saddle.

\begin{exercise}
Explain why instanton-like contributions are invisible in a power series in \(g\).
\begin{answer}
They scale like \(\exp(-\hbox{constant}/g^2)\), which cannot be reproduced by any finite Taylor series in powers of \(g\) around \(g=0\).
\end{answer}
\end{exercise}
""",
}


def chapter_intro(part_title: str, chapter_title: str, keywords: str, chapter_no: int) -> str:
    family = family_for(chapter_title)
    data = DATA[family]
    part_e = tex_escape(part_title)
    chapter_e = tex_escape(chapter_title)
    keywords_e = tex_escape(keywords)
    focus = tex_escape(data["focuses"][0])
    return f"""\\chapter{{{chapter_e}}}

\\chapterquote{{A field-theory formula is useful only after the smaller calculation inside it is visible.}}

This chapter is part of \\emph{{{part_e}}}.  The working vocabulary is {keywords_e}.  The first pass through the chapter should be slow: identify the object being changed, the condition held fixed, and the reason a boundary term or normalization is allowed.  The first concrete theme is {focus}; later sections reuse the same habit in a more compact notation.

For {chapter_e}, the calculus-level starting point is tied to {focus}.  Matrices, waves, operators, fields, and gauge variables are introduced only as the calculation requires them.  A formula is accepted after it has been checked in a finite model, differentiated or varied explicitly, and connected to the field-theoretic use that motivates it.
"""


def make_chapter(part_title: str, chapter_title: str, keywords: str, chapter_no: int) -> str:
    pieces = [chapter_intro(part_title, chapter_title, keywords, chapter_no)]
    for section_no in range(1, 9):
        title = section_title(chapter_title, section_no)
        pieces.append(f"\\section{{{tex_escape(title)}}}\n")
        pieces.append(long_explanation(chapter_title, section_no, keywords))
        pieces.append("\n\n")
        pieces.append(derivation_text(chapter_title, section_no))
        pieces.append("\n\n")
        pieces.append(example_block(chapter_title, section_no, chapter_no))
        pieces.append("\n")
        pieces.append(exercises(chapter_title, section_no, chapter_no))
        pieces.append("\n")
    pieces.append(cumulative_section(chapter_title, keywords, chapter_no))
    pieces.append("\n")
    pieces.append(f"""\\section{{Chapter synthesis}}

This chapter has treated {tex_escape(chapter_title.lower())} as a chain of calculations.  The safest summary is not a list of final formulas, but a map from assumptions to equations: finite model, limiting step, boundary condition, normalization, and field-theory use.  If one of those links is missing, the formula should be rederived before it is used in a later chapter.

\\begin{{exercise}}
Write a one-page reconstruction of {tex_escape(chapter_title.lower())}.  Include one equation from the finite model, one equation from the continuum or operator form, and one sentence explaining how the two are connected.
\\begin{{answer}}
A strong reconstruction names the basic objects, identifies the central derivative, variation, commutator, or symmetry operation, and states the assumption that allows the finite calculation to become the field-theory formula.
\\end{{answer}}
\\end{{exercise}}
""")
    return "\n".join(pieces)


def write_main(chapter_paths: list[tuple[str, str]]) -> None:
    lines = [
        r"\documentclass[11pt,oneside]{book}",
        r"\usepackage{qftcalc}",
        "",
        r"\title{\Huge Quantum Field Theory from Calculus\\[0.45em]",
        r"\Large A Self-Contained, Derivation-Based Course from Classical Fields to Gauge Theory}",
        r"\author{}",
        r"\date{}",
        "",
        r"\begin{document}",
        r"\frontmatter",
        r"\hypersetup{pageanchor=false}",
        r"\maketitle",
        r"\clearpage",
        r"\hypersetup{pageanchor=true}",
        r"\setcounter{page}{1}",
        r"\include{frontmatter/preface}",
        r"\tableofcontents",
        "",
        r"\mainmatter",
    ]
    last_part = None
    emitted_reviews: set[str] = set()
    for idx, (include_path, part_title) in enumerate(chapter_paths):
        if part_title != last_part:
            lines.append(r"\part{" + tex_escape(part_title) + "}")
            last_part = part_title
        lines.append(r"\include{" + include_path + "}")
        next_part = chapter_paths[idx + 1][1] if idx + 1 < len(chapter_paths) else None
        if part_title != next_part and part_title not in emitted_reviews:
            review_slug = f"partreview{len(emitted_reviews) + 1:02d}"
            lines.append(r"\include{chaptersfull/" + review_slug + "}")
            emitted_reviews.add(part_title)
    lines.extend(
        [
            "",
            r"\appendix",
            r"\include{appendicesfull/appnotebook}",
            r"\include{appendicesfull/appnotation}",
            r"\include{appendicesfull/appanswers}",
            "",
            r"\backmatter",
            r"\bibliographystyle{plain}",
            r"\nocite{noether1918,peskin1995,weinberg1995,zee2010,srednicki2007,schwartz2014,ryder1996}",
            r"\bibliography{references}",
            r"\end{document}",
            "",
        ]
    )
    (ROOT / "main.tex").write_text("\n".join(lines), encoding="utf-8")


def write_appendices() -> None:
    APPENDIX_DIR.mkdir(exist_ok=True)
    (APPENDIX_DIR / "appnotebook.tex").write_text(
        r"""\chapter{How to Work Through the Book}

This appendix is a practical guide for self-study.  The manuscript is long because the subject has many layers, but the working rhythm is simple.  For each section, copy the central derivation by hand, mark the boundary condition or normalization being used, and then solve one exercise without looking at the answer.  The goal is not speed.  The goal is to make each symbol accountable.

\section{A derivation log}

Keep a derivation log with four columns: formula, assumption, boundary condition, and check.  The formula is the line of mathematics being used.  The assumption records what is held fixed or treated as small.  The boundary condition records why a surface term vanishes or why it remains.  The check is a simple limit, dimensional test, or special case.

\section{When to move on}

Move on from a section when you can reproduce its central derivation without the prose.  You do not need to remember every symbol, but you should know why each derivative, commutator, source, or integral appears.  If a derivation still feels like a row of decorations, return to the finite model at the beginning of the section.
""",
        encoding="utf-8",
    )
    (APPENDIX_DIR / "appnotation.tex").write_text(
        r"""\chapter{Notation and Conventions}

\section{Spacetime}

The metric convention is \(\eta_{\mu\nu}=\operatorname{diag}(1,-1,-1,-1)\).  Four-vector products are written \(p\cdot x=p_\mu x^\mu=Et-\bm p\cdot\bm x\).  Natural units \(\hbar=c=1\) are used unless a section explicitly restores dimensions.

\section{Fourier transforms}

The four-dimensional convention is
\[
  f(x)=\int\frac{\dd^4p}{(2\pi)^4}\tilde f(p)e^{-\ii p\cdot x},
  \qquad
  \tilde f(p)=\int\dd^4x\,f(x)e^{\ii p\cdot x}.
\]

\section{Common propagators}

The scalar propagator is
\[
  \Delta_F(p)=\frac{\ii}{p^2-m^2+\ii\epsilon}.
\]
The Dirac propagator is
\[
  S_F(p)=\frac{\ii(\slashed p+m)}{p^2-m^2+\ii\epsilon}.
\]
The photon propagator in Feynman gauge is
\[
  D_{\mu\nu}(p)=\frac{-\ii\eta_{\mu\nu}}{p^2+\ii\epsilon}.
\]
""",
        encoding="utf-8",
    )
    (APPENDIX_DIR / "appanswers.tex").write_text(
        r"""\chapter{Using the Hints and Answers}

Most exercises include a short answer immediately after the problem.  The answer is meant to keep a self-studying reader from losing a day to a sign convention or a normalization factor.  When an answer gives a final formula, the missing work is usually an integration by parts, a Fourier transform, a matrix multiplication, a boundary-condition check, or a short expansion around a vacuum.

\section{A final checklist}

For every long calculation, check signs, units, limits, and symmetries.  A correct-looking formula that fails one of these tests should be rederived before it is trusted.
""",
        encoding="utf-8",
    )


def main() -> None:
    CHAPTER_DIR.mkdir(exist_ok=True)
    for old in CHAPTER_DIR.glob("*.tex"):
        old.unlink()
    for index, (part_title, text) in enumerate(PART_REVIEW.items(), start=1):
        (CHAPTER_DIR / f"partreview{index:02d}.tex").write_text(text, encoding="utf-8")
    chapter_paths: list[tuple[str, str]] = []
    chapter_no = 1
    for part_title, chapters in PARTS:
        for chapter_title, keywords in chapters:
            filename = f"ch{chapter_no:03d}{slug(chapter_title)}.tex"
            path = CHAPTER_DIR / filename
            path.write_text(make_chapter(part_title, chapter_title, keywords, chapter_no), encoding="utf-8")
            chapter_paths.append((f"chaptersfull/{filename[:-4]}", part_title))
            chapter_no += 1
    write_appendices()
    write_main(chapter_paths)
    print(f"Generated {chapter_no - 1} chapters in {CHAPTER_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
