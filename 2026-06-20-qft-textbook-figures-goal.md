# Goal: Add Reader-Friendly Figures To The QFT Textbook

## Goal Mode Objective

Follow the saved goal file at `/home/czc/projects/working/qft_from_caculus/2026-06-20-qft-textbook-figures-goal.md`; complete the task only when the verification section passes, and stop to ask if any listed stop condition occurs.

## Full Prompt

### Objective

Add a large, reader-friendly illustration program to the LaTeX textbook project `Quantum Field Theory from Calculus`, prioritizing LaTeX-native figures first, so that the full manuscript becomes substantially easier to learn from visually while still compiling cleanly as `main.pdf`. Use image2/AI-generated bitmap figures only when a LaTeX/TikZ/PGFPlots figure is not pedagogically clear, visually effective, or practical for the concept.

Completion means the current 56-chapter full textbook has at least 240 newly added instructional figures beyond the existing cover image, with broad coverage across the book and no chapter left visually unsupported.

### Context

The working directory is:

`/home/czc/projects/working/qft_from_caculus`

The project is an English LaTeX book with:

- `main.tex`
- `qftcalc.sty`
- `frontmatter/`
- `chaptersfull/`
- `appendicesfull/`
- `figures/`
- `references.bib`
- an existing compiled `main.pdf`

`main.tex` includes 56 full chapters from `chaptersfull/`, 8 part review files, and appendices. The current project appears to contain only the cover bitmap as a real figure asset. The task is to add a serious textbook-scale figure layer.

The user specifically wants as many useful figures as practical for reader friendliness and now prefers LaTeX-native generation first. Use TikZ, PGFPlots, source-native LaTeX drawing, or generated source-controlled vector/raster assets where they can produce clear mathematical diagrams, labels, plots, commutative structures, Feynman-style diagrams, coordinate sketches, or compile-stable graphics. Use image2/AI-generated bitmap figures as a second option when the LaTeX-native result is too weak, too cluttered, or cannot convey the physical intuition well enough.

### Scope

Codex may modify:

- `main.tex` if needed for package setup
- `qftcalc.sty` for figure macros, caption styling, TikZ/PGFPlots support, or graphics helpers
- files under `chaptersfull/`
- files under `appendicesfull/` if appendix figures are useful
- files under `figures/`, including new subdirectories
- helper scripts under `scripts/` for auditing figure counts, image manifests, prompt records, or build checks

Codex should create and insert at least 240 new figures. Prefer LaTeX/TikZ/PGFPlots/source-native figures for diagrams, axes, graph topology, mathematical structure, coordinate sketches, labels, arrows, exact symbolic notation, Feynman-style diagrams, and compile-stable vector graphics. Use image2/AI-generated bitmap assets only after the LaTeX-native approach is judged inadequate for a conceptual, visual, physical, geometric, or pedagogical illustration.

Figures must not be bare pictures with no internal guidance. Every generated figure should include concise in-figure text markers that help the reader decode it, such as axis labels, coordinate names, scale annotations, arrows with labels, region labels, input/output labels, or short concept labels. Prefer exact LaTeX/TikZ text for mathematical notation and labels. For image2 figures, request only short, plain, easy-to-render labels and verify their legibility; if image2 text is wrong or illegible, replace the figure with a LaTeX-native version or overlay the labels in LaTeX rather than leaving the figure unlabelled.

The figure program should prioritize reader comprehension, not decoration. Good figure types include:

- geometric intuition for calculus, vectors, gradients, divergence, curl, and coordinate transformations
- oscillation, Fourier decomposition, wave packets, distributions, and Green functions
- variational paths, stationary action, phase-space flow, coupled oscillators, and continuum limits
- fields over space, field configurations, potentials, boundary conditions, and normal modes
- spacetime diagrams, light cones, tensor index structure, and electromagnetic potentials
- Hilbert-space geometry, operators, commutators, spectra, spin, and identical-particle symmetry
- path-integral intuition, time slicing, fluctuation families, Euclidean continuation, and saddle points
- free-field oscillator modes, Fock space ladders, propagators, causal support, and particle interpretation
- Wick contractions, Feynman rules, scattering kinematics, phase space, loops, self-energy, and vertex corrections
- cutoff surfaces, dimensional regularization intuition, counterterms, running couplings, RG flow, and Wilsonian coarse graining
- group manifolds, Lie algebra generators, representations, symmetry actions, Noether currents, gauge redundancy, fiber-bundle intuition where appropriate
- Abelian and non-Abelian gauge fields, gauge fixing, Ward identities, Yang-Mills self-interactions, ghosts, and BRST structure
- spontaneous symmetry breaking, Mexican-hat potentials, Goldstone modes, Higgs mechanism, anomalies, instantons, lattice fields, Wilson loops, confinement, finite-temperature circles, curved spacetime, and Standard Model structure

Minimum coverage requirements:

- Add at least 240 new figures total, excluding `figures/cover-image2.png`.
- Every one of the 56 chapter files in `chaptersfull/` must receive at least 3 newly inserted instructional figures.
- At least 20 especially abstract or visually important chapters must receive at least 5 newly inserted instructional figures.
- Each of the 8 part review files should receive at least 1 visual synthesis figure if doing so improves review value.
- Figure captions must be substantive enough to teach: each caption should explain what the reader should notice, not merely name the picture.
- Each figure must be placed near the relevant explanation, derivation, example, or concept it supports.
- AI-generated bitmap figures must be saved under an organized `figures/` subdirectory and inserted with stable relative paths.
- Maintain a manifest or audit file listing every newly generated bitmap image, its intended concept, the chapter where it is used, and the prompt or short prompt summary used to create it.
- All generated figures should include meaningful visual labels or markers inside the figure, not only in the caption. Good markers include axis labels, coordinate labels, arrows named by their meaning, highlighted regions with short labels, or symbolic labels rendered by LaTeX/TikZ. When an AI image contains text, equations, axes, or labels, verify that the text is legible and correct. If image text is unreliable, add labels through LaTeX/TikZ overlays or replace the image with a source-native figure.
- Prefer consistent visual style across generated figures: serious textbook illustration, clean scientific composition, uncluttered backgrounds, high contrast, readable shapes, and no decorative filler.

### Out Of Scope

Do not rewrite the textbook prose except where small local edits are needed to introduce or reference a new figure.

Do not pad the book with irrelevant images. A figure only counts toward completion if it directly supports a nearby concept in the manuscript.

Do not use copyrighted textbook figures, web images, or unlicensed third-party diagrams. New bitmap figures should be generated or otherwise original; source-native diagrams should be original.

Do not make the book visually childish, promotional, or popular-science-like. The tone should remain serious, patient, and textbook-like.

Do not rely on AI-generated text inside images for mathematical notation. Use LaTeX captions, overlays, or TikZ labels for exact symbolic content.

Do not mark the goal complete merely because many images were generated. The images must be inserted into the manuscript, compile successfully, and satisfy the coverage and usefulness criteria.

### Verification

Before marking the goal complete, run or create equivalent checks proving all of the following:

1. The LaTeX project compiles successfully to `main.pdf`.

   Preferred command:

   ```bash
   latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
   ```

   If `latexmk` is unavailable, use the repository's existing successful build method and document the command.

2. The project contains at least 240 newly added instructional figures beyond the existing cover image.

   Provide an audit count based on source references and/or the generated manifest. The count must exclude `figures/cover-image2.png`.

3. Every chapter file under `chaptersfull/ch*.tex` has at least 3 newly inserted figures.

4. At least 20 chapter files under `chaptersfull/ch*.tex` have at least 5 newly inserted figures.

5. Each figure asset referenced by `\includegraphics` exists on disk and is readable.

6. Captions are present and pedagogically meaningful for all inserted figures.

7. The generated image manifest or audit file exists and lists, for each AI-generated bitmap:

   - image path
   - chapter or file where used
   - concept being illustrated
   - prompt or prompt summary
   - whether it was inspected or otherwise checked for obvious quality problems

8. Perform a final spot review of at least 25 generated figures across early, middle, and late chapters. The review should check that images are not blank, not obviously corrupted, not visually irrelevant, and include useful in-figure labels or markers. For image2 outputs, also check that any embedded text is correct and legible.

9. Summarize the verification results in the final response, including:

   - total new figure count
   - minimum figures per chapter
   - number of chapters with at least 5 figures
   - compile command and result
   - manifest/audit file path
   - any remaining image-quality risks

### Stop Conditions

Stop and ask the user before continuing if any of these occur:

- LaTeX-native generation cannot produce reader-friendly results for a large class of required figures, and image2 is unavailable or not authorized as the fallback
- generating image2 bitmap figures would require external payment, credentials, or a service the user has not authorized
- the manuscript structure changes so much that the 56-chapter coverage rule no longer matches `main.tex`
- LaTeX compilation fails for reasons unrelated to the figure work and cannot be fixed with small local changes
- a requested figure would require copying a copyrighted diagram or reproducing a specific third-party textbook image
- there is a tradeoff between adding many approximate images and fewer precise, well-labelled LaTeX/TikZ diagrams that materially affects pedagogical quality
- the work would require changing the textbook's language, title, core organization, or mathematical claims beyond small figure-related edits

## Notes

- Created for Codex Goal mode.
- Do not mark complete until the verification section passes or the user explicitly changes the completion standard.
