#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG_ROOT = ROOT / "figures" / "instructional"
MANIFEST = FIG_ROOT / "manifest.json"

BEGIN_RE = re.compile(
    r"\n% QFTFIGURE-BEGIN .*?\n.*?% QFTFIGURE-END .*?\n",
    re.DOTALL,
)

CORE_CHAPTERS = {
    7,
    8,
    9,
    12,
    14,
    15,
    17,
    20,
    23,
    24,
    25,
    27,
    29,
    30,
    32,
    35,
    36,
    39,
    41,
    43,
    46,
    47,
    50,
    52,
    53,
    54,
    55,
    56,
}


@dataclass(frozen=True)
class FigureSpec:
    file: Path
    title: str
    chapter_number: int | None
    index: int
    slug: str
    concept: str
    caption: str
    motif: str

    @property
    def figure_id(self) -> str:
        stem = self.file.stem
        return f"{stem}-{self.index:02d}-{self.slug}"

    @property
    def label(self) -> str:
        return f"fig:{self.figure_id}"

    @property
    def image_rel(self) -> str:
        subdir = self.file.stem
        filename = f"{self.figure_id}.pdf"
        return f"figures/instructional/{subdir}/{filename}"

    @property
    def image_abs(self) -> Path:
        return ROOT / self.image_rel

    @property
    def background_rel(self) -> str:
        subdir = self.file.stem
        filename = f"{self.figure_id}.png"
        return f"figures/instructional/{subdir}/{filename}"

    @property
    def background_abs(self) -> Path:
        return ROOT / self.background_rel

    @property
    def latex_rel(self) -> str:
        subdir = self.file.stem
        filename = f"{self.figure_id}.tex"
        return f"figures/instructional/{subdir}/{filename}"

    @property
    def latex_abs(self) -> Path:
        return ROOT / self.latex_rel


def tex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def label_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def slugify(text: str, limit: int = 34) -> str:
    text = text.lower()
    text = text.replace("one-particle-irreducible", "one-particle")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:limit].strip("-") or "figure")


def chapter_files() -> list[Path]:
    includes = (ROOT / "main.tex").read_text(encoding="utf-8")
    result: list[Path] = []
    for match in re.finditer(r"\\include\{(chaptersfull/ch[^}]+)\}", includes):
        path = ROOT / f"{match.group(1)}.tex"
        if path.exists():
            result.append(path)
    return result


def review_files() -> list[Path]:
    includes = (ROOT / "main.tex").read_text(encoding="utf-8")
    result: list[Path] = []
    for match in re.finditer(r"\\include\{(chaptersfull/partreview[^}]+)\}", includes):
        path = ROOT / f"{match.group(1)}.tex"
        if path.exists():
            result.append(path)
    return result


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\\chapter\{(.+?)\}", text)
    if not match:
        return path.stem
    return match.group(1)


def chapter_number(path: Path) -> int | None:
    match = re.match(r"ch(\d+)", path.stem)
    return int(match.group(1)) if match else None


def family_for(title: str) -> str:
    t = title.lower()
    if "non-abelian" in t or "yang" in t:
        return "yang-mills"
    if "anomalies" in t or "topology" in t or "instantons" in t:
        return "nonperturbative"
    if "dirac" in t or "spinors" in t:
        return "dirac"
    if "calculus starting" in t:
        return "calculus"
    if "vectors" in t or "coordinates" in t:
        return "geometry"
    if "multivariable" in t:
        return "multicalculus"
    if "complex" in t and "scalar" not in t:
        return "complex"
    if "linear algebra" in t:
        return "linear"
    if "eigenvectors" in t or "hilbert" in t:
        return "hilbert"
    if "fourier" in t or "green" in t:
        return "fourier"
    if "variational" in t:
        return "variational"
    if "lagrangian" in t:
        return "lagrangian"
    if "hamiltonian" in t:
        return "hamiltonian"
    if "oscillator" in t or "continuum" in t:
        return "oscillator"
    if "classical scalar" in t:
        return "field"
    if "noether" in t or "stress" in t:
        return "noether"
    if "relativity" in t or "tensor" in t:
        return "relativity"
    if "maxwell" in t:
        return "maxwell"
    if "quantum states" in t or "operators" in t or "measurements" in t:
        return "quantum"
    if "angular" in t or " spin" in t or "identical" in t:
        return "spin"
    if "time evolution" in t:
        return "time-evolution"
    if "path integral" in t:
        return "path-integral"
    if "scalar field as infinite" in t or "klein-gordon" in t:
        return "free-field"
    if "fock" in t:
        return "fock"
    if "propagators" in t or "microcausality" in t:
        return "propagator"
    if "complex scalar" in t:
        return "charge"
    if "generating" in t:
        return "generating"
    if "wick" in t:
        return "wick"
    if "interacting scalar" in t:
        return "interacting"
    if "feynman" in t:
        return "feynman"
    if "scattering" in t:
        return "scattering"
    if "lsz" in t:
        return "lsz"
    if "loops" in t or "self-energy" in t:
        return "loops"
    if "cutoff" in t:
        return "cutoff"
    if "dimensional" in t:
        return "dimreg"
    if "counterterm" in t or "renormalization conditions" in t:
        return "counterterms"
    if "running" in t or "renormalization group" in t:
        return "rg"
    if "effective action" in t or "one-particle" in t:
        return "effective-action"
    if "wilsonian" in t:
        return "wilsonian"
    if "operator product" in t:
        return "ope"
    if "groups" in t or "lie algebra" in t:
        return "groups"
    if "representations" in t:
        return "representations"
    if "global symmetries" in t:
        return "global-symmetry"
    if "abelian" in t or "qed" in t or "ward" in t:
        return "qed"
    if "ghost" in t or "brst" in t:
        return "brst"
    if "spontaneous" in t:
        return "ssb"
    if "higgs" in t:
        return "higgs"
    if "lattice" in t or "finite temperature" in t:
        return "lattice"
    if "standard model" in t or "curved" in t:
        return "standard-model"
    return "generic"


BASE_BANK: dict[str, list[tuple[str, str, str, str]]] = {
    "calculus": [
        ("linear-approx", "local linear approximation", "The tangent picture shows how a small neighborhood turns a curved function into the first-order data that later becomes a local field equation.", "curve"),
        ("riemann-sum", "sums becoming integrals", "The rectangles emphasize that an integral is a controlled limit of finite bookkeeping, the same bookkeeping used before functional integrals are introduced.", "bars"),
        ("integration-parts", "boundary term separation", "The shaded edge pieces remind the reader that integration by parts moves a derivative only after the boundary contribution has been named.", "boundary"),
        ("error-scale", "error terms and scale", "The nested neighborhoods show why an approximation must say which terms shrink fastest as the scale of the calculation is reduced.", "nested"),
        ("dimension-flow", "dimensional bookkeeping", "The layered arrows show a calculation carrying units through each operation, preventing symbols from becoming detached from measured quantities.", "flow"),
        ("local-equation", "reading a differential equation locally", "The small stencil around one point previews how a field equation is assembled from neighboring values rather than from a memorized formula.", "stencil"),
    ],
    "geometry": [
        ("vector-arrow", "vector versus coordinates", "The fixed arrow with two coordinate grids separates the geometric object from the component lists used to describe it.", "vectors"),
        ("projection", "projection onto a basis", "The right-triangle projection makes the dot product visible as the amount of one direction contained in another.", "projection"),
        ("basis-change", "basis change", "The rotated grids show that components can change while the vector and its physical length remain unchanged.", "rotated-grid"),
        ("metric-length", "length from an inner product", "The ellipse of equal length illustrates how a metric turns coordinate differences into invariant geometric measurements.", "ellipse"),
        ("frame-field", "local frames", "The small frames at different points preview the habit of attaching coordinate systems locally before writing tensor or spinor equations.", "frame-field"),
        ("invariant", "geometric invariant", "The unchanged contour under two coordinate descriptions shows what later counts as a scalar statement in field theory.", "contour"),
    ],
    "multicalculus": [
        ("gradient", "gradient as steepest change", "The arrows climbing the surface show that the gradient points toward the fastest local increase, not merely toward larger coordinate values.", "surface-gradient"),
        ("flux", "flux through a surface", "The streamlines crossing a small surface patch make divergence theorem bookkeeping concrete before it is used in field equations.", "flux"),
        ("curl", "curl as local rotation", "The tiny circulation loops show curl as the rotational tendency measured in a small neighborhood.", "curl"),
        ("jacobian", "Jacobian deformation", "The deformed grid shows why a change of variables must also transform the local volume element.", "deformed-grid"),
        ("field-samples", "field values over space", "The sampled height field turns a function of position into many coupled values, the first visual step toward field configurations.", "field-surface"),
        ("boundary-volume", "boundary and volume data", "The highlighted boundary around a region keeps surface terms visually tied to the volume calculation they came from.", "boundary"),
    ],
    "complex": [
        ("phase-circle", "complex phase rotation", "The rotating phasor shows how multiplication by a complex exponential is a rotation with a controlled magnitude.", "phase"),
        ("oscillation", "oscillation from rotation", "The shadow of circular motion onto a line connects sinusoidal motion with the complex exponential notation used throughout Fourier analysis.", "wave"),
        ("interference", "adding complex amplitudes", "The vector sum shows why phases can reinforce or cancel even when magnitudes are individually positive.", "phasor-sum"),
        ("mode", "single frequency mode", "The clean wave train isolates one mode before many modes are superposed into a signal.", "wave"),
        ("spectrum", "frequency spectrum", "The separated peaks show how a complicated signal can be read by its mode content rather than by its point values alone.", "spectrum"),
        ("normalization", "amplitude normalization", "The envelope around the oscillation makes the size of a mode a separate piece of information from its phase.", "wave-envelope"),
    ],
    "linear": [
        ("linear-map", "linear map deformation", "The square becoming a parallelogram gives a concrete picture of a matrix acting on all vectors at once.", "linear-map"),
        ("elimination", "elimination as row motion", "The triangular array suggests how elimination reorganizes equations while preserving the solution set.", "matrix"),
        ("determinant", "area scaling", "The before-and-after cell areas show determinant as local volume scaling rather than a mysterious formula.", "deformed-grid"),
        ("eigenvector", "eigenvector direction", "The invariant line through the deformation shows an eigenvector as a direction preserved by the transformation.", "eigen"),
        ("orthogonal", "orthogonal decomposition", "The perpendicular components show how a vector is resolved into independent pieces that can be measured separately.", "projection"),
        ("operator-view", "matrix as operator", "The flow of many arrows under one rule prepares the reader to treat matrices and later differential operators in the same language.", "flow"),
    ],
    "hilbert": [
        ("eigenbasis", "eigenbasis expansion", "The separated basis directions show a state decomposed into modes with independently measurable weights.", "basis-rays"),
        ("orthogonality", "orthogonality", "The crossing axes and isolated projections make orthogonality visible as zero overlap rather than spatial distance alone.", "projection"),
        ("spectrum", "discrete spectrum", "The vertical levels preview how an operator can be understood by the states on which it acts most simply.", "ladder"),
        ("completeness", "complete basis", "The fan of basis rays suggests how many simple directions can reconstruct a more complicated state.", "basis-rays"),
        ("inner-product", "inner product as overlap", "The overlapping wave shapes show the inner product as a measure of alignment between two states.", "overlap-waves"),
        ("hilbert-geometry", "geometry of states", "The normalized arc emphasizes that quantum states live in a geometry where direction and overlap matter.", "state-arc"),
    ],
    "fourier": [
        ("mode-sum", "Fourier mode sum", "The stack of simple waves building a localized packet shows how local structure can be made from delocalized modes.", "fourier-stack"),
        ("delta-sequence", "delta sequence", "The narrowing peaks make the delta function a limiting rule under an integral, not an ordinary tall function.", "delta"),
        ("green-source", "Green function response", "The point source and spreading response show a Green function as the field produced by a unit localized disturbance.", "green"),
        ("box-to-line", "box modes approaching continuum", "The increasingly dense mode markers visualize how discrete momenta become a continuum when the box is enlarged.", "spectrum"),
        ("derivative-modes", "derivative on modes", "The phase-shifted waves show why derivatives become multiplication by momentum in Fourier space.", "wave-pair"),
        ("boundary-condition", "boundary conditions selecting modes", "The allowed standing waves make the boundary condition visible as a selector of the spectrum.", "standing-waves"),
    ],
    "variational": [
        ("path-family", "nearby paths", "The family of paths around one curve shows a variation as a controlled comparison among neighboring histories.", "paths"),
        ("stationary-action", "stationary action", "The valley surface shows why the physical path is found by a stationarity condition rather than by minimizing every local quantity.", "action-valley"),
        ("boundary-fixed", "fixed endpoints", "The pinned endpoints make clear which variations are allowed when boundary terms are set aside.", "paths-fixed"),
        ("euler-lagrange", "Euler-Lagrange balance", "The opposing local arrows show the balance between direct dependence and derivative dependence in the Euler-Lagrange equation.", "balance"),
        ("field-variation", "field variation", "The two nearby surfaces show that varying a field means changing many position-labelled variables at once.", "two-surfaces"),
        ("surface-term", "surface term", "The highlighted boundary band keeps the discarded or retained surface contribution visually present.", "boundary"),
    ],
    "lagrangian": [
        ("configuration-path", "path in configuration space", "The curve through configuration space shows mechanics as a problem of comparing entire histories, not isolated positions.", "paths"),
        ("action-landscape", "action landscape", "The valley picture separates stationary action from a naive force diagram and prepares the variational derivation.", "action-valley"),
        ("generalized-coordinate", "generalized coordinates", "The curved coordinate grid shows why coordinates can be chosen for the problem rather than inherited from a fixed room.", "curvilinear"),
        ("constraint", "constraint surface", "The path confined to a surface shows how constraints reduce the space of allowed motions.", "constraint"),
        ("energy-exchange", "kinetic and potential exchange", "The paired curves show energy moving between two forms while the total remains controlled.", "energy"),
        ("canonical-bridge", "bridge to canonical variables", "The split between position and momentum axes previews the move from Lagrangian histories to Hamiltonian phase space.", "phase-space"),
    ],
    "hamiltonian": [
        ("phase-flow", "phase-space flow", "The arrows in phase space show Hamiltonian evolution as a flow that moves states while preserving their structure.", "phase-space"),
        ("level-sets", "energy contours", "The nested contours make energy conservation visible as motion along a curve rather than across it.", "contour"),
        ("legendre", "Legendre transform", "The tangent construction shows how changing variables replaces velocity information with momentum information.", "curve"),
        ("poisson", "Poisson bracket generator", "The rotational flow suggests how a bracket can generate an infinitesimal transformation.", "curl"),
        ("canonical-pair", "canonical pair", "The paired axes keep coordinates and momenta visually tied before they become noncommuting operators.", "phase-space"),
        ("constraint-flow", "constraint flow", "The flow tangent to a constraint surface previews why constrained systems need special bookkeeping.", "constraint"),
    ],
    "oscillator": [
        ("single-oscillator", "single oscillator", "The bowl and orbit show the oscillator as both a restoring-force problem and a phase-space rotation.", "oscillator"),
        ("coupled-chain", "coupled oscillator chain", "The linked masses show how many simple oscillators become collective normal modes.", "chain"),
        ("normal-mode", "normal mode pattern", "The alternating displacement pattern makes a normal mode visible as coherent motion of the whole system.", "standing-waves"),
        ("dispersion", "dispersion relation", "The curve of frequency against wave number prepares the reader to read particles as modes with energy-momentum relations.", "dispersion"),
        ("continuum-limit", "continuum limit", "The dense chain becoming a smooth wave shows how a field emerges from many coupled variables.", "chain-to-wave"),
        ("occupation", "occupation levels", "The stacked levels preview the quantum oscillator's ladder structure and later particle counting.", "ladder"),
    ],
    "field": [
        ("field-configuration", "field configuration", "The surface over space visualizes a scalar field as one value assigned to every point.", "field-surface"),
        ("plane-wave", "plane wave mode", "The regular wavefronts show a field mode carrying a definite spatial pattern.", "wavefronts"),
        ("field-energy", "field energy density", "The heat map makes local energy density visible before it is integrated into a total quantity.", "heatmap"),
        ("conjugate-momentum", "field and conjugate momentum", "The paired surfaces suggest that a field theory has both configuration data and momentum data at each point.", "two-surfaces"),
        ("boundary-data", "boundary data", "The highlighted edge shows where boundary conditions enter a classical field problem.", "boundary"),
        ("mode-expansion", "mode expansion", "The superposed waves show how a field configuration can be reconstructed from simpler modes.", "fourier-stack"),
    ],
    "noether": [
        ("symmetry-flow", "symmetry flow", "The arrows along a level set show a continuous symmetry moving configurations without changing the action.", "flow"),
        ("current-lines", "current lines", "The streamlines through a region visualize a conserved current as something whose inflow and outflow balance.", "flux"),
        ("charge-region", "charge in a volume", "The shaded region with boundary flux connects a conserved charge to a local continuity equation.", "boundary"),
        ("stress-energy", "stress-energy flow", "The grid of arrows indicates that energy and momentum move through spacetime as local fluxes.", "stress"),
        ("surface-term", "Noether surface term", "The bright boundary band reminds the reader that a symmetry derivation must account for total derivatives.", "boundary"),
        ("translation-symmetry", "translation symmetry", "The repeated pattern under a shift gives a visual test for when momentum conservation should appear.", "shift-pattern"),
    ],
    "relativity": [
        ("light-cone", "light cone", "The cone separates timelike, lightlike, and spacelike directions before any relativistic formula is used.", "lightcone"),
        ("boost", "Lorentz boost", "The tilted axes show a boost as a change of spacetime coordinates that leaves the interval structure intact.", "boost"),
        ("mass-shell", "mass shell", "The hyperbola visualizes the invariant relation between energy, momentum, and mass while separating the two physical branches.", "mass-shell"),
        ("four-vector", "four-vector components", "The arrow in spacetime with projected components separates the geometric vector from its frame-dependent coordinates.", "vectors"),
        ("index-raising", "metric action", "The paired grids show the metric as the object that translates between related component descriptions.", "ellipse"),
        ("causal-diamond", "causal diamond", "The diamond region makes clear which events can influence or be influenced by a given interval.", "causal-diamond"),
    ],
    "maxwell": [
        ("potential-field", "potentials producing fields", "The layered potential contours and field arrows show fields as derivatives of potentials rather than independent guesses.", "vector-field"),
        ("gauge-redundancy", "gauge-related potentials", "The two different contour patterns with the same field arrows make gauge redundancy visually concrete.", "gauge-orbit"),
        ("electric-magnetic", "electric and magnetic structure", "The crossed arrow families distinguish field components while keeping them part of one electromagnetic description.", "em-field"),
        ("wave-polarization", "wave polarization", "The transverse arrows along a wavefront prepare the later photon picture by showing what oscillates during propagation.", "polarization"),
        ("field-strength", "field strength from circulation", "The small loop with changing arrows previews the curl-like structure inside the field-strength tensor.", "curl"),
        ("boundary-flux", "Maxwell flux law", "The surface with passing lines ties integral flux laws to local differential equations.", "flux"),
    ],
    "quantum": [
        ("amplitude-vector", "amplitude vector", "The complex arrows show that quantum probabilities come after amplitudes are added, not before.", "phasor-sum"),
        ("basis-change", "basis change for states", "The same state resolved along two axes previews why measurement outcomes depend on the chosen basis.", "rotated-grid"),
        ("expectation", "expectation as weighted average", "The bars and center marker show an expectation value as a weighted summary of possible outcomes.", "bars"),
        ("commutator", "noncommuting operations", "The two paths around the square fail to meet, giving a geometric picture of a nonzero commutator.", "commutator"),
        ("time-evolution", "unitary time evolution", "The state moving along a circular arc shows norm-preserving evolution in state space.", "state-arc"),
        ("measurement-spectrum", "measurement spectrum", "The separated output channels visualize measurement as resolving a state into eigenstate components.", "spectrum"),
    ],
    "spin": [
        ("rotation-sphere", "rotations and axes", "The sphere with oriented axes gives a concrete home for angular momentum before spin is introduced abstractly.", "sphere-axes"),
        ("spinor-phase", "spinor phase", "The double-turn spiral hints that spinor behavior is not identical to ordinary vector rotation.", "helix"),
        ("addition", "adding angular momenta", "The vector triangle shows how angular-momentum pieces combine into a total object.", "phasor-sum"),
        ("symmetrization", "symmetrized two-particle state", "The paired paths meeting at exchanged endpoints show why identical particles require symmetry bookkeeping.", "exchange"),
        ("fermion-antisymmetry", "antisymmetric exchange", "The crossing paths with opposite shading remind the reader that exchanging fermions changes the sign of the amplitude.", "exchange"),
        ("spin-measurement", "spin measurement axes", "The tilted measurement directions show why spin outcomes are tied to the chosen axis.", "sphere-axes"),
    ],
    "time-evolution": [
        ("dyson-timeline", "Dyson time ordering", "The ordered marks along the time line show how perturbation theory sorts operator insertions by time.", "timeline"),
        ("interaction-picture", "interaction picture split", "The two overlaid rotations separate exactly solved motion from the perturbing interaction.", "state-arc"),
        ("transition", "transition amplitude", "The curved arrow between two levels visualizes a transition amplitude before it becomes a formula.", "transition"),
        ("series", "perturbation series", "The branching paths show how successive interaction insertions build a controlled approximation.", "branching"),
        ("adiabatic", "turning an interaction on", "The smooth ramp makes visible the idea of introducing a perturbation gradually.", "ramp"),
        ("resonance", "resonant response", "The peaked response curve shows why energy differences control transition probabilities.", "spectrum"),
    ],
    "path-integral": [
        ("path-bundle", "sum over paths", "The bundle of nearby and wild paths makes the path integral a weighted sum over histories rather than a single trajectory.", "path-bundle"),
        ("time-slicing", "time slicing", "The vertical slices show how an infinite-dimensional integral is approached through many ordinary integrals.", "time-slices"),
        ("stationary-phase", "stationary phase", "The coherent band around one path shows why nearby phases survive while rapidly varying paths cancel.", "paths"),
        ("gaussian", "Gaussian integral geometry", "The elliptical contours show the quadratic form that makes Gaussian path integrals exactly computable.", "ellipse"),
        ("source", "source coupled to a path", "The localized bump along the path illustrates how a source probes the system at selected times.", "source-path"),
        ("euclidean", "Euclidean rotation", "The rotation of the time axis previews why oscillatory phases can become decaying weights.", "boost"),
    ],
    "free-field": [
        ("mode-oscillators", "field modes as oscillators", "The row of independent oscillator bowls shows how a free field decomposes into many harmonic modes.", "multi-oscillator"),
        ("dispersion", "relativistic dispersion", "The dispersion curve connects mode frequency to momentum and mass, making each field mode resemble a relativistic oscillator.", "dispersion"),
        ("commutator-grid", "equal-time commutator grid", "The paired grid points show why canonical commutators are local in space at equal time.", "stencil"),
        ("plane-waves", "plane-wave expansion", "The layered wavefronts show the ingredients from which a free field is assembled.", "wavefronts"),
        ("vacuum-fluctuation", "vacuum fluctuation", "The faint surface ripples suggest nonzero field variance even before particles are added.", "field-surface"),
        ("normalization", "mode normalization", "The boxed region keeps the normalization convention tied to the finite-volume calculation.", "box-modes"),
    ],
    "fock": [
        ("ladder", "creation ladder", "The stacked levels and upward arrows visualize creation operators as moves through occupation-number states.", "ladder"),
        ("occupation", "occupation-number pattern", "The bars over modes show a many-particle state as counts assigned to field modes.", "occupation"),
        ("vacuum", "vacuum state", "The empty baseline with fluctuation shading distinguishes the vacuum from classical nothingness.", "vacuum"),
        ("particle-mode", "particle as mode excitation", "The highlighted wave among quieter modes shows a particle as an excitation of a field mode.", "wave-envelope"),
        ("normalization", "state normalization", "The normalized stack of amplitudes connects Fock states to the same probability bookkeeping used in quantum mechanics.", "bars"),
        ("multiparticle", "multiparticle state", "Several highlighted modes show how a Fock state can contain more than one excitation without naming particle trajectories.", "occupation"),
    ],
    "propagator": [
        ("two-point", "two-point connection", "The line connecting two spacetime points makes a propagator visible as a response between events.", "propagator"),
        ("causal-support", "causal support", "The light cone around a point shows which regions can carry commutator support.", "lightcone"),
        ("pole", "pole structure", "The peak near a marked shell previews how propagators encode particle masses.", "mass-shell"),
        ("retarded", "retarded response", "The disturbance spreading forward from a source shows the boundary condition built into a retarded Green function.", "green"),
        ("microcausality", "microcausality", "The separated spacelike points outside each other's cones visualize why certain commutators must vanish.", "causal-diamond"),
        ("contour", "contour prescription", "The path bending around singular points gives a visual reminder that propagators include a boundary prescription.", "contour-path"),
    ],
    "charge": [
        ("complex-field", "complex field rotation", "The two-component rotation shows a complex scalar field as a plane of real field components.", "phase"),
        ("charge-flow", "conserved charge flow", "The streamlines through a region connect phase symmetry with a conserved current.", "flux"),
        ("particle-antiparticle", "opposite charges", "The two highlighted mode families show how a complex field naturally carries particle and antiparticle excitations.", "occupation"),
        ("u1-orbit", "U(1) orbit", "The circular orbit in field space makes phase rotations concrete before the charge operator is introduced.", "phase"),
        ("current-density", "current density", "The arrows over a scalar-density background show charge density and current as local field data.", "vector-field"),
        ("chemical-potential", "charge weighting", "The tilted level stack hints at how conserved charge changes the bookkeeping of states.", "ladder"),
    ],
    "generating": [
        ("source-field", "source probing a field", "The localized source marks show how a generating functional records the field response to external probes.", "source-field"),
        ("functional-derivative", "functional derivative", "The highlighted point on a source curve visualizes varying one position-labelled input while holding the rest fixed.", "stencil"),
        ("connected", "connected correlators", "The network pieces distinguish connected responses from products of disconnected ones before the logarithm of the generating functional is used.", "network"),
        ("legendre", "Legendre transform structure", "The tangent construction previews the move from sources to average fields and explains why the conjugate variable changes.", "curve"),
        ("gaussian-source", "Gaussian source response", "The elliptical contours show why the free generating functional is governed by a quadratic kernel.", "ellipse"),
        ("correlator-map", "correlator map", "The arrows from source insertions to measured points make the functional a compact generator of many observables.", "network"),
    ],
    "wick": [
        ("pairings", "Wick pairings", "The arcs pairing insertions make contractions visible as a systematic combinatorial operation.", "pairings"),
        ("normal-order", "normal ordering", "The separated operator stacks show how normal ordering moves creation and annihilation pieces into a fixed order.", "ladder"),
        ("gaussian-moments", "Gaussian moments", "The paired dots on an ellipse remind the reader that Wick's theorem is a property of Gaussian averages.", "ellipse"),
        ("contraction-lines", "contraction lines", "The internal links between points preview the diagrammatic language used by Feynman rules.", "network"),
        ("symmetry-factor", "symmetry factor", "The repeated pairings with identical shapes show why counting overcounts unless graph symmetries are divided out.", "pairings"),
        ("time-ordering", "time-ordered contractions", "The ordered insertions on a line show where contractions sit inside a time-ordered product.", "timeline"),
    ],
    "interacting": [
        ("phi4-potential", "interacting scalar potential", "The quartic well shows how an interaction changes the field from independent modes to coupled fluctuations.", "potential"),
        ("vertex-local", "local vertex", "The meeting point of four lines makes locality at an interaction vertex visually explicit.", "vertex4"),
        ("perturbative-expansion", "interaction expansion", "The branching diagrams show perturbation theory as a sequence of increasing interaction insertions.", "branching"),
        ("correlation", "correlation created by interaction", "The linked regions show how an interaction makes field values at different points statistically dependent.", "network"),
        ("classical-vs-quantum", "background plus fluctuation", "The smooth background with small ripples previews expanding around a classical configuration.", "two-surfaces"),
        ("coupling-strength", "coupling strength", "The family of potentials shows how changing a coupling changes the shape of the theory.", "potential-family"),
    ],
    "feynman": [
        ("position-space", "position-space diagram", "The points connected by propagator lines show how a diagram represents integrations over interaction positions.", "feynman"),
        ("momentum-space", "momentum flow", "The arrows on a vertex make momentum conservation visible before the algebraic delta function appears.", "momentum-vertex"),
        ("vertex-factor", "vertex factor", "The local junction isolates the interaction rule from the propagator rule so the diagram can be translated into algebra.", "vertex4"),
        ("external-internal", "external and internal lines", "The contrast between outside legs and internal connections previews the anatomy of amplitudes.", "feynman"),
        ("tree-diagram", "tree-level process", "The branching tree shows the simplest perturbative contribution before loops enter and before any unconstrained loop momentum appears.", "tree-diagram"),
        ("diagram-to-integral", "diagram to integral", "The loop with a marked internal arrow shows where an unobserved momentum variable enters the integral.", "loop"),
    ],
    "scattering": [
        ("incoming-outgoing", "incoming and outgoing states", "The before-and-after beams show scattering as a comparison between asymptotic states measured far from the interaction region.", "scattering"),
        ("phase-space", "final-state phase space", "The shell of allowed momenta visualizes why rates require integrating over many possible final configurations.", "mass-shell"),
        ("cross-section", "cross section", "The target disk and incoming beam make cross section a geometric effective area before it becomes a formula.", "beam-target"),
        ("mandelstam", "kinematic channels", "The three exchange sketches hint that the same external particles can be organized into different channels.", "tree-diagram"),
        ("normalization", "box normalization", "The finite box with wavefronts keeps state normalization connected to the limiting procedure.", "box-modes"),
        ("rate", "rate from flux and probability", "The stream of incoming arrows and outgoing spread visually separates incident flux from transition probability.", "scattering"),
    ],
    "lsz": [
        ("external-legs", "external leg amputation", "The trimmed external lines show the visual content of removing external propagators to isolate the amplitude.", "amputation"),
        ("pole-residue", "pole residue", "The sharp pole and highlighted residue region show why asymptotic particles are extracted from propagators.", "spectrum"),
        ("asymptotic", "asymptotic states", "The widely separated incoming and outgoing packets show the states that LSZ connects to correlation functions.", "wave-packets"),
        ("correlator-amplitude", "correlator to amplitude", "The diagram changing from connected points to external particles summarizes the role of reduction.", "feynman"),
        ("on-shell", "on-shell limit", "The approach to the mass shell visualizes the limit used to identify physical particles.", "mass-shell"),
        ("wavefunction-renormalization", "field strength residue", "The rescaled arrow at the pole previews the normalization factor attached to external particles.", "flow"),
    ],
    "loops": [
        ("loop-momentum", "loop momentum", "The closed loop with an internal arrow shows why loop diagrams introduce momenta not fixed by external kinematics.", "loop"),
        ("self-energy", "self-energy correction", "The propagator interrupted by a loop visualizes how propagation is modified by fluctuations.", "self-energy"),
        ("vertex-correction", "vertex correction", "The triangular loop at a vertex shows how the local interaction is corrected by virtual processes.", "vertex-loop"),
        ("divergence", "large-momentum region", "The shaded outer momentum region previews why loop integrals can be sensitive to short distances.", "cutoff-shell"),
        ("renormalized-propagator", "renormalized propagator", "The before-and-after curves show a pole shifted and rescaled by self-energy effects.", "spectrum"),
        ("counterterm-insert", "counterterm insertion", "The small marked insertion on a line or vertex gives counterterms a visible place in diagrammatic bookkeeping.", "counterterm"),
    ],
    "cutoff": [
        ("momentum-cutoff", "momentum cutoff", "The disk with a hard boundary shows the simplest idea of excluding modes above a chosen scale.", "cutoff-shell"),
        ("short-distance", "short-distance sensitivity", "The magnifying nested regions show why large momentum corresponds to resolving smaller distances.", "nested"),
        ("counterterm", "counterterm cancellation", "The opposing shaded pieces show a bare divergent contribution balanced by a local counterterm.", "balance"),
        ("scale-dependence", "scale dependence", "The sliding cutoff boundary makes the arbitrary scale a visible part of the calculation.", "cutoff-shell"),
        ("power-counting", "power counting", "The layered momentum shells show how different regions contribute with different scaling.", "shells"),
        ("renormalized-quantity", "renormalized observable", "The stable central value amid changing outer shells visualizes how measured quantities remain finite.", "target"),
    ],
    "dimreg": [
        ("dimension-continuation", "dimension continuation", "The family of grids suggests analytic continuation in dimension without pretending to draw fractional space literally.", "deformed-grid"),
        ("epsilon-pole", "epsilon pole", "The sharp peak near zero shows the pole structure that replaces a hard cutoff divergence.", "spectrum"),
        ("minimal-subtraction", "minimal subtraction", "The isolated singular piece shows what is removed in a subtraction scheme.", "balance"),
        ("gamma-function", "analytic integral structure", "The smooth curve with a controlled singular point previews the special-function bookkeeping of dimensional regularization.", "curve"),
        ("scale-mu", "renormalization scale", "The marked reference scale shows why a scale enters when dimensions are continued.", "target"),
        ("scheme", "scheme dependence", "The two different paths ending at the same measured point show how intermediate conventions can differ.", "paths"),
    ],
    "counterterms": [
        ("bare-renormalized", "bare and renormalized parameters", "The layered parameter bars separate measured finite quantities from the bookkeeping pieces used to define them.", "bars"),
        ("mass-condition", "mass renormalization condition", "The pole aligned to a measured value shows what it means to choose a physical mass condition.", "spectrum"),
        ("field-strength", "field strength normalization", "The rescaled wave illustrates how normalization is fixed by a residue condition.", "wave-envelope"),
        ("local-counterterm", "local counterterm", "The marked local insertion makes a counterterm visible as a new local term in the same effective description.", "counterterm"),
        ("scheme-comparison", "renormalization schemes", "The parallel tracks show that different schemes organize intermediate quantities differently while preserving observables.", "parallel-flows"),
        ("observable-anchor", "observable anchor", "The measured marker anchoring a family of curves shows how renormalization conditions tie symbols to experiments.", "target"),
    ],
    "rg": [
        ("running-coupling", "running coupling", "The curve across scales shows a coupling as a scale-dependent coordinate, not a fixed universal number.", "rg-flow"),
        ("beta-vector-field", "beta function flow", "The arrows in coupling space visualize the beta function as a vector field.", "vector-field"),
        ("fixed-point", "fixed point", "The flow lines approaching a point make a fixed point visible as scale-invariant behavior.", "rg-fixed"),
        ("relevant-irrelevant", "relevant and irrelevant directions", "The stable and unstable directions around a fixed point preview universality and the classification of perturbations by scale.", "saddle-flow"),
        ("log-scale", "logarithmic scale", "The compressed scale markers show why renormalization naturally uses logarithmic distance in energy.", "spectrum"),
        ("trajectory", "RG trajectory", "The path through coupling space shows a theory changing description as the observation scale changes.", "rg-flow"),
    ],
    "effective-action": [
        ("source-legendre", "Legendre transform to effective action", "The tangent construction connects source dependence to an action for average fields.", "curve"),
        ("one-particle-irreducible", "one-particle-irreducible graph", "The graph that cannot be split by cutting one internal line makes the 1PI condition visual.", "network"),
        ("effective-potential", "effective potential", "The corrected potential curve shows how fluctuations modify the landscape seen by average fields.", "potential-family"),
        ("background-field", "background plus fluctuation", "The smooth surface with small ripples separates an average field from the fluctuations integrated around it.", "two-surfaces"),
        ("loop-expansion", "loop expansion", "The sequence from a tree to a loop diagram visualizes the hierarchy of corrections.", "tree-loop"),
        ("vertex-functions", "vertex functions", "The multi-leg junctions show the effective action as a generator of proper vertices.", "vertex4"),
    ],
    "wilsonian": [
        ("integrating-shell", "integrating out momentum shells", "The outer shell being removed shows Wilsonian coarse graining as changing the degrees of freedom retained.", "shells"),
        ("coarse-grain", "coarse graining", "The blurred-to-smooth field pattern shows how short-distance detail is replaced by effective parameters.", "coarse"),
        ("operator-flow", "operator coefficient flow", "The arrows among coefficient bars show local operators changing weights as the cutoff changes.", "bars-flow"),
        ("decoupling", "heavy-mode decoupling", "The separated heavy level above a low-energy band visualizes why heavy modes leave local traces.", "ladder"),
        ("universality", "universality", "The many microscopic paths converging to one large-scale behavior illustrate universality under repeated coarse graining.", "converging-flows"),
        ("effective-theory", "effective theory window", "The highlighted scale window shows where an EFT is meant to be accurate.", "target-band"),
    ],
    "ope": [
        ("short-distance", "short-distance expansion", "The two nearby insertions merging into one local region make the operator product expansion visible.", "ope"),
        ("local-operators", "tower of local operators", "The stacked local terms show the OPE as an ordered expansion in increasingly suppressed operators.", "ladder"),
        ("power-counting", "power counting hierarchy", "The shrinking bars show how operator dimension organizes the importance of terms.", "bars"),
        ("coefficient-functions", "coefficient functions", "The smooth outer envelopes around a local insertion show long-distance coefficients multiplying local data.", "nested"),
        ("separation-scale", "separation of scales", "The small inner circle and large outer region distinguish local physics from distant measurement.", "nested"),
        ("matching", "matching calculation", "The two descriptions meeting at one scale show how short-distance physics is encoded in local coefficients.", "parallel-flows"),
    ],
    "groups": [
        ("group-manifold", "group manifold", "The curved surface with nearby arrows shows a continuous group as a space of transformations.", "manifold"),
        ("generator", "generator as tangent", "The tangent arrow at the identity visualizes a Lie algebra generator as an infinitesimal motion.", "tangent-manifold"),
        ("commutator", "commutator loop", "The small nonclosing loop shows how noncommuting transformations produce a new direction.", "commutator"),
        ("structure-constants", "structure constants", "The triangle of generator directions suggests how commutators close within the algebra.", "basis-rays"),
        ("representation", "matrix representation", "The same transformation acting on arrows previews a representation as a concrete action on a vector space.", "linear-map"),
        ("orbit", "group orbit", "The orbit through a point shows all configurations related by a symmetry action.", "gauge-orbit"),
    ],
    "representations": [
        ("multiplet", "multiplet", "The cluster of related components shows a representation as a set of fields transformed together.", "multiplet"),
        ("weight-diagram", "weight diagram", "The lattice of points previews how charges and weights organize states inside a representation.", "weight-lattice"),
        ("charge-axis", "charge eigenvalues", "The separated marks on an axis show charges as labels of representation components.", "spectrum"),
        ("tensor-product", "tensor product decomposition", "The branching diagram shows combined representations breaking into simpler pieces that can be handled one sector at a time.", "branching"),
        ("rotation-action", "group action on states", "The orbiting state vector shows a representation in action rather than as abstract notation.", "state-arc"),
        ("selection-rule", "selection rule", "The allowed and blocked arrows visualize how representation data constrain transitions.", "transition"),
    ],
    "global-symmetry": [
        ("global-rotation", "global transformation", "The same rotation applied everywhere shows the meaning of a global symmetry.", "phase-field"),
        ("noether-current", "Noether current", "The streamlines created by a continuous symmetry connect global transformations to local conservation.", "flux"),
        ("charge-generator", "charge as generator", "The circular orbit with a marked generator shows how charge moves a state along a symmetry direction.", "phase"),
        ("ward-identity-seed", "symmetry constraint", "The balanced diagram pieces hint that symmetry imposes relations among correlation functions.", "balance"),
        ("broken-or-preserved", "symmetry test", "The unchanged and changed patterns show what it means for an action or state to respect a transformation.", "shift-pattern"),
        ("current-conservation", "continuity equation", "The inflow and outflow through a boundary visualize local conservation.", "boundary"),
    ],
    "dirac": [
        ("spinor-components", "spinor components", "The paired component blocks show a spinor as structured data transformed by Lorentz symmetry.", "multiplet"),
        ("gamma-matrices", "gamma matrix action", "The arrows between component blocks suggest gamma matrices mixing spinor components while preserving the relativistic bookkeeping.", "matrix-flow"),
        ("light-cone-spinor", "relativistic spinor propagation", "The wave packet inside a light cone connects spinor fields to causal relativistic motion.", "lightcone"),
        ("particle-antiparticle", "particle and antiparticle branches", "The split branches visualize positive- and negative-frequency solutions before reinterpretation as antiparticles.", "branching"),
        ("bilinear", "spinor bilinear", "The two spinor blocks joining into a vector arrow shows why bilinears create Lorentz objects.", "flow"),
        ("fermion-line", "fermion line orientation", "The oriented line gives the diagrammatic convention for tracking fermion flow through amplitudes and interactions.", "fermion-line"),
    ],
    "qed": [
        ("local-phase", "local phase symmetry", "The phases changing from point to point show why ordinary derivatives must be replaced by covariant ones.", "phase-field"),
        ("gauge-connection", "gauge connection", "The arrows attached between neighboring points visualize a connection comparing phases locally.", "lattice-links"),
        ("photon-propagator", "photon propagator", "The wavy line between two currents makes the mediator role of the photon visually explicit.", "photon-line"),
        ("qed-vertex", "QED vertex", "The fermion line meeting a wavy photon line isolates the basic QED interaction rule.", "qed-vertex"),
        ("ward-identity", "Ward identity", "The balanced incoming and outgoing current picture hints that gauge symmetry constrains amplitudes.", "balance"),
        ("gauge-fixing", "gauge fixing slice", "The slice crossing gauge orbits shows gauge fixing as choosing one representative from each redundant family.", "gauge-slice"),
    ],
    "yang-mills": [
        ("nonabelian-orbit", "non-Abelian gauge orbit", "The twisting orbit shows why non-Abelian transformations cannot be treated as independent phase rotations.", "manifold"),
        ("field-strength", "non-Abelian field strength", "The small loop with a mismatch after transport visualizes curvature in gauge space.", "commutator"),
        ("self-interaction", "gauge boson self-interaction", "The three- and four-line junctions show why Yang-Mills fields interact with themselves.", "yang-mills-vertices"),
        ("covariant-commutator", "covariant commutator", "The nonclosing transport square gives the visual content of a covariant commutator.", "commutator"),
        ("asymptotic-freedom", "asymptotic freedom flow", "The coupling flow weakening at short distances previews the qualitative behavior of non-Abelian gauge theory.", "rg-flow"),
        ("color-flow", "color flow", "The braided lines show internal charge labels moving through an interaction where non-Abelian ordering matters.", "braid"),
    ],
    "brst": [
        ("gauge-volume", "gauge volume", "The long redundant orbit next to a transverse slice shows why gauge volume must be divided out.", "gauge-slice"),
        ("ghost-loop", "ghost loop", "The closed dashed loop gives ghost fields a visual role as bookkeeping for gauge fixing.", "ghost-loop"),
        ("brst-arrow", "BRST transformation", "The directed chain of fields visualizes BRST as a differential-like operation acting across the gauge-fixed field content.", "flow"),
        ("nilpotency", "nilpotency", "The two-step arrow ending at zero illustrates the idea behind applying the BRST operation twice.", "branching"),
        ("physical-states", "physical state selection", "The highlighted subspace shows physical states as cohomology-like survivors of the BRST bookkeeping.", "state-arc"),
        ("faddeev-popov", "Faddeev-Popov determinant", "The crossing of a slice through orbits visualizes the Jacobian hidden inside gauge fixing.", "gauge-slice"),
    ],
    "ssb": [
        ("mexican-hat", "degenerate vacua", "The circular valley of minima makes spontaneous symmetry breaking visible as choosing one vacuum from many equivalent ones.", "mexican-hat"),
        ("vacuum-choice", "chosen vacuum", "The marked point on the vacuum circle shows that the equations can be symmetric even when the chosen state is not.", "phase"),
        ("goldstone", "Goldstone direction", "The flat angular direction and steep radial direction distinguish massless and massive fluctuations.", "mexican-contours"),
        ("order-parameter", "order parameter", "The arrow growing away from the origin visualizes an order parameter selecting a direction in field space.", "phase"),
        ("broken-generator", "broken generator", "The tangent motion around the vacuum circle shows the direction created by a broken generator.", "tangent-manifold"),
        ("domains", "domains of vacuum choice", "The patches of different orientation show how local choices of vacuum can vary across space.", "domains"),
    ],
    "higgs": [
        ("gauge-goldstone", "Goldstone mode eaten by gauge field", "The angular mode feeding into a gauge-field line gives a visual summary of how a gauge boson gains a longitudinal mode.", "higgs-eating"),
        ("mass-generation", "gauge boson mass", "The formerly transverse line acquiring a third component visualizes the new massive vector degree of freedom.", "polarization"),
        ("unitary-gauge", "unitary gauge", "The radial-only fluctuation after a gauge choice shows why the Goldstone coordinate can disappear from the spectrum.", "mexican-contours"),
        ("higgs-potential", "Higgs potential", "The potential valley and radial excitation show the scalar sector around the chosen vacuum.", "mexican-hat"),
        ("electroweak-mixing", "field mixing", "The two input arrows rotating into physical output arrows preview electroweak mixing.", "rotated-grid"),
        ("degree-counting", "degree-of-freedom counting", "The blocks before and after symmetry breaking keep the counting of physical modes explicit.", "blocks"),
    ],
    "nonperturbative": [
        ("topological-sector", "topological sectors", "The separated winding classes show configurations grouped by a global property that cannot be changed smoothly.", "winding"),
        ("instanton", "instanton profile", "The localized Euclidean lump shows a nonperturbative saddle as a field configuration in spacetime.", "heatmap"),
        ("anomaly", "failed symmetry", "The broken balance diagram visualizes an anomaly as a symmetry of the classical expression that fails in the quantum measure.", "broken-balance"),
        ("wilson-loop", "Wilson loop", "The closed loop enclosing flux makes gauge-invariant nonlocal information visible beyond ordinary perturbative fields.", "wilson-loop"),
        ("theta-vacua", "theta sectors", "The family of phase-weighted sectors hints at how topological sectors combine in amplitudes.", "phase"),
        ("confinement", "flux tube", "The narrow tube between charges visualizes the qualitative idea behind confinement and the growth of separation energy.", "flux-tube"),
    ],
    "lattice": [
        ("lattice-field", "field on a lattice", "The grid of sites with local values shows how a field theory can be regularized by replacing space with a lattice.", "lattice-field"),
        ("link-variable", "link variables", "The arrows on lattice links visualize gauge variables living between sites rather than only on sites.", "lattice-links"),
        ("plaquette", "plaquette loop", "The highlighted square loop shows the smallest gauge-invariant curvature measurement on a lattice.", "plaquette"),
        ("wilson-loop", "Wilson loop area", "The large rectangular loop previews how confinement is diagnosed by loop behavior.", "wilson-loop"),
        ("thermal-circle", "thermal circle", "The compact Euclidean time direction shows finite temperature as periodicity in imaginary time.", "thermal-circle"),
        ("continuum-limit", "continuum limit", "The grid becoming finer shows how a lattice calculation is connected back to continuum field theory.", "grid-refine"),
    ],
    "standard-model": [
        ("gauge-group", "Standard Model gauge factors", "The three linked sectors show the gauge-group structure as connected but distinct pieces of one theory.", "standard-model"),
        ("representations", "matter representations", "The grouped multiplets visualize matter fields as organized by their symmetry charges.", "multiplet"),
        ("yukawa", "Yukawa coupling", "The fermion pair meeting a scalar line shows how masses arise after symmetry breaking.", "yukawa"),
        ("electroweak", "electroweak breaking", "The mixing diagram shows weak and hypercharge fields reorganizing into physical fields.", "rotated-grid"),
        ("curved-background", "QFT on a curved background", "The field pattern drawn over a curved grid makes clear that the background geometry changes the bookkeeping of local fields.", "curved-grid"),
        ("course-map", "course synthesis", "The network map ties calculus, fields, symmetry, renormalization, and the Standard Model into one path through the book.", "network"),
    ],
    "generic": [
        ("concept-map", "concept map", "The connected nodes organize the chapter's main objects as a dependency map rather than a list of formulas.", "network"),
        ("local-to-global", "local-to-global structure", "The small neighborhood embedded in a larger region shows how local rules build global behavior.", "nested"),
        ("finite-to-continuum", "finite-to-continuum bridge", "The discrete samples becoming a smooth curve make the limiting step visible.", "chain-to-wave"),
        ("symmetry-balance", "symmetry and balance", "The balanced arrows show how an invariance or conservation law constrains the calculation.", "balance"),
        ("scale-picture", "scale picture", "The nested bands keep the scale of the calculation explicit.", "nested"),
        ("workflow", "calculation workflow", "The arrows through several stages turn the chapter's method into a visual checklist for the reader.", "flow"),
    ],
}


REVIEW_BANK: list[tuple[str, str, str, str]] = [
    ("part-map", "part synthesis map", "The map collects the part's main constructions into a visual route so the reader can see how the chapters support one another.", "network"),
]


def specs_for_file(path: Path) -> list[FigureSpec]:
    title = read_title(path)
    number = chapter_number(path)
    if path.stem.startswith("partreview"):
        bank = REVIEW_BANK
        count = 1
    else:
        family = family_for(title)
        bank = BASE_BANK[family]
        count = 6 if number in CORE_CHAPTERS else 4
    specs = []
    for index, (slug, concept, caption, motif) in enumerate(bank[:count], start=1):
        specs.append(
            FigureSpec(
                file=path.relative_to(ROOT),
                title=title,
                chapter_number=number,
                index=index,
                slug=slugify(slug),
                concept=concept,
                caption=caption,
                motif=motif,
            )
        )
    return specs


def seed_for(text: str) -> int:
    return int(sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def setup_ax(ax: plt.Axes, seed: int) -> np.random.Generator:
    rng = np.random.default_rng(seed)
    ax.set_facecolor("#fbfaf7")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    return rng


def draw_arrow(ax: plt.Axes, x0: float, y0: float, x1: float, y1: float, color: str = "#0c5f78", lw: float = 2.0, alpha: float = 1.0) -> None:
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=0, shrinkB=0, alpha=alpha),
    )


def draw_grid(ax: plt.Axes, angle: float = 0.0, color: str = "#d8d1c4", alpha: float = 0.55) -> None:
    vals = np.linspace(-0.9, 0.9, 9)
    rot = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
    for v in vals:
        pts = np.array([[-0.9, v], [0.9, v]]) @ rot.T
        ax.plot(pts[:, 0], pts[:, 1], color=color, lw=0.8, alpha=alpha)
        pts = np.array([[v, -0.9], [v, 0.9]]) @ rot.T
        ax.plot(pts[:, 0], pts[:, 1], color=color, lw=0.8, alpha=alpha)


def motif_curve(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 300)
    y = 0.45 * np.sin(2.0 * x + 0.3) + 0.2 * x**2 - 0.05
    x0 = -0.08
    y0 = 0.45 * np.sin(2.0 * x0 + 0.3) + 0.2 * x0**2 - 0.05
    slope = 0.9 * np.cos(2.0 * x0 + 0.3) + 0.4 * x0
    ax.fill_between(x, y - 0.08, y + 0.08, where=np.abs(x - x0) < 0.32, color="#f2c66d", alpha=0.35)
    ax.plot(x, y, color="#12212b", lw=3)
    ax.plot(x, y0 + slope * (x - x0), color="#0c8aa0", lw=2)
    ax.scatter([x0], [y0], s=80, color="#d85c41", zorder=5)


def motif_bars(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.85, 0.85, 13)
    vals = 0.25 + 0.55 * np.exp(-3.5 * xs**2)
    ax.bar(xs, vals, width=0.11, bottom=-0.75, color="#77b7c5", edgecolor="#12212b", linewidth=0.7, alpha=0.8)
    ax.plot(xs, vals - 0.75, color="#12212b", lw=2.5)
    ax.axhline(-0.75, color="#484848", lw=1)


def motif_boundary(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 300)
    r = 0.58 + 0.08 * np.sin(3 * theta)
    x = r * np.cos(theta)
    y = 0.72 * r * np.sin(theta)
    ax.fill(x, y, color="#d8e7e8", alpha=0.7)
    ax.plot(x, y, color="#0c5f78", lw=3)
    for t in np.linspace(0.2, 2 * np.pi - 0.2, 14):
        rr = 0.58 + 0.08 * np.sin(3 * t)
        px, py = rr * np.cos(t), 0.72 * rr * np.sin(t)
        draw_arrow(ax, 0.82 * px, 0.82 * py, 1.08 * px, 1.08 * py, "#d85c41", 1.4, 0.8)


def motif_nested(ax: plt.Axes, rng: np.random.Generator) -> None:
    colors = ["#d85c41", "#f2c66d", "#77b7c5", "#315f72"]
    for i, rad in enumerate([0.82, 0.58, 0.34, 0.14]):
        circ = plt.Circle((0, 0), rad, fill=False, lw=3 - 0.25 * i, color=colors[i], alpha=0.85)
        ax.add_patch(circ)
    draw_arrow(ax, -0.9, -0.82, 0.82, -0.82, "#12212b", 1.8)


def motif_flow(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.75, 0.75, 4)
    ys = 0.22 * np.sin(np.linspace(0, np.pi, 4))
    ax.plot(xs, ys, color="#d8d1c4", lw=12, solid_capstyle="round", alpha=0.8)
    for i in range(3):
        draw_arrow(ax, xs[i], ys[i], xs[i + 1], ys[i + 1], "#0c5f78", 2.8)
    ax.scatter(xs, ys, s=170, color=["#77b7c5", "#f2c66d", "#d85c41", "#315f72"], edgecolor="#12212b", linewidth=1)


def motif_stencil(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0.0, alpha=0.35)
    pts = [(-0.35, 0), (0, 0), (0.35, 0), (0, 0.35), (0, -0.35)]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=[70, 150, 70, 70, 70], color="#77b7c5", edgecolor="#12212b")
    for p in pts:
        if p != (0, 0):
            draw_arrow(ax, p[0], p[1], 0, 0, "#d85c41", 1.6, 0.7)


def motif_vectors(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0.0, alpha=0.35)
    draw_grid(ax, 0.42, color="#eadfca", alpha=0.4)
    draw_arrow(ax, -0.55, -0.45, 0.55, 0.45, "#12212b", 3)
    draw_arrow(ax, -0.55, -0.45, 0.35, -0.45, "#0c8aa0", 2)
    draw_arrow(ax, 0.35, -0.45, 0.55, 0.45, "#d85c41", 2)


def motif_projection(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.75, -0.55, 0.75, -0.55, "#12212b", 2.5)
    draw_arrow(ax, -0.55, -0.55, 0.35, 0.55, "#0c5f78", 3)
    ax.plot([0.35, 0.35], [0.55, -0.55], color="#d85c41", lw=2, ls="--")
    ax.plot([-0.55, 0.35], [-0.55, -0.55], color="#f2a23a", lw=5, alpha=0.55)


def motif_rotated_grid(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0.0, "#d8d1c4", 0.45)
    draw_grid(ax, 0.55, "#77b7c5", 0.45)
    draw_arrow(ax, -0.25, -0.25, 0.55, 0.42, "#12212b", 3)


def motif_ellipse(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 250)
    ax.plot(0.75 * np.cos(theta), 0.38 * np.sin(theta), color="#0c5f78", lw=3)
    ax.plot(0.42 * np.cos(theta), 0.68 * np.sin(theta), color="#d85c41", lw=2, alpha=0.75)
    draw_arrow(ax, 0, 0, 0.58, 0.25, "#12212b", 2.3)


def motif_frame_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0, alpha=0.22)
    for x in np.linspace(-0.65, 0.65, 4):
        for y in np.linspace(-0.45, 0.45, 3):
            a = 0.6 * np.sin(2 * x + y)
            draw_arrow(ax, x, y, x + 0.13 * np.cos(a), y + 0.13 * np.sin(a), "#0c5f78", 1.4)
            draw_arrow(ax, x, y, x - 0.11 * np.sin(a), y + 0.11 * np.cos(a), "#d85c41", 1.2)


def motif_contour(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 140)
    y = np.linspace(-1, 1, 140)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-((X - 0.2) ** 2 + 2 * (Y + 0.1) ** 2)) + 0.45 * np.exp(-4 * ((X + 0.45) ** 2 + (Y - 0.35) ** 2))
    ax.contourf(X, Y, Z, levels=12, cmap="YlGnBu", alpha=0.85)
    ax.contour(X, Y, Z, levels=7, colors="#12212b", linewidths=0.6, alpha=0.6)


def motif_surface_gradient(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 120)
    y = np.linspace(-1, 1, 120)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(2.2 * X) * np.cos(1.7 * Y) + 0.4 * X
    ax.contourf(X, Y, Z, levels=16, cmap="PuBuGn", alpha=0.85)
    for x0, y0 in [(-0.5, -0.2), (-0.1, 0.15), (0.42, -0.35), (0.35, 0.45)]:
        gx = 2.2 * np.cos(2.2 * x0) * np.cos(1.7 * y0) + 0.4
        gy = -1.7 * np.sin(2.2 * x0) * np.sin(1.7 * y0)
        norm = math.hypot(gx, gy) or 1
        draw_arrow(ax, x0, y0, x0 + 0.22 * gx / norm, y0 + 0.22 * gy / norm, "#d85c41", 2)


def motif_flux(ax: plt.Axes, rng: np.random.Generator) -> None:
    for y in np.linspace(-0.65, 0.65, 8):
        x = np.linspace(-0.9, 0.9, 160)
        ax.plot(x, y + 0.12 * np.sin(3 * x + 2 * y), color="#0c5f78", lw=1.7, alpha=0.75)
        draw_arrow(ax, 0.45, y + 0.12 * np.sin(3 * 0.45 + 2 * y), 0.62, y + 0.12 * np.sin(3 * 0.62 + 2 * y), "#0c5f78", 1.5)
    ax.add_patch(plt.Circle((0, 0), 0.48, fill=False, color="#d85c41", lw=3))


def motif_curl(ax: plt.Axes, rng: np.random.Generator) -> None:
    for cx, cy, r in [(-0.45, 0.25, 0.18), (0.25, -0.12, 0.23), (0.45, 0.42, 0.14), (-0.08, -0.55, 0.16)]:
        theta = np.linspace(0.2, 1.85 * np.pi, 100)
        ax.plot(cx + r * np.cos(theta), cy + r * np.sin(theta), color="#0c5f78", lw=2)
        draw_arrow(ax, cx + r * np.cos(theta[-8]), cy + r * np.sin(theta[-8]), cx + r * np.cos(theta[-1]), cy + r * np.sin(theta[-1]), "#d85c41", 2)


def motif_deformed_grid(ax: plt.Axes, rng: np.random.Generator) -> None:
    vals = np.linspace(-0.8, 0.8, 7)
    for v in vals:
        y = np.linspace(-0.8, 0.8, 120)
        x = v + 0.18 * np.sin(2.8 * y)
        ax.plot(x, y, color="#77b7c5", lw=1.2)
        x = np.linspace(-0.8, 0.8, 120)
        y = v + 0.15 * np.sin(2.5 * x)
        ax.plot(x, y, color="#d8d1c4", lw=1.2)


def motif_field_surface(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 140)
    y = np.linspace(-1, 1, 140)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(4 * X + 0.3) * np.cos(3 * Y) * np.exp(-0.3 * (X**2 + Y**2))
    ax.imshow(Z, extent=[-1, 1, -1, 1], origin="lower", cmap="RdYlBu_r", alpha=0.9)
    ax.contour(X, Y, Z, levels=8, colors="#12212b", linewidths=0.4, alpha=0.45)


def motif_phase(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 220)
    ax.plot(0.65 * np.cos(theta), 0.65 * np.sin(theta), color="#d8d1c4", lw=2)
    for a, color in [(0.35, "#0c5f78"), (1.25, "#d85c41"), (2.55, "#f2a23a")]:
        draw_arrow(ax, 0, 0, 0.6 * np.cos(a), 0.6 * np.sin(a), color, 3)


def motif_wave(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 500)
    ax.plot(x, 0.42 * np.sin(10 * x), color="#0c5f78", lw=3)
    ax.plot(x, 0.42 * np.cos(10 * x), color="#d85c41", lw=2, alpha=0.65)
    ax.axhline(0, color="#d8d1c4", lw=1)


def motif_phasor_sum(ax: plt.Axes, rng: np.random.Generator) -> None:
    starts = [(0, 0), (0.45, 0.18), (0.12, 0.62)]
    ends = [(0.45, 0.18), (0.12, 0.62), (0.65, 0.62)]
    colors = ["#0c5f78", "#d85c41", "#f2a23a"]
    for s, e, c in zip(starts, ends, colors):
        draw_arrow(ax, s[0] - 0.45, s[1] - 0.35, e[0] - 0.45, e[1] - 0.35, c, 3)
    draw_arrow(ax, -0.45, -0.35, 0.2, 0.27, "#12212b", 2.2)


def motif_spectrum(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.array([-0.72, -0.45, -0.1, 0.24, 0.52, 0.75])
    heights = np.array([0.18, 0.65, 0.32, 0.82, 0.48, 0.25])
    for x, h in zip(xs, heights):
        ax.plot([x, x], [-0.72, -0.72 + h], color="#0c5f78", lw=5, alpha=0.85)
    ax.axhline(-0.72, color="#12212b", lw=1.4)


def motif_wave_envelope(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 600)
    env = np.exp(-5 * x**2)
    ax.fill_between(x, -0.55 * env, 0.55 * env, color="#f2c66d", alpha=0.4)
    ax.plot(x, 0.55 * env * np.sin(18 * x), color="#0c5f78", lw=2.5)


def motif_linear_map(ax: plt.Axes, rng: np.random.Generator) -> None:
    square = np.array([[-0.65, -0.45], [0.05, -0.45], [0.05, 0.25], [-0.65, 0.25], [-0.65, -0.45]])
    A = np.array([[1.0, 0.45], [0.25, 1.0]])
    mapped = square @ A.T + np.array([0.42, 0.1])
    ax.plot(square[:, 0], square[:, 1], color="#d8d1c4", lw=3)
    ax.plot(mapped[:, 0], mapped[:, 1], color="#0c5f78", lw=3)
    draw_arrow(ax, -0.1, -0.08, 0.27, 0.05, "#d85c41", 2.5)


def motif_matrix(ax: plt.Axes, rng: np.random.Generator) -> None:
    for i in range(5):
        for j in range(5):
            color = "#77b7c5" if j <= i else "#f2c66d"
            ax.add_patch(plt.Rectangle((-0.65 + j * 0.26, 0.55 - i * 0.26), 0.2, 0.2, facecolor=color, edgecolor="#12212b", lw=0.6, alpha=0.75))


def motif_eigen(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0, alpha=0.25)
    ax.plot([-0.8, 0.8], [-0.35, 0.35], color="#d85c41", lw=3)
    for t in np.linspace(-0.6, 0.6, 5):
        draw_arrow(ax, t, 0.44 * t, 1.25 * t, 0.55 * t, "#0c5f78", 1.8, 0.85)


def motif_basis_rays(ax: plt.Axes, rng: np.random.Generator) -> None:
    for a, c in zip(np.linspace(0.15, 2.8, 7), ["#0c5f78", "#77b7c5", "#f2c66d", "#d85c41", "#315f72", "#8fb8a8", "#c78d73"]):
        draw_arrow(ax, 0, 0, 0.78 * np.cos(a), 0.78 * np.sin(a), c, 2)


def motif_ladder(ax: plt.Axes, rng: np.random.Generator) -> None:
    ys = np.linspace(-0.65, 0.65, 6)
    for i, y in enumerate(ys):
        ax.plot([-0.55, 0.55], [y, y], color="#12212b", lw=1.5 + 0.15 * i)
    for i in range(len(ys) - 1):
        draw_arrow(ax, 0.0, ys[i] + 0.03, 0.0, ys[i + 1] - 0.03, "#d85c41", 2)


def motif_overlap_waves(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 500)
    y1 = np.exp(-7 * (x + 0.18) ** 2)
    y2 = 0.9 * np.exp(-7 * (x - 0.12) ** 2)
    ax.fill_between(x, -0.75, -0.75 + 0.9 * np.minimum(y1, y2), color="#f2c66d", alpha=0.5)
    ax.plot(x, -0.75 + 0.9 * y1, color="#0c5f78", lw=2.5)
    ax.plot(x, -0.75 + 0.9 * y2, color="#d85c41", lw=2.5)


def motif_state_arc(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0.2, 2.2, 160)
    ax.plot(0.72 * np.cos(theta), 0.72 * np.sin(theta), color="#0c5f78", lw=3)
    draw_arrow(ax, 0.72 * np.cos(theta[-8]), 0.72 * np.sin(theta[-8]), 0.72 * np.cos(theta[-1]), 0.72 * np.sin(theta[-1]), "#d85c41", 2.5)
    draw_arrow(ax, 0, 0, 0.72 * np.cos(theta[0]), 0.72 * np.sin(theta[0]), "#12212b", 1.5)
    draw_arrow(ax, 0, 0, 0.72 * np.cos(theta[-1]), 0.72 * np.sin(theta[-1]), "#12212b", 1.5)


def motif_fourier_stack(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 500)
    y = np.zeros_like(x)
    colors = ["#77b7c5", "#f2c66d", "#d85c41", "#315f72"]
    for n, c in zip([1, 2, 4, 7], colors):
        comp = 0.16 * np.sin(n * np.pi * (x + 1))
        y += comp
        ax.plot(x, comp + 0.18 * (n in [2, 4]) - 0.5 + 0.08 * n / 7, color=c, lw=1.4, alpha=0.55)
    ax.plot(x, y + 0.35, color="#12212b", lw=3)


def motif_delta(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 600)
    for sig, c in [(0.24, "#77b7c5"), (0.14, "#f2c66d"), (0.07, "#d85c41")]:
        y = np.exp(-(x / sig) ** 2) / sig
        y = y / y.max()
        ax.plot(x, -0.75 + 1.35 * y, color=c, lw=2.4)
    ax.axhline(-0.75, color="#12212b", lw=1)


def motif_green(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 400)
    y = 0.65 * np.exp(-3 * np.abs(x))
    ax.plot(x, y - 0.55, color="#0c5f78", lw=3)
    ax.scatter([0], [0.1], s=100, color="#d85c41")
    for r in [0.22, 0.42, 0.62]:
        ax.add_patch(plt.Circle((0, 0.1), r, fill=False, color="#f2c66d", lw=1.5, alpha=0.55))


def motif_standing_waves(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 300)
    for k, y0, c in [(1, 0.48, "#0c5f78"), (2, 0.0, "#d85c41"), (3, -0.48, "#315f72")]:
        ax.plot(x, y0 + 0.16 * np.sin(k * np.pi * (x + 0.85) / 1.7), color=c, lw=2.2)
        ax.scatter([-0.85, 0.85], [y0, y0], color="#12212b", s=20)


def motif_paths(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 220)
    for i in range(9):
        amp = 0.12 * (i - 4) / 4
        y = -0.55 + 0.9 * (x + 0.85) / 1.7 + amp * np.sin(np.pi * (x + 0.85) / 1.7)
        ax.plot(x, y, color="#77b7c5", lw=1.2, alpha=0.45)
    ax.plot(x, -0.55 + 0.9 * (x + 0.85) / 1.7, color="#12212b", lw=3)


def motif_action_valley(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 150)
    y = np.linspace(-1, 1, 150)
    X, Y = np.meshgrid(x, y)
    Z = (Y - 0.4 * X**2) ** 2 + 0.12 * X**2
    ax.contourf(X, Y, Z, levels=18, cmap="YlOrBr_r", alpha=0.8)
    ax.plot(x, 0.4 * x**2, color="#0c5f78", lw=3)


def motif_paths_fixed(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_paths(ax, rng)
    ax.scatter([-0.85, 0.85], [-0.55, 0.35], s=120, color="#d85c41", zorder=5)


def motif_balance(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([-0.65, 0.65], [0, 0], color="#12212b", lw=4)
    ax.add_patch(plt.Circle((-0.55, -0.28), 0.22, color="#77b7c5", alpha=0.8, ec="#12212b"))
    ax.add_patch(plt.Circle((0.55, -0.28), 0.22, color="#f2c66d", alpha=0.85, ec="#12212b"))
    ax.plot([0, -0.55], [0, -0.28], color="#12212b", lw=2)
    ax.plot([0, 0.55], [0, -0.28], color="#12212b", lw=2)
    draw_arrow(ax, -0.9, 0.5, -0.15, 0.12, "#0c5f78", 2)
    draw_arrow(ax, 0.9, 0.5, 0.15, 0.12, "#d85c41", 2)


def motif_two_surfaces(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 300)
    y1 = 0.22 * np.sin(5 * x) + 0.22
    y2 = 0.22 * np.sin(5 * x + 0.6) - 0.25
    ax.fill_between(x, y1 - 0.06, y1 + 0.06, color="#77b7c5", alpha=0.25)
    ax.fill_between(x, y2 - 0.06, y2 + 0.06, color="#f2c66d", alpha=0.25)
    ax.plot(x, y1, color="#0c5f78", lw=3)
    ax.plot(x, y2, color="#d85c41", lw=3)


def motif_curvilinear(ax: plt.Axes, rng: np.random.Generator) -> None:
    vals = np.linspace(-0.8, 0.8, 8)
    for v in vals:
        t = np.linspace(-0.85, 0.85, 160)
        ax.plot(t, v + 0.18 * np.sin(2.5 * t), color="#77b7c5", lw=1.2)
        ax.plot(v + 0.18 * np.sin(2.5 * t), t, color="#d8d1c4", lw=1.2)
    ax.plot(np.linspace(-0.75, 0.75, 100), 0.25 * np.sin(4 * np.linspace(-0.75, 0.75, 100)), color="#12212b", lw=3)


def motif_constraint(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 250)
    ax.plot(0.75 * np.cos(theta), 0.38 * np.sin(theta), color="#77b7c5", lw=8, alpha=0.3)
    ax.plot(0.75 * np.cos(theta), 0.38 * np.sin(theta), color="#0c5f78", lw=2.5)
    phi = np.linspace(0.4, 2.6, 80)
    ax.plot(0.75 * np.cos(phi), 0.38 * np.sin(phi), color="#d85c41", lw=4)


def motif_energy(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 300)
    a = 0.4 + 0.28 * np.sin(2 * np.pi * (x + 0.95) / 1.9)
    b = 0.4 - 0.28 * np.sin(2 * np.pi * (x + 0.95) / 1.9)
    ax.plot(x, a, color="#0c5f78", lw=3)
    ax.plot(x, b, color="#d85c41", lw=3)
    ax.plot(x, a + b - 0.65, color="#12212b", lw=2)


def motif_phase_space(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 300)
    for r in [0.25, 0.45, 0.65]:
        ax.plot(r * np.cos(theta), 0.65 * r * np.sin(theta), color="#77b7c5", lw=1.5)
    for a in np.linspace(0, 2 * np.pi, 10, endpoint=False):
        draw_arrow(ax, 0.5 * np.cos(a), 0.325 * np.sin(a), 0.5 * np.cos(a + 0.22), 0.325 * np.sin(a + 0.22), "#d85c41", 1.3)
    ax.axhline(0, color="#12212b", lw=1)
    ax.axvline(0, color="#12212b", lw=1)


def motif_oscillator(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 300)
    ax.plot(x, 0.75 * x**2 - 0.65, color="#0c5f78", lw=3)
    ax.scatter([-0.42], [0.75 * 0.42**2 - 0.65], color="#d85c41", s=90)
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(0.28 * np.cos(theta) + 0.55, 0.18 * np.sin(theta) + 0.45, color="#12212b", lw=2)


def motif_chain(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.75, 0.75, 8)
    ys = 0.18 * np.sin(np.linspace(0, 2 * np.pi, 8))
    ax.plot(xs, ys, color="#12212b", lw=2)
    for x, y in zip(xs, ys):
        ax.add_patch(plt.Circle((x, y), 0.07, color="#77b7c5", ec="#12212b"))
        ax.plot([x, x], [y, -0.7], color="#d8d1c4", lw=1)


def motif_dispersion(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    y = -0.65 + 0.55 * np.sqrt(0.18 + 2.3 * x**2)
    ax.plot(x, y, color="#0c5f78", lw=3)
    ax.fill_between(x, -0.65, y, color="#77b7c5", alpha=0.25)
    ax.axhline(-0.65, color="#12212b", lw=1)
    ax.axvline(0, color="#12212b", lw=1)


def motif_chain_to_wave(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.85, 0.85, 18)
    ys = 0.35 * np.sin(2 * np.pi * (xs + 0.85) / 1.7) - 0.35
    ax.scatter(xs, ys, s=45, color="#d85c41")
    x = np.linspace(-0.85, 0.85, 300)
    ax.plot(x, 0.35 * np.sin(2 * np.pi * (x + 0.85) / 1.7) + 0.35, color="#0c5f78", lw=3)


def motif_stress(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_grid(ax, 0, alpha=0.25)
    for x in np.linspace(-0.65, 0.65, 4):
        for y in np.linspace(-0.45, 0.45, 3):
            draw_arrow(ax, x - 0.08, y, x + 0.12, y + 0.05 * np.sin(3 * x), "#0c5f78", 1.5)
            draw_arrow(ax, x, y - 0.08, x + 0.03 * np.cos(2 * y), y + 0.12, "#d85c41", 1.5)


def motif_shift_pattern(ax: plt.Axes, rng: np.random.Generator) -> None:
    for offset, c in [(-0.22, "#77b7c5"), (0.22, "#f2c66d")]:
        xs = np.linspace(-0.8, 0.8, 9) + offset
        ax.scatter(xs, 0.25 * np.sin(8 * xs), s=70, color=c, edgecolor="#12212b", alpha=0.75)
    draw_arrow(ax, -0.25, -0.55, 0.25, -0.55, "#d85c41", 2.5)


def motif_lightcone(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([0, -0.65], [-0.75, 0.75], color="#0c5f78", lw=3)
    ax.plot([0, 0.65], [-0.75, 0.75], color="#0c5f78", lw=3)
    ax.plot([0, -0.65], [0.75, -0.75], color="#d85c41", lw=2, alpha=0.65)
    ax.plot([0, 0.65], [0.75, -0.75], color="#d85c41", lw=2, alpha=0.65)
    ax.fill([-0.65, 0, 0.65, 0], [0.75, 0, 0.75, 0], color="#77b7c5", alpha=0.2)
    ax.scatter([0], [0], color="#12212b", s=60)


def motif_boost(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.axhline(0, color="#d8d1c4", lw=2)
    ax.axvline(0, color="#d8d1c4", lw=2)
    draw_arrow(ax, 0, 0, 0.72, 0, "#12212b", 2)
    draw_arrow(ax, 0, 0, 0, 0.72, "#12212b", 2)
    draw_arrow(ax, 0, 0, 0.72, 0.28, "#0c5f78", 2.5)
    draw_arrow(ax, 0, 0, 0.28, 0.72, "#d85c41", 2.5)


def motif_mass_shell(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    y = 0.25 * np.sqrt(1 + 5 * x**2)
    ax.plot(x, y, color="#0c5f78", lw=3)
    ax.plot(x, -y, color="#d85c41", lw=2.2, alpha=0.75)
    ax.axhline(0, color="#12212b", lw=1)
    ax.axvline(0, color="#12212b", lw=1)


def motif_causal_diamond(ax: plt.Axes, rng: np.random.Generator) -> None:
    pts = np.array([[0, 0.8], [0.55, 0], [0, -0.8], [-0.55, 0], [0, 0.8]])
    ax.fill(pts[:, 0], pts[:, 1], color="#77b7c5", alpha=0.25)
    ax.plot(pts[:, 0], pts[:, 1], color="#0c5f78", lw=3)
    ax.scatter([0], [0], s=70, color="#d85c41")


def motif_vector_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    for x in np.linspace(-0.75, 0.75, 6):
        for y in np.linspace(-0.55, 0.55, 5):
            u = -y
            v = x
            norm = math.hypot(u, v) or 1
            draw_arrow(ax, x, y, x + 0.14 * u / norm, y + 0.14 * v / norm, "#0c5f78", 1.2, 0.8)
    ax.add_patch(plt.Circle((0, 0), 0.08, color="#d85c41", alpha=0.8))


def motif_gauge_orbit(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 250)
    for off, c in [(-0.28, "#77b7c5"), (0.18, "#f2c66d")]:
        ax.plot(0.56 * np.cos(theta) + off, 0.24 * np.sin(theta) + 0.25 * off, color=c, lw=3, alpha=0.85)
    ax.scatter([-0.28, 0.18], [-0.07, 0.045], color="#d85c41", s=60)


def motif_em_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    for x in np.linspace(-0.7, 0.7, 6):
        draw_arrow(ax, x, -0.6, x, 0.55, "#0c5f78", 1.6, 0.7)
    for y in np.linspace(-0.45, 0.45, 5):
        ax.plot(0.22 * np.sin(np.linspace(0, 2 * np.pi, 120)) + 0.05, y + 0.1 * np.cos(np.linspace(0, 2 * np.pi, 120)), color="#d85c41", lw=1.5, alpha=0.75)


def motif_polarization(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 180)
    ax.plot(x, 0.15 * np.sin(12 * x), color="#12212b", lw=2)
    for x0 in np.linspace(-0.7, 0.7, 7):
        draw_arrow(ax, x0, 0.15 * np.sin(12 * x0), x0, 0.15 * np.sin(12 * x0) + 0.35 * np.cos(4 * x0), "#0c5f78", 1.6)


def motif_commutator(ax: plt.Axes, rng: np.random.Generator) -> None:
    pts = [(-0.55, -0.45), (0.35, -0.35), (0.5, 0.45), (-0.3, 0.35)]
    draw_arrow(ax, *pts[0], *pts[1], "#0c5f78", 2.5)
    draw_arrow(ax, *pts[1], *pts[2], "#d85c41", 2.5)
    draw_arrow(ax, *pts[0], *pts[3], "#d85c41", 2.5)
    draw_arrow(ax, *pts[3], pts[2][0] - 0.18, pts[2][1] + 0.03, "#0c5f78", 2.5)
    ax.scatter([pts[2][0]], [pts[2][1]], color="#12212b", s=70)


def motif_sphere_axes(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 250)
    ax.plot(0.62 * np.cos(theta), 0.62 * np.sin(theta), color="#77b7c5", lw=3)
    ax.plot(0.62 * np.cos(theta), 0.18 * np.sin(theta), color="#77b7c5", lw=1.4, alpha=0.7)
    draw_arrow(ax, 0, 0, 0.15, 0.72, "#d85c41", 2.5)
    draw_arrow(ax, 0, 0, 0.62, -0.15, "#0c5f78", 2.5)


def motif_helix(ax: plt.Axes, rng: np.random.Generator) -> None:
    t = np.linspace(0, 4 * np.pi, 400)
    x = -0.8 + 1.6 * t / t.max()
    y = 0.35 * np.sin(t)
    ax.plot(x, y, color="#0c5f78", lw=2.5)
    ax.plot(x, 0.35 * np.cos(t), color="#d85c41", lw=1.5, alpha=0.6)


def motif_exchange(ax: plt.Axes, rng: np.random.Generator) -> None:
    t = np.linspace(0, 1, 200)
    ax.plot(-0.75 + 1.5 * t, -0.45 + 0.75 * t + 0.18 * np.sin(np.pi * t), color="#0c5f78", lw=3)
    ax.plot(-0.75 + 1.5 * t, 0.45 - 0.75 * t - 0.18 * np.sin(np.pi * t), color="#d85c41", lw=3)
    ax.scatter([-0.75, -0.75, 0.75, 0.75], [-0.45, 0.45, 0.3, -0.3], color="#12212b", s=40)


def motif_timeline(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([-0.85, 0.85], [0, 0], color="#12212b", lw=2)
    for x, c in zip([-0.55, -0.15, 0.25, 0.62], ["#77b7c5", "#f2c66d", "#d85c41", "#315f72"]):
        ax.plot([x, x], [-0.25, 0.25], color=c, lw=4)
        ax.scatter([x], [0], s=80, color=c, edgecolor="#12212b")
    draw_arrow(ax, 0.65, 0, 0.85, 0, "#12212b", 2)


def motif_transition(ax: plt.Axes, rng: np.random.Generator) -> None:
    ys = [-0.5, 0.1, 0.55]
    for y in ys:
        ax.plot([-0.65, 0.65], [y, y], color="#12212b", lw=2)
    draw_arrow(ax, -0.25, ys[0] + 0.05, 0.25, ys[2] - 0.05, "#d85c41", 3)


def motif_branching(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.75, 0, -0.25, 0, "#12212b", 2)
    for y in [-0.45, 0, 0.45]:
        draw_arrow(ax, -0.25, 0, 0.35, y, "#0c5f78", 2)
        draw_arrow(ax, 0.35, y, 0.75, 0.6 * y, "#d85c41", 1.6, 0.75)


def motif_ramp(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    y = -0.55 + 0.95 / (1 + np.exp(-6 * x))
    ax.plot(x, y, color="#0c5f78", lw=3)
    ax.fill_between(x, -0.55, y, color="#77b7c5", alpha=0.25)


def motif_path_bundle(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 240)
    for i in range(22):
        amp = rng.normal(0, 0.09)
        phase = rng.uniform(0, 2 * np.pi)
        y = -0.55 + 0.75 * (x + 0.85) / 1.7 + amp * np.sin(2 * np.pi * (x + 0.85) / 1.7 + phase)
        ax.plot(x, y, color="#77b7c5", lw=0.8, alpha=0.35)
    ax.plot(x, -0.55 + 0.75 * (x + 0.85) / 1.7, color="#12212b", lw=3)


def motif_time_slices(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 240)
    y = 0.35 * np.sin(2.5 * x) - 0.1
    ax.plot(x, y, color="#12212b", lw=3)
    for x0 in np.linspace(-0.75, 0.75, 9):
        ax.plot([x0, x0], [-0.75, 0.75], color="#77b7c5", lw=1.4, alpha=0.65)
        ax.scatter([x0], [0.35 * np.sin(2.5 * x0) - 0.1], color="#d85c41", s=30)


def motif_source_path(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 240)
    y = 0.35 * np.sin(2.5 * x) - 0.1
    ax.plot(x, y, color="#12212b", lw=3)
    for x0 in [-0.4, 0.18, 0.55]:
        yy = 0.35 * np.sin(2.5 * x0) - 0.1
        ax.add_patch(plt.Circle((x0, yy), 0.11, color="#f2c66d", ec="#d85c41", lw=2, alpha=0.85))


def motif_multi_oscillator(ax: plt.Axes, rng: np.random.Generator) -> None:
    for i, x0 in enumerate(np.linspace(-0.75, 0.75, 5)):
        x = np.linspace(-0.14, 0.14, 80)
        ax.plot(x0 + x, 0.9 * x**2 + 0.12 * np.sin(i) - 0.35, color="#0c5f78", lw=2)
        ax.scatter([x0], [0.12 * np.sin(i) - 0.35], color="#d85c41", s=35)


def motif_wavefronts(ax: plt.Axes, rng: np.random.Generator) -> None:
    for x0 in np.linspace(-0.8, 0.8, 9):
        ax.plot([x0 - 0.25, x0 + 0.25], [-0.7, 0.7], color="#0c5f78", lw=1.8, alpha=0.7)
    draw_arrow(ax, -0.75, -0.55, 0.75, 0.55, "#d85c41", 2.5)


def motif_box_modes(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.add_patch(plt.Rectangle((-0.8, -0.55), 1.6, 1.1, fill=False, ec="#12212b", lw=2.5))
    x = np.linspace(-0.8, 0.8, 250)
    for k, off, c in [(1, 0.25, "#0c5f78"), (2, -0.15, "#d85c41")]:
        ax.plot(x, off + 0.18 * np.sin(k * np.pi * (x + 0.8) / 1.6), color=c, lw=2)


def motif_occupation(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.75, 0.75, 7)
    vals = [0.18, 0.52, 0.25, 0.75, 0.35, 0.12, 0.42]
    ax.bar(xs, vals, width=0.14, bottom=-0.7, color="#77b7c5", edgecolor="#12212b", linewidth=0.8)
    ax.scatter(xs, np.array(vals) - 0.7, color="#d85c41", s=25)


def motif_vacuum(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    y = 0.08 * np.sin(30 * x) * np.exp(-0.8 * x**2)
    ax.fill_between(x, -0.15 + y, 0.15 + y, color="#77b7c5", alpha=0.22)
    ax.plot(x, y, color="#0c5f78", lw=2)
    ax.axhline(0, color="#12212b", lw=1.5)


def motif_propagator(ax: plt.Axes, rng: np.random.Generator) -> None:
    p1 = (-0.65, -0.35)
    p2 = (0.62, 0.38)
    ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], s=100, color="#d85c41", zorder=5)
    x = np.linspace(p1[0], p2[0], 200)
    y = np.linspace(p1[1], p2[1], 200) + 0.08 * np.sin(np.linspace(0, 8 * np.pi, 200))
    ax.plot(x, y, color="#0c5f78", lw=3)


def motif_contour_path(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.scatter([-0.25, 0.35], [0, 0], color="#d85c41", s=80)
    x = np.linspace(-0.85, 0.85, 300)
    y = 0.18 * np.sin(2 * np.pi * (x + 0.85) / 1.7)
    y += 0.25 * np.exp(-60 * (x + 0.25) ** 2) - 0.22 * np.exp(-60 * (x - 0.35) ** 2)
    ax.plot(x, y, color="#0c5f78", lw=3)


def motif_source_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_field_surface(ax, rng)
    for p in [(-0.45, 0.35), (0.2, -0.2), (0.55, 0.45)]:
        ax.scatter([p[0]], [p[1]], s=100, color="#f2c66d", edgecolor="#12212b", zorder=5)


def motif_network(ax: plt.Axes, rng: np.random.Generator) -> None:
    pts = np.array([[-0.65, 0.35], [-0.35, -0.35], [0.0, 0.1], [0.35, -0.42], [0.62, 0.32], [0.0, 0.62]])
    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (2, 5), (1, 3)]
    for i, j in edges:
        ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color="#0c5f78", lw=2, alpha=0.75)
    ax.scatter(pts[:, 0], pts[:, 1], s=130, color="#f2c66d", edgecolor="#12212b")


def motif_pairings(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.75, 0.75, 6)
    ax.scatter(xs, np.zeros_like(xs) - 0.5, s=70, color="#12212b")
    pairs = [(0, 3), (1, 5), (2, 4)]
    for i, j in pairs:
        t = np.linspace(0, np.pi, 100)
        cx = 0.5 * (xs[i] + xs[j])
        rx = 0.5 * abs(xs[j] - xs[i])
        ax.plot(cx + rx * np.cos(t), -0.5 + 0.24 * (j - i) * np.sin(t), color="#0c5f78", lw=2)


def motif_potential(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    y = 0.9 * (x**4 - 0.75 * x**2) - 0.2
    ax.plot(x, y, color="#0c5f78", lw=3)
    ax.axhline(0, color="#d8d1c4", lw=1)


def motif_vertex4(ax: plt.Axes, rng: np.random.Generator) -> None:
    for a in [0.2, 1.25, 3.45, 5.1]:
        draw_arrow(ax, 0.78 * np.cos(a), 0.78 * np.sin(a), 0.08 * np.cos(a), 0.08 * np.sin(a), "#0c5f78", 2.5)
    ax.scatter([0], [0], s=110, color="#d85c41")


def motif_potential_family(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 300)
    for lam, c in [(0.5, "#77b7c5"), (0.9, "#0c5f78"), (1.4, "#d85c41")]:
        y = lam * (x**4 - 0.65 * x**2) - 0.25
        ax.plot(x, y, color=c, lw=2.2)


def motif_feynman(ax: plt.Axes, rng: np.random.Generator) -> None:
    pts = [(-0.75, -0.45), (-0.18, -0.05), (0.18, 0.08), (0.75, 0.45), (-0.7, 0.48), (0.7, -0.5)]
    for i, j in [(0, 1), (1, 2), (2, 3), (4, 1), (2, 5)]:
        ax.plot([pts[i][0], pts[j][0]], [pts[i][1], pts[j][1]], color="#0c5f78", lw=2.6)
    ax.scatter([pts[1][0], pts[2][0]], [pts[1][1], pts[2][1]], s=70, color="#d85c41")


def motif_momentum_vertex(ax: plt.Axes, rng: np.random.Generator) -> None:
    for a, outward in [(0.35, False), (2.6, False), (-0.9, True), (1.25, True)]:
        if outward:
            draw_arrow(ax, 0.08 * np.cos(a), 0.08 * np.sin(a), 0.78 * np.cos(a), 0.78 * np.sin(a), "#0c5f78", 2.2)
        else:
            draw_arrow(ax, 0.78 * np.cos(a), 0.78 * np.sin(a), 0.08 * np.cos(a), 0.08 * np.sin(a), "#d85c41", 2.2)
    ax.scatter([0], [0], s=120, color="#12212b")


def motif_tree_diagram(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.85, -0.35, -0.2, 0, "#0c5f78", 2.2)
    draw_arrow(ax, -0.85, 0.35, -0.2, 0, "#0c5f78", 2.2)
    draw_arrow(ax, -0.2, 0, 0.2, 0, "#12212b", 2.2)
    draw_arrow(ax, 0.2, 0, 0.85, -0.35, "#d85c41", 2.2)
    draw_arrow(ax, 0.2, 0, 0.85, 0.35, "#d85c41", 2.2)


def motif_loop(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 240)
    ax.plot(0.38 * np.cos(theta), 0.38 * np.sin(theta), color="#0c5f78", lw=3)
    ax.plot([-0.85, -0.38], [0, 0], color="#12212b", lw=2.2)
    ax.plot([0.38, 0.85], [0, 0], color="#12212b", lw=2.2)
    draw_arrow(ax, 0.36, 0.04, 0.28, 0.24, "#d85c41", 2)


def motif_scattering(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.9, -0.35, -0.12, -0.05, "#0c5f78", 2.5)
    draw_arrow(ax, -0.9, 0.35, -0.12, 0.05, "#0c5f78", 2.5)
    draw_arrow(ax, 0.12, 0.05, 0.9, 0.55, "#d85c41", 2.5)
    draw_arrow(ax, 0.12, -0.05, 0.9, -0.45, "#d85c41", 2.5)
    ax.add_patch(plt.Circle((0, 0), 0.16, color="#f2c66d", ec="#12212b"))


def motif_beam_target(ax: plt.Axes, rng: np.random.Generator) -> None:
    for y in np.linspace(-0.4, 0.4, 5):
        draw_arrow(ax, -0.9, y, -0.15, y, "#0c5f78", 1.8)
    ax.add_patch(plt.Circle((0.18, 0), 0.38, color="#f2c66d", alpha=0.45, ec="#12212b", lw=2))
    for a in np.linspace(-0.8, 0.8, 5):
        draw_arrow(ax, 0.18, 0, 0.85, a, "#d85c41", 1.4, 0.75)


def motif_amputation(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([-0.85, -0.35], [0.45, 0.15], color="#d8d1c4", lw=5)
    ax.plot([0.35, 0.85], [-0.15, -0.45], color="#d8d1c4", lw=5)
    ax.plot([-0.35, 0.35], [0.15, -0.15], color="#0c5f78", lw=3)
    ax.plot([-0.45, -0.25], [0.02, 0.28], color="#d85c41", lw=3)
    ax.plot([0.25, 0.45], [-0.28, -0.02], color="#d85c41", lw=3)


def motif_wave_packets(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.95, 0.95, 600)
    y1 = np.exp(-45 * (x + 0.55) ** 2) * np.sin(45 * x)
    y2 = np.exp(-45 * (x - 0.55) ** 2) * np.sin(45 * x)
    ax.plot(x, y1 + 0.28, color="#0c5f78", lw=2)
    ax.plot(x, y2 - 0.28, color="#d85c41", lw=2)


def motif_self_energy(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([-0.85, -0.25], [0, 0], color="#12212b", lw=2.5)
    ax.plot([0.25, 0.85], [0, 0], color="#12212b", lw=2.5)
    theta = np.linspace(0, 2 * np.pi, 220)
    ax.plot(0.25 * np.cos(theta), 0.28 * np.sin(theta), color="#0c5f78", lw=3)
    ax.scatter([-0.25, 0.25], [0, 0], s=60, color="#d85c41")


def motif_vertex_loop(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_vertex4(ax, rng)
    theta = np.linspace(0, 2 * np.pi, 120)
    ax.plot(0.28 * np.cos(theta), 0.28 * np.sin(theta) + 0.32, color="#f2a23a", lw=2.5)


def motif_cutoff_shell(ax: plt.Axes, rng: np.random.Generator) -> None:
    for r, c, a in [(0.8, "#d85c41", 0.18), (0.56, "#77b7c5", 0.32), (0.32, "#f2c66d", 0.45)]:
        ax.add_patch(plt.Circle((0, 0), r, color=c, alpha=a, ec="#12212b", lw=1.4 if r == 0.8 else 0.8))
    ax.scatter([0], [0], s=40, color="#12212b")


def motif_counterterm(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.plot([-0.85, 0.85], [0, 0], color="#0c5f78", lw=3)
    ax.add_patch(plt.Rectangle((-0.1, -0.17), 0.2, 0.34, facecolor="#f2c66d", edgecolor="#d85c41", lw=2))
    for y in [-0.45, 0.45]:
        draw_arrow(ax, -0.55, y, -0.12, 0.05 * np.sign(y), "#d85c41", 1.5, 0.75)
        draw_arrow(ax, 0.12, 0.05 * np.sign(y), 0.55, y, "#d85c41", 1.5, 0.75)


def motif_shells(ax: plt.Axes, rng: np.random.Generator) -> None:
    for i, r in enumerate([0.22, 0.42, 0.62, 0.82]):
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ec=["#f2c66d", "#77b7c5", "#0c5f78", "#d85c41"][i], lw=3 - 0.2 * i, alpha=0.8))


def motif_target(ax: plt.Axes, rng: np.random.Generator) -> None:
    for r, c in [(0.78, "#d85c41"), (0.55, "#f2c66d"), (0.32, "#77b7c5"), (0.12, "#12212b")]:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ec=c, lw=3))
    ax.scatter([0], [0], s=55, color="#12212b")


def motif_parallel_flows(ax: plt.Axes, rng: np.random.Generator) -> None:
    for y, c in [(-0.45, "#0c5f78"), (0, "#f2c66d"), (0.45, "#d85c41")]:
        x = np.linspace(-0.85, 0.85, 140)
        ax.plot(x, y + 0.08 * np.sin(4 * x), color=c, lw=2.2)
        draw_arrow(ax, 0.55, y + 0.08 * np.sin(4 * 0.55), 0.75, y + 0.08 * np.sin(4 * 0.75), c, 2)


def motif_rg_flow(ax: plt.Axes, rng: np.random.Generator) -> None:
    for x0 in np.linspace(-0.75, 0.65, 6):
        for y0 in np.linspace(-0.55, 0.55, 4):
            u = 0.25 - 0.45 * x0
            v = -0.25 * y0 + 0.12 * np.sin(3 * x0)
            norm = math.hypot(u, v) or 1
            draw_arrow(ax, x0, y0, x0 + 0.16 * u / norm, y0 + 0.16 * v / norm, "#0c5f78", 1.1, 0.7)
    ax.plot(np.linspace(-0.75, 0.75, 150), 0.25 * np.sin(2 * np.linspace(-0.75, 0.75, 150)), color="#d85c41", lw=3)


def motif_rg_fixed(ax: plt.Axes, rng: np.random.Generator) -> None:
    for a in np.linspace(0, 2 * np.pi, 14, endpoint=False):
        draw_arrow(ax, 0.8 * np.cos(a), 0.6 * np.sin(a), 0.28 * np.cos(a), 0.21 * np.sin(a), "#0c5f78", 1.5, 0.7)
    ax.scatter([0], [0], s=110, color="#d85c41")


def motif_saddle_flow(ax: plt.Axes, rng: np.random.Generator) -> None:
    for y in np.linspace(-0.55, 0.55, 5):
        draw_arrow(ax, -0.7, y, -0.18, 0.35 * y, "#0c5f78", 1.4)
        draw_arrow(ax, 0.18, 0.35 * y, 0.7, y, "#d85c41", 1.4)
    ax.scatter([0], [0], s=90, color="#12212b")


def motif_tree_loop(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_tree_diagram(ax, rng)
    theta = np.linspace(0, 2 * np.pi, 120)
    ax.plot(0.16 * np.cos(theta) + 0.0, 0.16 * np.sin(theta) + 0.36, color="#f2a23a", lw=2)


def motif_coarse(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.9, 0.9, 400)
    rough = 0.25 * np.sin(16 * x) + 0.12 * np.sin(45 * x)
    smooth = 0.25 * np.sin(16 * x)
    ax.plot(x, rough + 0.3, color="#d85c41", lw=1.3, alpha=0.8)
    ax.plot(x, smooth - 0.25, color="#0c5f78", lw=3)


def motif_bars_flow(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.65, 0.65, 5)
    vals1 = np.array([0.6, 0.45, 0.3, 0.2, 0.1])
    vals2 = np.array([0.25, 0.36, 0.45, 0.4, 0.2])
    ax.bar(xs - 0.035, vals1, width=0.06, bottom=-0.65, color="#77b7c5")
    ax.bar(xs + 0.035, vals2, width=0.06, bottom=-0.65, color="#d85c41")
    for x in xs:
        draw_arrow(ax, x - 0.08, 0.45, x + 0.08, 0.45, "#12212b", 1.1)


def motif_converging_flows(ax: plt.Axes, rng: np.random.Generator) -> None:
    for y in np.linspace(-0.65, 0.65, 7):
        x = np.linspace(-0.85, 0.65, 140)
        curve = y * np.exp(-1.8 * (x + 0.85)) + 0.12 * np.sin(3 * x)
        ax.plot(x, curve, color="#77b7c5", lw=1.8, alpha=0.75)
        draw_arrow(ax, 0.45, curve[-20], 0.65, curve[-1], "#d85c41", 1.5)


def motif_target_band(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.add_patch(plt.Rectangle((-0.2, -0.75), 0.4, 1.5, color="#f2c66d", alpha=0.35))
    xs = np.linspace(-0.85, 0.85, 9)
    ax.plot(xs, 0.55 * np.sin(3 * xs), color="#0c5f78", lw=3)


def motif_ope(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.scatter([-0.18, 0.18], [0, 0], s=80, color="#d85c41")
    for r in [0.22, 0.45, 0.68]:
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ec="#77b7c5", lw=2, alpha=0.65))
    draw_arrow(ax, -0.7, 0.55, -0.18, 0.08, "#0c5f78", 1.5)
    draw_arrow(ax, 0.7, -0.55, 0.18, -0.08, "#0c5f78", 1.5)


def motif_manifold(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 240)
    ax.fill(0.75 * np.cos(theta), 0.35 * np.sin(theta), color="#77b7c5", alpha=0.25)
    ax.plot(0.75 * np.cos(theta), 0.35 * np.sin(theta), color="#0c5f78", lw=3)
    for a in [0.4, 1.8, 3.2, 5.0]:
        x, y = 0.55 * np.cos(a), 0.26 * np.sin(a)
        draw_arrow(ax, x, y, x - 0.18 * np.sin(a), y + 0.1 * np.cos(a), "#d85c41", 1.8)


def motif_tangent_manifold(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_manifold(ax, rng)
    draw_arrow(ax, -0.1, 0.0, 0.55, 0.18, "#12212b", 3)


def motif_multiplet(ax: plt.Axes, rng: np.random.Generator) -> None:
    coords = [(-0.35, 0.35), (0.35, 0.35), (-0.35, -0.35), (0.35, -0.35)]
    for x, y in coords:
        ax.add_patch(plt.Circle((x, y), 0.18, color="#77b7c5", ec="#12212b", alpha=0.8))
    for i, j in [(0, 1), (1, 3), (3, 2), (2, 0)]:
        ax.plot([coords[i][0], coords[j][0]], [coords[i][1], coords[j][1]], color="#d85c41", lw=2)


def motif_weight_lattice(ax: plt.Axes, rng: np.random.Generator) -> None:
    pts = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            if abs(i + j) <= 2:
                pts.append((0.24 * (i + 0.5 * j), 0.21 * math.sqrt(3) * j))
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=65, color="#f2c66d", edgecolor="#12212b")
    ax.axhline(0, color="#d8d1c4", lw=1)
    ax.axvline(0, color="#d8d1c4", lw=1)


def motif_phase_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    for x in np.linspace(-0.65, 0.65, 5):
        for y in np.linspace(-0.45, 0.45, 4):
            a = 4 * x + 2 * y
            draw_arrow(ax, x, y, x + 0.12 * np.cos(a), y + 0.12 * np.sin(a), "#0c5f78", 1.3)


def motif_matrix_flow(ax: plt.Axes, rng: np.random.Generator) -> None:
    for i, x in enumerate([-0.55, -0.25, 0.05, 0.35]):
        ax.add_patch(plt.Rectangle((x, -0.45), 0.18, 0.9, facecolor="#77b7c5", edgecolor="#12212b", alpha=0.55))
    for y in [-0.3, 0, 0.3]:
        draw_arrow(ax, -0.8, y, 0.75, -y * 0.7, "#d85c41", 1.5, 0.8)


def motif_fermion_line(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.85, -0.25, 0.85, 0.25, "#0c5f78", 3)
    for x in np.linspace(-0.55, 0.55, 4):
        ax.plot([x - 0.08, x + 0.08], [-0.12 + 0.29 * (x + 0.55), -0.12 + 0.29 * (x + 0.55) + 0.08], color="#d85c41", lw=2)


def motif_lattice_links(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.6, 0.6, 4)
    ys = np.linspace(-0.45, 0.45, 4)
    for x in xs:
        for y in ys:
            ax.scatter([x], [y], s=35, color="#12212b")
    for x in xs[:-1]:
        for y in ys:
            draw_arrow(ax, x + 0.03, y, x + 0.27, y, "#0c5f78", 1)
    for x in xs:
        for y in ys[:-1]:
            draw_arrow(ax, x, y + 0.03, x, y + 0.24, "#d85c41", 1)


def motif_photon_line(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.75, 0.75, 300)
    y = 0.12 * np.sin(35 * x)
    ax.plot(x, y, color="#0c5f78", lw=2.5)
    ax.scatter([-0.82, 0.82], [0, 0], s=80, color="#d85c41")


def motif_qed_vertex(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.75, -0.4, 0, 0, "#12212b", 2.5)
    draw_arrow(ax, 0, 0, 0.75, -0.4, "#12212b", 2.5)
    x = np.linspace(0, 0.65, 150)
    ax.plot(0.0 + 0.08 * np.sin(35 * x), x, color="#0c5f78", lw=2.5)
    ax.scatter([0], [0], s=100, color="#d85c41")


def motif_gauge_slice(ax: plt.Axes, rng: np.random.Generator) -> None:
    for off in [-0.45, 0, 0.45]:
        theta = np.linspace(-0.2, 2.8, 160)
        ax.plot(0.55 * np.cos(theta) + off, 0.26 * np.sin(theta) + 0.18 * off, color="#77b7c5", lw=2)
    ax.plot([-0.65, 0.65], [-0.55, 0.55], color="#d85c41", lw=4, alpha=0.75)


def motif_yang_mills_vertices(ax: plt.Axes, rng: np.random.Generator) -> None:
    for center in [(-0.38, 0.0), (0.42, 0.0)]:
        n = 3 if center[0] < 0 else 4
        for a in np.linspace(0, 2 * np.pi, n, endpoint=False):
            x = np.linspace(0, 0.33, 80)
            ax.plot(center[0] + x * np.cos(a) + 0.03 * np.sin(25 * x) * np.sin(a), center[1] + x * np.sin(a) - 0.03 * np.sin(25 * x) * np.cos(a), color="#0c5f78", lw=2)
        ax.scatter([center[0]], [center[1]], s=70, color="#d85c41")


def motif_braid(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-0.85, 0.85, 300)
    for phase, c in [(0, "#0c5f78"), (2.1, "#d85c41"), (4.2, "#f2a23a")]:
        ax.plot(x, 0.28 * np.sin(5 * x + phase), color=c, lw=2.3)


def motif_ghost_loop(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 240)
    ax.plot(0.42 * np.cos(theta), 0.42 * np.sin(theta), color="#315f72", lw=3, ls="--")
    draw_arrow(ax, 0.39, 0.1, 0.3, 0.28, "#d85c41", 2)
    ax.plot([-0.85, -0.42], [0, 0], color="#12212b", lw=2)
    ax.plot([0.42, 0.85], [0, 0], color="#12212b", lw=2)


def motif_mexican_hat(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 170)
    y = np.linspace(-1, 1, 170)
    X, Y = np.meshgrid(x, y)
    R2 = X**2 + Y**2
    Z = (R2 - 0.42) ** 2
    ax.contourf(X, Y, Z, levels=16, cmap="YlOrBr_r", alpha=0.85)
    ax.contour(X, Y, Z, levels=[0.02, 0.08, 0.18, 0.35], colors="#12212b", linewidths=0.6)
    ax.scatter([0.65], [0], s=80, color="#d85c41")


def motif_mexican_contours(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_mexican_hat(ax, rng)
    draw_arrow(ax, 0.65, 0, 0.65, 0.32, "#0c5f78", 2.4)
    draw_arrow(ax, 0.65, 0, 0.9, 0, "#d85c41", 2.4)


def motif_domains(ax: plt.Axes, rng: np.random.Generator) -> None:
    x = np.linspace(-1, 1, 120)
    y = np.linspace(-1, 1, 120)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(5 * X) + np.cos(4 * Y) + 0.4 * np.sin(7 * (X + Y))
    ax.contourf(X, Y, Z, levels=[-3, -0.5, 0.3, 3], colors=["#77b7c5", "#f2c66d", "#d85c41"], alpha=0.55)
    ax.contour(X, Y, Z, levels=[-0.5, 0.3], colors="#12212b", linewidths=1)


def motif_higgs_eating(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 180)
    ax.plot(0.32 * np.cos(theta) - 0.35, 0.32 * np.sin(theta), color="#f2c66d", lw=3)
    x = np.linspace(-0.05, 0.75, 200)
    ax.plot(x, 0.1 * np.sin(30 * x), color="#0c5f78", lw=2.5)
    draw_arrow(ax, -0.12, 0.0, 0.12, 0.0, "#d85c41", 2.3)


def motif_blocks(ax: plt.Axes, rng: np.random.Generator) -> None:
    for i, x in enumerate(np.linspace(-0.75, -0.15, 4)):
        ax.add_patch(plt.Rectangle((x, 0.15), 0.12, 0.28, facecolor="#77b7c5", edgecolor="#12212b"))
    for i, x in enumerate(np.linspace(0.15, 0.75, 3)):
        ax.add_patch(plt.Rectangle((x, -0.25), 0.14, 0.42, facecolor="#f2c66d", edgecolor="#12212b"))
    draw_arrow(ax, -0.02, 0.1, 0.12, -0.02, "#d85c41", 2.2)


def motif_winding(ax: plt.Axes, rng: np.random.Generator) -> None:
    for off, turns, c in [(-0.5, 1, "#77b7c5"), (0, 2, "#f2c66d"), (0.5, 3, "#d85c41")]:
        t = np.linspace(0, 2 * np.pi * turns, 300)
        ax.plot(off + 0.12 * np.cos(t), -0.45 + 0.9 * t / t.max(), color=c, lw=2.2)


def motif_broken_balance(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_balance(ax, rng)
    ax.plot([-0.15, 0.15], [0.62, 0.28], color="#d85c41", lw=4)
    ax.plot([-0.15, 0.15], [0.28, 0.62], color="#d85c41", lw=4)


def motif_wilson_loop(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.add_patch(plt.Rectangle((-0.55, -0.35), 1.1, 0.7, fill=False, ec="#0c5f78", lw=4))
    for x in np.linspace(-0.4, 0.4, 5):
        draw_arrow(ax, x, -0.15, x + 0.12, 0.15, "#d85c41", 1.5)


def motif_flux_tube(ax: plt.Axes, rng: np.random.Generator) -> None:
    ax.add_patch(plt.Circle((-0.65, 0), 0.12, color="#d85c41", ec="#12212b"))
    ax.add_patch(plt.Circle((0.65, 0), 0.12, color="#0c5f78", ec="#12212b"))
    ax.plot([-0.55, 0.55], [0, 0], color="#f2a23a", lw=16, alpha=0.35, solid_capstyle="round")
    ax.plot([-0.55, 0.55], [0, 0], color="#f2a23a", lw=4, solid_capstyle="round")


def motif_lattice_field(ax: plt.Axes, rng: np.random.Generator) -> None:
    xs = np.linspace(-0.7, 0.7, 6)
    ys = np.linspace(-0.5, 0.5, 5)
    for x in xs:
        ax.plot([x, x], [ys[0], ys[-1]], color="#d8d1c4", lw=1)
    for y in ys:
        ax.plot([xs[0], xs[-1]], [y, y], color="#d8d1c4", lw=1)
    for x in xs:
        for y in ys:
            s = 30 + 80 * (0.5 + 0.5 * math.sin(4 * x + 3 * y))
            ax.scatter([x], [y], s=s, color="#77b7c5", edgecolor="#12212b", alpha=0.85)


def motif_plaquette(ax: plt.Axes, rng: np.random.Generator) -> None:
    motif_lattice_links(ax, rng)
    ax.add_patch(plt.Rectangle((-0.2, -0.15), 0.4, 0.3, fill=False, ec="#f2a23a", lw=5))


def motif_thermal_circle(ax: plt.Axes, rng: np.random.Generator) -> None:
    theta = np.linspace(0, 2 * np.pi, 240)
    ax.plot(0.38 * np.cos(theta), 0.38 * np.sin(theta), color="#0c5f78", lw=4)
    for x in np.linspace(-0.85, 0.85, 6):
        ax.plot([x, x], [-0.65, 0.65], color="#d8d1c4", lw=1)
    draw_arrow(ax, 0.38, 0, 0.25, 0.28, "#d85c41", 2.2)


def motif_grid_refine(ax: plt.Axes, rng: np.random.Generator) -> None:
    for offset, step, c in [(-0.45, 0.22, "#77b7c5"), (0.45, 0.11, "#d85c41")]:
        vals = np.arange(-0.35, 0.36, step)
        for v in vals:
            ax.plot([offset - 0.35, offset + 0.35], [v, v], color=c, lw=0.8)
            ax.plot([offset + v, offset + v], [-0.35, 0.35], color=c, lw=0.8)
    draw_arrow(ax, -0.05, 0, 0.05, 0, "#12212b", 2.2)


def motif_standard_model(ax: plt.Axes, rng: np.random.Generator) -> None:
    centers = [(-0.45, 0.25), (0.45, 0.25), (0, -0.35)]
    colors = ["#77b7c5", "#f2c66d", "#d85c41"]
    for c, col in zip(centers, colors):
        ax.add_patch(plt.Circle(c, 0.28, color=col, alpha=0.55, ec="#12212b", lw=2))
    for i, j in [(0, 1), (1, 2), (2, 0)]:
        ax.plot([centers[i][0], centers[j][0]], [centers[i][1], centers[j][1]], color="#12212b", lw=2)


def motif_yukawa(ax: plt.Axes, rng: np.random.Generator) -> None:
    draw_arrow(ax, -0.75, -0.35, 0, 0, "#12212b", 2.5)
    draw_arrow(ax, 0, 0, 0.75, -0.35, "#12212b", 2.5)
    ax.plot([0, 0], [0, 0.65], color="#d85c41", lw=3)
    ax.scatter([0], [0], s=100, color="#f2c66d", edgecolor="#12212b")


def motif_curved_grid(ax: plt.Axes, rng: np.random.Generator) -> None:
    vals = np.linspace(-0.8, 0.8, 8)
    for v in vals:
        t = np.linspace(-0.85, 0.85, 180)
        ax.plot(t, v + 0.12 * np.sin(4 * t + 2 * v), color="#77b7c5", lw=1)
        ax.plot(v + 0.12 * np.sin(4 * t + 2 * v), t, color="#d8d1c4", lw=1)
    ax.plot(np.linspace(-0.8, 0.8, 200), 0.2 * np.sin(5 * np.linspace(-0.8, 0.8, 200)), color="#d85c41", lw=3)


MOTIFS = {
    "curve": motif_curve,
    "bars": motif_bars,
    "boundary": motif_boundary,
    "nested": motif_nested,
    "flow": motif_flow,
    "stencil": motif_stencil,
    "vectors": motif_vectors,
    "projection": motif_projection,
    "rotated-grid": motif_rotated_grid,
    "ellipse": motif_ellipse,
    "frame-field": motif_frame_field,
    "contour": motif_contour,
    "surface-gradient": motif_surface_gradient,
    "flux": motif_flux,
    "curl": motif_curl,
    "deformed-grid": motif_deformed_grid,
    "field-surface": motif_field_surface,
    "phase": motif_phase,
    "wave": motif_wave,
    "phasor-sum": motif_phasor_sum,
    "spectrum": motif_spectrum,
    "wave-envelope": motif_wave_envelope,
    "linear-map": motif_linear_map,
    "matrix": motif_matrix,
    "eigen": motif_eigen,
    "basis-rays": motif_basis_rays,
    "ladder": motif_ladder,
    "overlap-waves": motif_overlap_waves,
    "state-arc": motif_state_arc,
    "fourier-stack": motif_fourier_stack,
    "delta": motif_delta,
    "green": motif_green,
    "wave-pair": motif_wave,
    "standing-waves": motif_standing_waves,
    "paths": motif_paths,
    "action-valley": motif_action_valley,
    "paths-fixed": motif_paths_fixed,
    "balance": motif_balance,
    "two-surfaces": motif_two_surfaces,
    "curvilinear": motif_curvilinear,
    "constraint": motif_constraint,
    "energy": motif_energy,
    "phase-space": motif_phase_space,
    "oscillator": motif_oscillator,
    "chain": motif_chain,
    "dispersion": motif_dispersion,
    "chain-to-wave": motif_chain_to_wave,
    "stress": motif_stress,
    "shift-pattern": motif_shift_pattern,
    "lightcone": motif_lightcone,
    "boost": motif_boost,
    "mass-shell": motif_mass_shell,
    "causal-diamond": motif_causal_diamond,
    "vector-field": motif_vector_field,
    "gauge-orbit": motif_gauge_orbit,
    "em-field": motif_em_field,
    "polarization": motif_polarization,
    "commutator": motif_commutator,
    "sphere-axes": motif_sphere_axes,
    "helix": motif_helix,
    "exchange": motif_exchange,
    "timeline": motif_timeline,
    "transition": motif_transition,
    "branching": motif_branching,
    "ramp": motif_ramp,
    "path-bundle": motif_path_bundle,
    "time-slices": motif_time_slices,
    "source-path": motif_source_path,
    "multi-oscillator": motif_multi_oscillator,
    "wavefronts": motif_wavefronts,
    "box-modes": motif_box_modes,
    "occupation": motif_occupation,
    "vacuum": motif_vacuum,
    "propagator": motif_propagator,
    "contour-path": motif_contour_path,
    "source-field": motif_source_field,
    "network": motif_network,
    "pairings": motif_pairings,
    "potential": motif_potential,
    "vertex4": motif_vertex4,
    "potential-family": motif_potential_family,
    "feynman": motif_feynman,
    "momentum-vertex": motif_momentum_vertex,
    "tree-diagram": motif_tree_diagram,
    "loop": motif_loop,
    "scattering": motif_scattering,
    "beam-target": motif_beam_target,
    "amputation": motif_amputation,
    "wave-packets": motif_wave_packets,
    "self-energy": motif_self_energy,
    "vertex-loop": motif_vertex_loop,
    "cutoff-shell": motif_cutoff_shell,
    "counterterm": motif_counterterm,
    "shells": motif_shells,
    "target": motif_target,
    "parallel-flows": motif_parallel_flows,
    "rg-flow": motif_rg_flow,
    "rg-fixed": motif_rg_fixed,
    "saddle-flow": motif_saddle_flow,
    "tree-loop": motif_tree_loop,
    "coarse": motif_coarse,
    "bars-flow": motif_bars_flow,
    "converging-flows": motif_converging_flows,
    "target-band": motif_target_band,
    "ope": motif_ope,
    "manifold": motif_manifold,
    "tangent-manifold": motif_tangent_manifold,
    "multiplet": motif_multiplet,
    "weight-lattice": motif_weight_lattice,
    "phase-field": motif_phase_field,
    "matrix-flow": motif_matrix_flow,
    "fermion-line": motif_fermion_line,
    "lattice-links": motif_lattice_links,
    "photon-line": motif_photon_line,
    "qed-vertex": motif_qed_vertex,
    "gauge-slice": motif_gauge_slice,
    "yang-mills-vertices": motif_yang_mills_vertices,
    "braid": motif_braid,
    "ghost-loop": motif_ghost_loop,
    "mexican-hat": motif_mexican_hat,
    "mexican-contours": motif_mexican_contours,
    "domains": motif_domains,
    "higgs-eating": motif_higgs_eating,
    "blocks": motif_blocks,
    "winding": motif_winding,
    "broken-balance": motif_broken_balance,
    "wilson-loop": motif_wilson_loop,
    "flux-tube": motif_flux_tube,
    "lattice-field": motif_lattice_field,
    "plaquette": motif_plaquette,
    "thermal-circle": motif_thermal_circle,
    "grid-refine": motif_grid_refine,
    "standard-model": motif_standard_model,
    "yukawa": motif_yukawa,
    "curved-grid": motif_curved_grid,
}


AXIS_MOTIFS = {
    "curve",
    "bars",
    "wave",
    "spectrum",
    "wave-envelope",
    "overlap-waves",
    "delta",
    "green",
    "standing-waves",
    "energy",
    "dispersion",
    "mass-shell",
    "timeline",
    "transition",
    "ramp",
    "occupation",
    "vacuum",
    "potential",
    "potential-family",
    "rg-flow",
    "coarse",
    "bars-flow",
    "target-band",
}

GEOMETRY_MOTIFS = {
    "vectors",
    "projection",
    "rotated-grid",
    "ellipse",
    "frame-field",
    "contour",
    "deformed-grid",
    "linear-map",
    "eigen",
    "basis-rays",
    "state-arc",
    "sphere-axes",
    "helix",
    "phase",
    "phasor-sum",
    "curvilinear",
    "constraint",
}

FIELD_MOTIFS = {
    "surface-gradient",
    "flux",
    "curl",
    "field-surface",
    "two-surfaces",
    "stress",
    "vector-field",
    "em-field",
    "polarization",
    "phase-field",
    "source-field",
    "wavefronts",
    "box-modes",
    "multi-oscillator",
    "curved-grid",
}

DIAGRAM_MOTIFS = {
    "feynman",
    "momentum-vertex",
    "tree-diagram",
    "loop",
    "scattering",
    "amputation",
    "self-energy",
    "vertex-loop",
    "vertex4",
    "tree-loop",
    "fermion-line",
    "photon-line",
    "qed-vertex",
    "yang-mills-vertices",
    "ghost-loop",
    "yukawa",
    "higgs-eating",
}

LATTICE_MOTIFS = {
    "lattice-links",
    "lattice-field",
    "plaquette",
    "wilson-loop",
    "thermal-circle",
    "grid-refine",
    "weight-lattice",
}

SYMMETRY_MOTIFS = {
    "gauge-orbit",
    "gauge-slice",
    "manifold",
    "tangent-manifold",
    "multiplet",
    "matrix-flow",
    "standard-model",
    "mexican-hat",
    "mexican-contours",
    "domains",
    "winding",
    "broken-balance",
    "flux-tube",
}


MOTIF_MARKERS: dict[str, list[str]] = {
    "curve": ["axis", "tangent", "local patch"],
    "bars": ["bins", "sum", "limit curve"],
    "boundary": ["region", "boundary", "flux"],
    "nested": ["inner scale", "outer scale", "approximation"],
    "flow": ["input", "map", "output"],
    "stencil": ["center value", "neighbors", "local rule"],
    "vectors": ["vector", "components", "basis"],
    "projection": ["vector", "projection", "basis direction"],
    "rotated-grid": ["same vector", "old axes", "new axes"],
    "ellipse": ["metric", "equal length", "vector"],
    "frame-field": ["point", "local frame", "field"],
    "contour": ["level set", "invariant", "coordinates"],
    "surface-gradient": ["position", "gradient", "steepest rise"],
    "flux": ["surface", "flow lines", "outward flux"],
    "curl": ["local loop", "circulation", "rotation"],
    "deformed-grid": ["old cell", "new cell", "Jacobian"],
    "field-surface": ["position x", "field value", "configuration"],
    "phase": ["phase angle", "amplitude", "rotation"],
    "wave": ["time", "amplitude", "phase"],
    "phasor-sum": ["amplitude A", "amplitude B", "result"],
    "spectrum": ["mode label", "weight", "peak"],
    "wave-envelope": ["carrier", "envelope", "normalization"],
    "linear-map": ["input cell", "matrix action", "output cell"],
    "matrix": ["row", "pivot", "eliminated part"],
    "eigen": ["eigenline", "input vector", "scaled vector"],
    "basis-rays": ["basis ray", "coefficient", "state"],
    "ladder": ["lower level", "raising step", "upper level"],
    "overlap-waves": ["state one", "state two", "overlap"],
    "state-arc": ["initial state", "unitary path", "final state"],
    "fourier-stack": ["mode", "superposition", "signal"],
    "delta": ["width", "height", "fixed area"],
    "green": ["source", "response", "propagation"],
    "standing-waves": ["boundary", "node", "allowed mode"],
    "paths": ["initial point", "varied path", "final point"],
    "action-valley": ["trial history", "stationary path", "action"],
    "paths-fixed": ["fixed endpoint", "variation", "fixed endpoint"],
    "balance": ["left term", "balance point", "right term"],
    "two-surfaces": ["field", "variation", "nearby field"],
    "curvilinear": ["coordinate line", "path", "adapted axes"],
    "constraint": ["constraint surface", "allowed path", "reduced space"],
    "energy": ["kinetic part", "potential part", "total"],
    "phase-space": ["coordinate q", "momentum p", "flow"],
    "oscillator": ["potential", "state", "orbit"],
    "chain": ["site", "spring link", "normal motion"],
    "dispersion": ["wave number", "frequency", "mass gap"],
    "chain-to-wave": ["discrete sites", "continuum field", "limit"],
    "stress": ["cell", "energy flow", "momentum flow"],
    "shift-pattern": ["before shift", "translation", "after shift"],
    "lightcone": ["space", "time", "causal cone"],
    "boost": ["old axes", "boosted axes", "same interval"],
    "mass-shell": ["momentum", "energy", "mass shell"],
    "causal-diamond": ["past", "event", "future"],
    "vector-field": ["potential contours", "field arrows", "derivative"],
    "gauge-orbit": ["gauge orbit", "same physics", "representative"],
    "em-field": ["electric part", "magnetic part", "wave direction"],
    "polarization": ["propagation", "transverse field", "polarization"],
    "commutator": ["order AB", "order BA", "mismatch"],
    "sphere-axes": ["rotation axis", "state vector", "measurement axis"],
    "helix": ["first turn", "second turn", "spinor phase"],
    "exchange": ["particle one", "exchange", "particle two"],
    "timeline": ["early time", "insertion", "late time"],
    "transition": ["initial level", "transition", "final level"],
    "branching": ["input state", "alternatives", "outputs"],
    "ramp": ["free theory", "turn on", "interaction"],
    "path-bundle": ["classical path", "fluctuations", "sum over histories"],
    "time-slices": ["time slice", "path value", "product limit"],
    "source-path": ["source insertion", "path", "weighted history"],
    "multi-oscillator": ["oscillator", "mode", "coupling"],
    "wavefronts": ["wavefront", "momentum", "phase"],
    "box-modes": ["box", "boundary", "mode"],
    "occupation": ["mode", "occupation", "particle count"],
    "vacuum": ["mean field", "fluctuation", "zero point"],
    "propagator": ["source point", "propagator", "observation point"],
    "contour-path": ["pole", "contour", "deformation"],
    "source-field": ["source", "field response", "measured point"],
    "network": ["node", "dependency", "synthesis"],
    "pairings": ["operator", "contraction", "pairing"],
    "potential": ["field value", "potential", "minimum"],
    "vertex4": ["external leg", "vertex", "coupling"],
    "potential-family": ["bare curve", "renormalized curve", "condition"],
    "feynman": ["incoming line", "internal line", "outgoing line"],
    "momentum-vertex": ["incoming momentum", "vertex", "outgoing momentum"],
    "tree-diagram": ["incoming", "propagator", "outgoing"],
    "loop": ["external line", "loop momentum", "internal line"],
    "scattering": ["incoming beam", "interaction", "outgoing particles"],
    "beam-target": ["beam", "target", "scattered states"],
    "amputation": ["external leg", "amputated core", "external leg"],
    "wave-packets": ["incoming packet", "overlap region", "outgoing packet"],
    "self-energy": ["external line", "self energy", "corrected line"],
    "vertex-loop": ["bare vertex", "loop correction", "renormalized vertex"],
    "cutoff-shell": ["low modes", "cutoff shell", "discarded modes"],
    "counterterm": ["bare term", "counterterm", "finite result"],
    "shells": ["IR modes", "momentum shell", "UV cutoff"],
    "target": ["target value", "tolerance", "matching scale"],
    "parallel-flows": ["full theory", "matching", "effective theory"],
    "rg-flow": ["scale", "running coupling", "trajectory"],
    "rg-fixed": ["flow arrows", "fixed point", "relevant direction"],
    "saddle-flow": ["steepest path", "saddle", "fluctuation"],
    "tree-loop": ["tree level", "loop level", "correction"],
    "coarse": ["short detail", "coarse field", "long scale"],
    "bars-flow": ["operator", "coefficient", "RG flow"],
    "converging-flows": ["microscopic input", "coarse graining", "universal output"],
    "target-band": ["low scale", "EFT window", "high scale"],
    "ope": ["nearby insertions", "local operator", "coefficient"],
    "manifold": ["group element", "orbit", "tangent direction"],
    "tangent-manifold": ["identity", "generator", "group motion"],
    "multiplet": ["component", "multiplet", "symmetry action"],
    "weight-lattice": ["weight", "charge axis", "multiplet"],
    "phase-field": ["point", "local phase", "connection need"],
    "matrix-flow": ["spinor component", "gamma action", "mixed component"],
    "fermion-line": ["fermion flow", "arrow", "spinor factor"],
    "lattice-links": ["site", "link variable", "parallel transport"],
    "photon-line": ["current", "photon line", "current"],
    "qed-vertex": ["fermion in", "photon", "fermion out"],
    "gauge-slice": ["gauge orbit", "slice", "representative"],
    "yang-mills-vertices": ["three gluon", "self coupling", "four gluon"],
    "braid": ["color label", "ordering", "non Abelian flow"],
    "ghost-loop": ["ghost line", "loop", "gauge fixing"],
    "mexican-hat": ["vacuum circle", "chosen vacuum", "radial mode"],
    "mexican-contours": ["Goldstone direction", "radial direction", "vacuum"],
    "domains": ["domain", "wall", "vacuum choice"],
    "higgs-eating": ["Goldstone mode", "gauge field", "massive vector"],
    "blocks": ["before breaking", "rearrangement", "after breaking"],
    "winding": ["sector Q", "winding", "separate class"],
    "broken-balance": ["classical symmetry", "measure", "anomaly"],
    "wilson-loop": ["closed loop", "enclosed flux", "area"],
    "flux-tube": ["charge", "flux tube", "anticharge"],
    "lattice-field": ["site value", "lattice spacing", "field"],
    "plaquette": ["link", "plaquette", "curvature"],
    "thermal-circle": ["space", "Euclidean time", "period beta"],
    "grid-refine": ["coarse lattice", "finer lattice", "continuum limit"],
    "standard-model": ["SU3 sector", "SU2 sector", "U1 sector"],
    "yukawa": ["fermion", "scalar", "mass term"],
    "curved-grid": ["curved background", "local field", "geometry"],
}


def compact_label(text: str, limit: int = 28) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    words = cleaned.split()
    result: list[str] = []
    for word in words:
        candidate = " ".join(result + [word])
        if len(candidate) > limit:
            break
        result.append(word)
    return " ".join(result) if result else cleaned[:limit].rstrip()


def in_figure_labels(spec: FigureSpec) -> list[str]:
    concept = compact_label(spec.concept, 30)
    motif = spec.motif
    if motif in MOTIF_MARKERS:
        labels = [concept, *MOTIF_MARKERS[motif]]
    elif motif in AXIS_MOTIFS:
        labels = [concept, "input scale", "output value", "key feature"]
    elif motif in GEOMETRY_MOTIFS:
        labels = [concept, "object", "components", "basis/frame"]
    elif motif in FIELD_MOTIFS:
        labels = [concept, "position x", "field value", "local change"]
    elif motif in DIAGRAM_MOTIFS:
        labels = [concept, "incoming", "vertex", "outgoing"]
    elif motif in LATTICE_MOTIFS:
        labels = [concept, "site", "link", "loop/cell"]
    elif motif in SYMMETRY_MOTIFS:
        labels = [concept, "orbit", "chosen point", "generator"]
    elif motif in {"boundary", "nested", "target", "cutoff-shell", "shells", "ope"}:
        labels = [concept, "inner region", "boundary", "outer scale"]
    elif motif in {"flow", "parallel-flows", "converging-flows", "branching"}:
        labels = [concept, "input", "map/flow", "output"]
    elif motif in {"network", "blocks", "matrix"}:
        labels = [concept, "node/block", "relation", "grouping"]
    elif motif in {"paths", "paths-fixed", "path-bundle", "time-slices", "source-path", "exchange", "contour-path"}:
        labels = [concept, "start", "history", "endpoint"]
    elif motif in {"balance", "commutator"}:
        labels = [concept, "operation A", "operation B", "mismatch"]
    elif motif in {"lightcone", "boost", "causal-diamond"}:
        labels = [concept, "space", "time", "causal region"]
    else:
        labels = [concept, "input", "structure", "output"]

    unique: list[str] = []
    for label in labels:
        label = compact_label(label, 30)
        if label and label not in unique:
            unique.append(label)
    return unique[:4]


def tikz_label_document(spec: FigureSpec, labels: list[str]) -> str:
    image_name = label_escape(spec.background_abs.name)
    escaped = [label_escape(label) for label in labels]
    while len(escaped) < 4:
        escaped.append(f"marker {len(escaped) + 1}")
    return rf"""\documentclass[tikz,border=2pt]{{standalone}}
\usepackage{{graphicx}}
\usepackage{{tikz}}
\usetikzlibrary{{arrows.meta}}
\begin{{document}}
\begin{{tikzpicture}}
  \node[anchor=south west, inner sep=0] (img) at (0,0) {{\includegraphics[width=12cm]{{{image_name}}}}};
  \begin{{scope}}[
    x={{(img.south east)}},
    y={{(img.north west)}},
    labelbox/.style={{font=\sffamily\small, fill=white, fill opacity=0.88, text opacity=1, rounded corners=1.5pt, inner xsep=3pt, inner ysep=2pt, draw=black!20}},
    callout/.style={{-{{Latex[length=2.2mm]}}, line width=0.7pt, black!70}},
  ]
    \node[labelbox, anchor=north west] at (0.035,0.965) {{{escaped[0]}}};
    \draw[callout] (0.16,0.18) -- (0.33,0.18) node[midway, above, labelbox] {{{escaped[1]}}};
    \draw[callout] (0.74,0.78) -- (0.55,0.58) node[pos=0, above, labelbox] {{{escaped[2]}}};
    \node[labelbox, anchor=south east] at (0.965,0.055) {{{escaped[3]}}};
  \end{{scope}}
\end{{tikzpicture}}
\end{{document}}
"""


def compile_latex_figure(spec: FigureSpec) -> None:
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", spec.latex_abs.name],
        cwd=spec.latex_abs.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-40:])
        raise RuntimeError(f"pdflatex failed for {spec.latex_rel}:\n{tail}")
    for suffix in [".aux", ".log"]:
        path = spec.latex_abs.with_suffix(suffix)
        if path.exists():
            path.unlink()


def render_figure(spec: FigureSpec) -> None:
    spec.image_abs.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=160)
    rng = setup_ax(ax, seed_for(spec.figure_id))
    MOTIFS.get(spec.motif, motif_network)(ax, rng)
    ax.set_aspect("equal", adjustable="box")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    fig.savefig(spec.background_abs, facecolor="#fbfaf7")
    plt.close(fig)
    labels = in_figure_labels(spec)
    spec.latex_abs.write_text(tikz_label_document(spec, labels), encoding="utf-8")
    compile_latex_figure(spec)


def figure_block(spec: FigureSpec) -> str:
    caption = tex_escape(spec.caption)
    return (
        f"\n% QFTFIGURE-BEGIN {spec.figure_id}\n"
        f"\\qftfigure{{{spec.image_rel}}}{{{caption}}}{{{spec.label}}}\n"
        f"% QFTFIGURE-END {spec.figure_id}\n"
    )


def insert_specs(path: Path, specs: list[FigureSpec]) -> None:
    text = path.read_text(encoding="utf-8")
    text = BEGIN_RE.sub("\n", text)
    lines = text.splitlines()
    section_indices = [i for i, line in enumerate(lines) if line.startswith(r"\section{")]
    if not section_indices:
        section_indices = [i for i, line in enumerate(lines) if line.startswith(r"\chapter{")]
    if not section_indices:
        raise RuntimeError(f"No insertion point found in {path}")

    inserts: dict[int, list[str]] = {}
    for idx, spec in enumerate(specs):
        line_index = section_indices[min(idx, len(section_indices) - 1)]
        inserts.setdefault(line_index, []).append(figure_block(spec))

    output: list[str] = []
    for i, line in enumerate(lines):
        output.append(line)
        if i in inserts:
            output.extend(inserts[i])
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def build_manifest(specs: list[FigureSpec]) -> dict[str, object]:
    entries = []
    for spec in specs:
        labels = in_figure_labels(spec)
        entries.append(
            {
                "id": spec.figure_id,
                "image_path": spec.image_rel,
                "background_image_path": spec.background_rel,
                "latex_source_path": spec.latex_rel,
                "tex_file": str(spec.file),
                "chapter_title": spec.title,
                "chapter_number": spec.chapter_number,
                "concept": spec.concept,
                "caption": spec.caption,
                "generator": "latex-tikz-labelled",
                "generation_priority": "latex-first",
                "image2_status": "not-used-latex-native-preferred",
                "in_figure_labels": labels,
                "prompt_summary": (
                    "LaTeX/TikZ labelled textbook figure for "
                    f"{spec.title}: {spec.concept}; markers: {', '.join(labels)}."
                ),
                "inspected": "programmatic LaTeX generation; final spot review still required",
            }
        )
    return {
        "goal_file": "2026-06-20-qft-textbook-figures-goal.md",
        "note": (
            "These figures are generated locally as original LaTeX/TikZ labelled textbook assets. "
            "The source-native PDF is the manuscript asset; the PNG background is an intermediate "
            "original shape layer, and TikZ supplies concise in-figure labels or markers. "
            "Use image2 only when a LaTeX-native labelled figure is not pedagogically effective."
        ),
        "total_entries": len(entries),
        "entries": entries,
    }


def main() -> None:
    specs: list[FigureSpec] = []
    for path in chapter_files() + review_files():
        file_specs = specs_for_file(path)
        specs.extend(file_specs)
        for spec in file_specs:
            render_figure(spec)
        insert_specs(path, file_specs)
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(build_manifest(specs), indent=2), encoding="utf-8")
    print(json.dumps({"generated_or_updated": len(specs), "manifest": str(MANIFEST.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
