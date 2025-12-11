"""
Comprehensive Multiomics Visualization
======================================

This module provides mathematical visualizations for multiomics datasets including:
- Genomics: DNA structure, sequences, genetic variations
- Epigenomics: DNA methylation, histone modifications
- Transcriptomics: RNA expression, gene expression matrices
- Proteomics: Protein structures, protein-protein interactions
- Metabolomics: Metabolic pathways, small molecules

Run with: manimgl multiomics_visualization.py <SceneName>
Example: manimgl multiomics_visualization.py MultiomicsOverview
"""

from manimlib import *
import numpy as np

# Custom color palette for omics layers
GENOMICS_COLOR = "#4A90D9"      # Blue
EPIGENOMICS_COLOR = "#9B59B6"   # Purple
TRANSCRIPTOMICS_COLOR = "#E74C3C"  # Red
PROTEOMICS_COLOR = "#27AE60"    # Green
METABOLOMICS_COLOR = "#F39C12"  # Orange

# DNA base colors
ADENINE_COLOR = "#E74C3C"   # Red
THYMINE_COLOR = "#3498DB"   # Blue
GUANINE_COLOR = "#2ECC71"   # Green
CYTOSINE_COLOR = "#F1C40F"  # Yellow
URACIL_COLOR = "#9B59B6"    # Purple


class DNAHelix(VGroup):
    """A 3D-like DNA double helix structure."""

    def __init__(
        self,
        length=6,
        num_turns=2,
        radius=0.5,
        height=4,
        num_points=100,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.length = length
        self.num_turns = num_turns
        self.radius = radius
        self.height = height
        self.num_points = num_points

        self._create_helix()

    def _create_helix(self):
        # Create the two backbone strands
        t_values = np.linspace(0, self.num_turns * TAU, self.num_points)

        # First strand (leading)
        strand1_points = []
        strand2_points = []

        for i, t in enumerate(t_values):
            y = (t / (self.num_turns * TAU)) * self.height - self.height / 2
            # Strand 1
            x1 = self.radius * np.cos(t)
            z1 = self.radius * np.sin(t) * 0.3  # Flatten for 2D appearance
            strand1_points.append([x1, y, 0])

            # Strand 2 (opposite phase)
            x2 = self.radius * np.cos(t + PI)
            z2 = self.radius * np.sin(t + PI) * 0.3
            strand2_points.append([x2, y, 0])

        strand1 = VMobject()
        strand1.set_points_smoothly([np.array(p) for p in strand1_points])
        strand1.set_stroke(GENOMICS_COLOR, width=4)

        strand2 = VMobject()
        strand2.set_points_smoothly([np.array(p) for p in strand2_points])
        strand2.set_stroke(GENOMICS_COLOR, width=4)

        self.add(strand1, strand2)

        # Add base pairs (rungs)
        bases = ["A", "T", "G", "C"]
        base_colors = {
            "A": ADENINE_COLOR, "T": THYMINE_COLOR,
            "G": GUANINE_COLOR, "C": CYTOSINE_COLOR
        }
        complements = {"A": "T", "T": "A", "G": "C", "C": "G"}

        num_base_pairs = int(self.num_turns * 10)
        base_indices = np.linspace(0, len(t_values) - 1, num_base_pairs).astype(int)

        for idx in base_indices:
            t = t_values[idx]
            y = (t / (self.num_turns * TAU)) * self.height - self.height / 2

            x1 = self.radius * np.cos(t)
            x2 = self.radius * np.cos(t + PI)

            # Create base pair line
            base_pair = Line(
                np.array([x1, y, 0]),
                np.array([x2, y, 0]),
                stroke_width=2,
                color=WHITE
            )

            # Add base labels
            base1 = np.random.choice(bases)
            base2 = complements[base1]

            label1 = Text(base1, font_size=14)
            label1.set_color(base_colors[base1])
            label1.move_to(np.array([x1 * 0.6, y, 0]))

            label2 = Text(base2, font_size=14)
            label2.set_color(base_colors[base2])
            label2.move_to(np.array([x2 * 0.6, y, 0]))

            self.add(base_pair, label1, label2)


class HistoneOctamer(VGroup):
    """Visualization of histone octamer with DNA wrapped around."""

    def __init__(self, radius=0.8, **kwargs):
        super().__init__(**kwargs)

        # Core histone (octamer represented as a circle)
        core = Circle(radius=radius)
        core.set_fill(EPIGENOMICS_COLOR, opacity=0.6)
        core.set_stroke(EPIGENOMICS_COLOR, width=2)

        # DNA wrapping around
        theta_range = np.linspace(-PI * 0.8, PI * 0.8, 50)
        dna_radius = radius + 0.15

        dna_points = []
        for theta in theta_range:
            x = dna_radius * np.cos(theta)
            y = dna_radius * np.sin(theta)
            dna_points.append([x, y, 0])

        dna_wrap = VMobject()
        dna_wrap.set_points_smoothly([np.array(p) for p in dna_points])
        dna_wrap.set_stroke(GENOMICS_COLOR, width=4)

        # Histone tails
        tail_positions = [UP, DOWN, LEFT, RIGHT]
        tails = VGroup()
        for pos in tail_positions:
            tail_start = core.get_center() + pos * radius
            tail_end = tail_start + pos * 0.5
            tail = Line(tail_start, tail_end, stroke_width=3)
            tail.set_color(EPIGENOMICS_COLOR)
            tails.add(tail)

        # Labels
        h_label = Text("H3/H4", font_size=16)
        h_label.move_to(core.get_center())
        h_label.set_color(WHITE)

        self.add(core, dna_wrap, tails, h_label)
        self.core = core
        self.tails = tails


class MethylationMark(VGroup):
    """Visualization of DNA methylation mark (methyl group on cytosine)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Cytosine base
        base = Circle(radius=0.2)
        base.set_fill(CYTOSINE_COLOR, opacity=0.8)
        base.set_stroke(WHITE, width=1)

        # Methyl group (CH3)
        methyl = Circle(radius=0.12)
        methyl.set_fill(EPIGENOMICS_COLOR, opacity=1)
        methyl.set_stroke(WHITE, width=1)
        methyl.next_to(base, UP, buff=0.05)

        # Label
        label = Text("Me", font_size=10)
        label.move_to(methyl.get_center())
        label.set_color(WHITE)

        self.add(base, methyl, label)


class GeneExpressionHeatmap(VGroup):
    """A gene expression heatmap visualization."""

    def __init__(
        self,
        n_genes=10,
        n_samples=6,
        cell_size=0.4,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.n_genes = n_genes
        self.n_samples = n_samples
        self.cell_size = cell_size

        # Generate random expression data
        np.random.seed(42)
        self.data = np.random.randn(n_genes, n_samples)

        self._create_heatmap()

    def _create_heatmap(self):
        # Normalize data for coloring
        data_norm = (self.data - self.data.min()) / (self.data.max() - self.data.min())

        cells = VGroup()
        for i in range(self.n_genes):
            for j in range(self.n_samples):
                cell = Square(side_length=self.cell_size)
                cell.move_to([
                    j * self.cell_size - (self.n_samples - 1) * self.cell_size / 2,
                    -i * self.cell_size + (self.n_genes - 1) * self.cell_size / 2,
                    0
                ])

                # Color based on expression level (blue-white-red)
                val = data_norm[i, j]
                if val < 0.5:
                    color = interpolate_color(BLUE, WHITE, val * 2)
                else:
                    color = interpolate_color(WHITE, RED, (val - 0.5) * 2)

                cell.set_fill(color, opacity=0.9)
                cell.set_stroke(GREY, width=0.5)
                cells.add(cell)

        self.add(cells)

        # Add gene labels
        gene_labels = VGroup()
        for i in range(self.n_genes):
            label = Text(f"Gene{i+1}", font_size=12)
            label.next_to(cells[i * self.n_samples], LEFT, buff=0.1)
            gene_labels.add(label)

        self.add(gene_labels)

        # Add sample labels
        sample_labels = VGroup()
        for j in range(self.n_samples):
            label = Text(f"S{j+1}", font_size=12)
            label.next_to(cells[j], UP, buff=0.1)
            sample_labels.add(label)

        self.add(sample_labels)

        self.cells = cells


class RNAMolecule(VGroup):
    """Visualization of an RNA molecule (single strand with secondary structure)."""

    def __init__(self, length=20, **kwargs):
        super().__init__(**kwargs)

        # Create a wavy single strand
        points = []
        for i in range(length):
            x = i * 0.3 - (length - 1) * 0.15
            y = 0.3 * np.sin(i * 0.5)
            points.append([x, y, 0])

        strand = VMobject()
        strand.set_points_smoothly([np.array(p) for p in points])
        strand.set_stroke(TRANSCRIPTOMICS_COLOR, width=4)

        # Add base markers
        bases = ["A", "U", "G", "C"]
        base_colors = {
            "A": ADENINE_COLOR, "U": URACIL_COLOR,
            "G": GUANINE_COLOR, "C": CYTOSINE_COLOR
        }

        base_markers = VGroup()
        for i in range(0, length, 3):
            if i < len(points):
                base = np.random.choice(bases)
                marker = Dot(radius=0.08, color=base_colors[base])
                marker.move_to(points[i])
                base_markers.add(marker)

        self.add(strand, base_markers)

        # Add 5' and 3' labels
        label_5 = Text("5'", font_size=14)
        label_5.next_to(strand, LEFT, buff=0.1)
        label_5.set_color(TRANSCRIPTOMICS_COLOR)

        label_3 = Text("3'", font_size=14)
        label_3.next_to(strand, RIGHT, buff=0.1)
        label_3.set_color(TRANSCRIPTOMICS_COLOR)

        self.add(label_5, label_3)


class ProteinStructure(VGroup):
    """Visualization of protein secondary structure (alpha helix and beta sheet)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Alpha helix (spiral)
        helix_points = []
        for t in np.linspace(0, 3 * TAU, 60):
            x = 0.3 * np.cos(t)
            y = t / (3 * TAU) * 2 - 1
            helix_points.append([x - 1.5, y, 0])

        helix = VMobject()
        helix.set_points_smoothly([np.array(p) for p in helix_points])
        helix.set_stroke(PROTEOMICS_COLOR, width=6)

        helix_label = Text("α-helix", font_size=14)
        helix_label.next_to(helix, DOWN, buff=0.2)
        helix_label.set_color(PROTEOMICS_COLOR)

        # Beta sheet (zigzag arrows)
        beta_sheet = VGroup()
        for i in range(3):
            arrow_points = []
            x_offset = 1.2 + i * 0.5
            direction = 1 if i % 2 == 0 else -1

            for j in range(6):
                x = x_offset + 0.15 * (j % 2) * direction
                y = j * 0.4 - 1
                arrow_points.append([x, y, 0])

            strand = VMobject()
            strand.set_points_smoothly([np.array(p) for p in arrow_points])
            strand.set_stroke(PROTEOMICS_COLOR, width=4)

            # Arrow head at the end
            arrow = Arrow(
                start=arrow_points[-2],
                end=arrow_points[-1],
                buff=0,
                stroke_width=4
            )
            arrow.set_color(PROTEOMICS_COLOR)

            beta_sheet.add(strand)

        beta_label = Text("β-sheet", font_size=14)
        beta_label.next_to(beta_sheet, DOWN, buff=0.2)
        beta_label.set_color(PROTEOMICS_COLOR)

        # Hydrogen bonds between beta strands
        h_bonds = VGroup()
        for i in range(5):
            y = i * 0.4 - 0.8
            bond = DashedLine(
                np.array([1.35, y, 0]),
                np.array([1.55, y, 0]),
                dash_length=0.05
            )
            bond.set_stroke(GREY, width=1)
            h_bonds.add(bond)

        self.add(helix, helix_label, beta_sheet, beta_label, h_bonds)


class ProteinInteractionNetwork(VGroup):
    """Visualization of protein-protein interaction network."""

    def __init__(self, n_proteins=8, **kwargs):
        super().__init__(**kwargs)

        self.n_proteins = n_proteins

        # Create protein nodes in a circular layout
        angles = np.linspace(0, TAU, n_proteins, endpoint=False)
        radius = 2

        proteins = VGroup()
        positions = []

        for i, angle in enumerate(angles):
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            positions.append(np.array([x, y, 0]))

            protein = Circle(radius=0.3)
            protein.set_fill(PROTEOMICS_COLOR, opacity=0.7)
            protein.set_stroke(WHITE, width=2)
            protein.move_to([x, y, 0])

            label = Text(f"P{i+1}", font_size=14)
            label.move_to(protein.get_center())
            label.set_color(WHITE)

            proteins.add(VGroup(protein, label))

        self.add(proteins)

        # Create interaction edges (random connections)
        np.random.seed(123)
        edges = VGroup()
        for i in range(n_proteins):
            for j in range(i + 1, n_proteins):
                if np.random.random() > 0.5:
                    edge = Line(
                        positions[i],
                        positions[j],
                        stroke_width=2
                    )
                    edge.set_color(interpolate_color(WHITE, PROTEOMICS_COLOR, 0.5))
                    edges.add(edge)

        # Add edges behind proteins
        self.add_to_back(edges)

        self.proteins = proteins
        self.edges = edges


class MetabolicPathway(VGroup):
    """Visualization of a metabolic pathway."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Define metabolites and enzymes
        metabolites = ["Glucose", "G6P", "F6P", "FBP", "Pyruvate"]

        compounds = VGroup()
        arrows = VGroup()
        enzymes = VGroup()

        x_positions = np.linspace(-4, 4, len(metabolites))

        for i, (x, name) in enumerate(zip(x_positions, metabolites)):
            # Metabolite circle
            compound = Circle(radius=0.4)
            compound.set_fill(METABOLOMICS_COLOR, opacity=0.7)
            compound.set_stroke(WHITE, width=2)
            compound.move_to([x, 0, 0])

            label = Text(name, font_size=11)
            label.next_to(compound, DOWN, buff=0.15)
            label.set_color(WHITE)

            compounds.add(VGroup(compound, label))

            # Arrow to next metabolite
            if i < len(metabolites) - 1:
                arrow = Arrow(
                    start=np.array([x + 0.5, 0, 0]),
                    end=np.array([x_positions[i + 1] - 0.5, 0, 0]),
                    buff=0,
                    stroke_width=3
                )
                arrow.set_color(WHITE)
                arrows.add(arrow)

                # Enzyme label above arrow
                enzyme_names = ["HK", "PGI", "PFK", "Aldolase"]
                if i < len(enzyme_names):
                    enzyme = Text(enzyme_names[i], font_size=10)
                    enzyme.move_to(arrow.get_center() + UP * 0.3)
                    enzyme.set_color(YELLOW)
                    enzymes.add(enzyme)

        self.add(compounds, arrows, enzymes)
        self.compounds = compounds
        self.arrows = arrows


class SmallMolecule(VGroup):
    """Visualization of a small molecule (e.g., metabolite)."""

    def __init__(self, structure="hexagon", **kwargs):
        super().__init__(**kwargs)

        if structure == "hexagon":
            # Create benzene-like ring
            ring = RegularPolygon(n=6, start_angle=PI/6)
            ring.set_stroke(METABOLOMICS_COLOR, width=3)
            ring.scale(0.5)

            # Add double bonds (alternating)
            inner_ring = RegularPolygon(n=6, start_angle=PI/6)
            inner_ring.set_stroke(METABOLOMICS_COLOR, width=2)
            inner_ring.scale(0.35)

            # Atom decorations
            atoms = VGroup()
            vertices = ring.get_vertices()
            for i, v in enumerate(vertices):
                atom = Dot(radius=0.08)
                atom.move_to(v)
                if i % 2 == 0:
                    atom.set_color(RED)  # Oxygen-like
                else:
                    atom.set_color(GREY)  # Carbon
                atoms.add(atom)

            self.add(ring, inner_ring, atoms)

        elif structure == "chain":
            # Create carbon chain
            points = []
            for i in range(6):
                x = i * 0.3 - 0.75
                y = 0.2 * (i % 2) - 0.1
                points.append([x, y, 0])

            chain = VMobject()
            chain.set_points_as_corners([np.array(p) for p in points])
            chain.set_stroke(METABOLOMICS_COLOR, width=3)

            atoms = VGroup()
            for i, p in enumerate(points):
                atom = Dot(radius=0.06)
                atom.move_to(p)
                atom.set_color(GREY)
                atoms.add(atom)

            self.add(chain, atoms)


# =============================================================================
# MAIN SCENES
# =============================================================================

class GenomicsScene(Scene):
    """Visualization of genomic concepts: DNA structure, sequences, and variations."""

    def construct(self):
        # Title
        title = Text("Genomics", font_size=48)
        title.set_color(GENOMICS_COLOR)
        title.to_edge(UP)

        subtitle = Text("DNA Structure & Genetic Information", font_size=24)
        subtitle.next_to(title, DOWN)
        subtitle.set_color(GREY)

        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()

        # DNA Double Helix
        dna = DNAHelix(num_turns=2, height=3.5)
        dna.shift(LEFT * 3)

        self.play(ShowCreation(dna), run_time=3)
        self.wait()

        # DNA sequence representation
        sequence_title = Text("DNA Sequence", font_size=20)
        sequence_title.move_to(RIGHT * 3 + UP * 1.5)

        sequence = "ATCGATCGATCG"
        seq_chars = VGroup()
        colors = {
            "A": ADENINE_COLOR, "T": THYMINE_COLOR,
            "G": GUANINE_COLOR, "C": CYTOSINE_COLOR
        }

        for i, char in enumerate(sequence):
            c = Text(char, font_size=24)
            c.set_color(colors[char])
            c.move_to(RIGHT * (1.5 + i * 0.35) + UP * 0.5)
            seq_chars.add(c)

        self.play(Write(sequence_title))
        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in seq_chars], lag_ratio=0.1))
        self.wait()

        # SNP visualization
        snp_title = Text("Single Nucleotide Polymorphism (SNP)", font_size=18)
        snp_title.move_to(RIGHT * 3 + DOWN * 0.5)

        # Show variant
        variant_seq = "ATCGTTCGATCG"
        variant_chars = VGroup()

        for i, char in enumerate(variant_seq):
            c = Text(char, font_size=24)
            c.set_color(colors[char])
            c.move_to(RIGHT * (1.5 + i * 0.35) + DOWN * 1.2)
            if i == 4:  # Highlight the SNP
                highlight = SurroundingRectangle(c, color=YELLOW, buff=0.05)
                variant_chars.add(VGroup(c, highlight))
            else:
                variant_chars.add(c)

        self.play(Write(snp_title))
        self.play(LaggedStart(*[FadeIn(c, shift=UP) for c in variant_chars], lag_ratio=0.1))

        # Arrow pointing to SNP
        snp_arrow = Arrow(
            start=RIGHT * 3.3 + DOWN * 0.7,
            end=RIGHT * 3.3 + DOWN * 1.05,
            buff=0,
            stroke_width=2
        )
        snp_arrow.set_color(YELLOW)
        snp_label = Text("A→T", font_size=14, color=YELLOW)
        snp_label.next_to(snp_arrow, RIGHT, buff=0.1)

        self.play(ShowCreation(snp_arrow), Write(snp_label))
        self.wait(2)

        # Clear and show summary
        self.play(*[FadeOut(m) for m in self.mobjects])

        summary = VGroup(
            Text("Genomics Studies:", font_size=28, color=GENOMICS_COLOR),
            Text("- Complete DNA sequences", font_size=20),
            Text("- Genetic variations (SNPs, CNVs)", font_size=20),
            Text("- Structural variants", font_size=20),
            Text("- Genome assembly & annotation", font_size=20),
        )
        summary.arrange(DOWN, aligned_edge=LEFT, buff=0.3)

        self.play(LaggedStart(*[FadeIn(s, shift=LEFT) for s in summary], lag_ratio=0.2))
        self.wait(2)


class EpigenomicsScene(Scene):
    """Visualization of epigenomic concepts: DNA methylation and histone modifications."""

    def construct(self):
        # Title
        title = Text("Epigenomics", font_size=48)
        title.set_color(EPIGENOMICS_COLOR)
        title.to_edge(UP)

        subtitle = Text("Chemical Modifications to DNA & Histones", font_size=24)
        subtitle.next_to(title, DOWN)
        subtitle.set_color(GREY)

        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()

        # DNA Methylation section
        methyl_title = Text("DNA Methylation", font_size=24)
        methyl_title.move_to(LEFT * 3.5 + UP * 1)
        methyl_title.set_color(EPIGENOMICS_COLOR)

        # Create CpG island visualization
        dna_segment = VGroup()
        bases = ["C", "G", "C", "G", "C", "G", "A", "T"]

        for i, base in enumerate(bases):
            rect = Square(side_length=0.4)
            rect.move_to(LEFT * (4.5 - i * 0.5) + DOWN * 0.5)

            color = {
                "C": CYTOSINE_COLOR, "G": GUANINE_COLOR,
                "A": ADENINE_COLOR, "T": THYMINE_COLOR
            }[base]
            rect.set_fill(color, opacity=0.7)
            rect.set_stroke(WHITE, width=1)

            label = Text(base, font_size=14)
            label.move_to(rect.get_center())

            dna_segment.add(VGroup(rect, label))

        self.play(Write(methyl_title), FadeIn(dna_segment))

        # Add methylation marks to cytosines
        methyl_marks = VGroup()
        for i, base in enumerate(bases):
            if base == "C" and i < len(bases) - 1 and bases[i + 1] == "G":
                mark = Circle(radius=0.12)
                mark.set_fill(EPIGENOMICS_COLOR, opacity=1)
                mark.set_stroke(WHITE, width=1)
                mark.move_to(LEFT * (4.5 - i * 0.5) + DOWN * 0.1)

                me_label = Text("Me", font_size=8)
                me_label.move_to(mark.get_center())
                me_label.set_color(WHITE)

                methyl_marks.add(VGroup(mark, me_label))

        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in methyl_marks], lag_ratio=0.3))

        cpg_label = Text("CpG Island", font_size=14, color=GREY)
        cpg_label.next_to(dna_segment, DOWN, buff=0.3)
        self.play(Write(cpg_label))
        self.wait()

        # Histone modification section
        histone_title = Text("Histone Modifications", font_size=24)
        histone_title.move_to(RIGHT * 2.5 + UP * 1)
        histone_title.set_color(EPIGENOMICS_COLOR)

        # Create histone octamer
        histone = HistoneOctamer(radius=0.6)
        histone.move_to(RIGHT * 2.5 + DOWN * 0.5)

        self.play(Write(histone_title), FadeIn(histone))

        # Show different modifications
        modifications = VGroup()
        mod_types = ["Ac", "Me", "Ph", "Ub"]
        mod_colors = [GREEN, EPIGENOMICS_COLOR, RED, YELLOW]

        for i, (mod, color) in enumerate(zip(mod_types, mod_colors)):
            angle = i * PI / 2
            pos = histone.get_center() + np.array([
                1.3 * np.cos(angle),
                1.3 * np.sin(angle),
                0
            ])

            mark = Circle(radius=0.15)
            mark.set_fill(color, opacity=0.8)
            mark.set_stroke(WHITE, width=1)
            mark.move_to(pos)

            label = Text(mod, font_size=10)
            label.move_to(mark.get_center())
            label.set_color(WHITE)

            modifications.add(VGroup(mark, label))

        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in modifications], lag_ratio=0.2))

        # Legend
        legend = VGroup(
            Text("Ac = Acetylation", font_size=12, color=GREEN),
            Text("Me = Methylation", font_size=12, color=EPIGENOMICS_COLOR),
            Text("Ph = Phosphorylation", font_size=12, color=RED),
            Text("Ub = Ubiquitination", font_size=12, color=YELLOW),
        )
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend.move_to(RIGHT * 5 + DOWN * 1.5)

        self.play(FadeIn(legend))
        self.wait(2)

        # Clear and show impact
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Show gene expression states
        active_gene = VGroup()
        active_label = Text("Active Gene", font_size=20, color=GREEN)
        active_label.move_to(LEFT * 3 + UP * 1)

        active_dna = Line(LEFT * 5, LEFT * 1, stroke_width=4)
        active_dna.set_color(GENOMICS_COLOR)
        active_dna.shift(DOWN * 0.2)

        # Open chromatin (loose nucleosomes)
        open_histones = VGroup()
        for i in range(3):
            h = Circle(radius=0.25)
            h.set_fill(EPIGENOMICS_COLOR, opacity=0.4)
            h.set_stroke(EPIGENOMICS_COLOR, width=1)
            h.move_to(LEFT * (4 - i * 1.5) + DOWN * 0.2)
            open_histones.add(h)

        active_gene.add(active_label, active_dna, open_histones)

        # Silenced gene
        silent_gene = VGroup()
        silent_label = Text("Silenced Gene", font_size=20, color=RED)
        silent_label.move_to(RIGHT * 3 + UP * 1)

        silent_dna = Line(RIGHT * 1, RIGHT * 5, stroke_width=4)
        silent_dna.set_color(GENOMICS_COLOR)
        silent_dna.shift(DOWN * 0.2)

        # Closed chromatin (tight nucleosomes)
        closed_histones = VGroup()
        for i in range(5):
            h = Circle(radius=0.25)
            h.set_fill(EPIGENOMICS_COLOR, opacity=0.8)
            h.set_stroke(EPIGENOMICS_COLOR, width=2)
            h.move_to(RIGHT * (1.5 + i * 0.7) + DOWN * 0.2)
            closed_histones.add(h)

        silent_gene.add(silent_label, silent_dna, closed_histones)

        self.play(FadeIn(active_gene), FadeIn(silent_gene))

        # Arrows showing expression
        active_arrow = Arrow(LEFT * 3, LEFT * 3 + DOWN, buff=0.1)
        active_arrow.set_color(GREEN)
        active_text = Text("High Expression", font_size=14, color=GREEN)
        active_text.next_to(active_arrow, DOWN)

        silent_arrow = Arrow(RIGHT * 3, RIGHT * 3 + DOWN, buff=0.1)
        silent_arrow.set_color(RED)
        silent_text = Text("Low Expression", font_size=14, color=RED)
        silent_text.next_to(silent_arrow, DOWN)

        self.play(
            ShowCreation(active_arrow), Write(active_text),
            ShowCreation(silent_arrow), Write(silent_text)
        )
        self.wait(2)


class TranscriptomicsScene(Scene):
    """Visualization of transcriptomic concepts: RNA expression and analysis."""

    def construct(self):
        # Title
        title = Text("Transcriptomics", font_size=48)
        title.set_color(TRANSCRIPTOMICS_COLOR)
        title.to_edge(UP)

        subtitle = Text("RNA Expression Analysis", font_size=24)
        subtitle.next_to(title, DOWN)
        subtitle.set_color(GREY)

        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()

        # Central dogma - Transcription
        dna_label = Text("DNA", font_size=20, color=GENOMICS_COLOR)
        dna_line = Line(LEFT * 3, RIGHT, stroke_width=6)
        dna_line.set_color(GENOMICS_COLOR)
        dna_group = VGroup(dna_label, dna_line)
        dna_label.next_to(dna_line, LEFT)
        dna_group.move_to(LEFT * 2 + UP * 0.5)

        self.play(ShowCreation(dna_line), Write(dna_label))

        # Transcription arrow
        trans_arrow = Arrow(LEFT * 0.5 + UP * 0.3, LEFT * 0.5 + DOWN * 0.3, buff=0)
        trans_arrow.set_color(YELLOW)
        trans_label = Text("Transcription", font_size=14, color=YELLOW)
        trans_label.next_to(trans_arrow, RIGHT)

        self.play(ShowCreation(trans_arrow), Write(trans_label))

        # RNA molecule
        rna = RNAMolecule(length=15)
        rna.move_to(LEFT * 2 + DOWN * 1)
        rna_label = Text("mRNA", font_size=20, color=TRANSCRIPTOMICS_COLOR)
        rna_label.next_to(rna, LEFT, buff=0.3)

        self.play(ShowCreation(rna), Write(rna_label))
        self.wait()

        # Move everything left
        left_group = VGroup(dna_group, trans_arrow, trans_label, rna, rna_label)
        self.play(left_group.animate.shift(LEFT * 1.5).scale(0.8))

        # Gene Expression Heatmap
        heatmap_title = Text("Expression Matrix", font_size=20)
        heatmap_title.move_to(RIGHT * 3 + UP * 2)

        heatmap = GeneExpressionHeatmap(n_genes=8, n_samples=5, cell_size=0.35)
        heatmap.move_to(RIGHT * 3)

        self.play(Write(heatmap_title))
        self.play(FadeIn(heatmap, scale=0.5), run_time=2)

        # Color scale legend
        scale_label = Text("Expression Level", font_size=12)
        scale_label.move_to(RIGHT * 3 + DOWN * 2.3)

        color_scale = VGroup()
        for i, val in enumerate(np.linspace(0, 1, 10)):
            rect = Rectangle(height=0.15, width=0.25)
            if val < 0.5:
                color = interpolate_color(BLUE, WHITE, val * 2)
            else:
                color = interpolate_color(WHITE, RED, (val - 0.5) * 2)
            rect.set_fill(color, opacity=1)
            rect.set_stroke(width=0)
            rect.move_to(RIGHT * (1.5 + i * 0.25) + DOWN * 2.6)
            color_scale.add(rect)

        low_label = Text("Low", font_size=10)
        low_label.next_to(color_scale, LEFT, buff=0.1)
        high_label = Text("High", font_size=10)
        high_label.next_to(color_scale, RIGHT, buff=0.1)

        self.play(
            Write(scale_label),
            FadeIn(color_scale),
            Write(low_label), Write(high_label)
        )
        self.wait(2)

        # Clear and show RNA-seq workflow
        self.play(*[FadeOut(m) for m in self.mobjects])

        workflow_title = Text("RNA-seq Workflow", font_size=32, color=TRANSCRIPTOMICS_COLOR)
        workflow_title.to_edge(UP)

        steps = [
            ("1. RNA Extraction", "Extract total RNA"),
            ("2. Library Prep", "Fragment & add adapters"),
            ("3. Sequencing", "Generate reads"),
            ("4. Alignment", "Map to reference"),
            ("5. Quantification", "Count expression"),
        ]

        step_mobjects = VGroup()
        for i, (step, desc) in enumerate(steps):
            box = RoundedRectangle(width=2.2, height=1, corner_radius=0.1)
            box.set_fill(TRANSCRIPTOMICS_COLOR, opacity=0.3)
            box.set_stroke(TRANSCRIPTOMICS_COLOR, width=2)
            box.move_to(LEFT * 4 + RIGHT * i * 2.3)

            step_text = Text(step, font_size=12)
            step_text.move_to(box.get_center() + UP * 0.2)

            desc_text = Text(desc, font_size=9, color=GREY)
            desc_text.move_to(box.get_center() + DOWN * 0.2)

            step_mobjects.add(VGroup(box, step_text, desc_text))

        # Arrows between steps
        arrows = VGroup()
        for i in range(len(steps) - 1):
            arrow = Arrow(
                step_mobjects[i].get_right(),
                step_mobjects[i + 1].get_left(),
                buff=0.1,
                stroke_width=2
            )
            arrow.set_color(WHITE)
            arrows.add(arrow)

        self.play(Write(workflow_title))
        self.play(
            LaggedStart(*[FadeIn(s, scale=0.8) for s in step_mobjects], lag_ratio=0.2),
            LaggedStart(*[ShowCreation(a) for a in arrows], lag_ratio=0.2)
        )
        self.wait(2)


class ProteomicsScene(Scene):
    """Visualization of proteomic concepts: proteins and their interactions."""

    def construct(self):
        # Title
        title = Text("Proteomics", font_size=48)
        title.set_color(PROTEOMICS_COLOR)
        title.to_edge(UP)

        subtitle = Text("Protein Structure & Interactions", font_size=24)
        subtitle.next_to(title, DOWN)
        subtitle.set_color(GREY)

        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()

        # Protein structure
        structure_title = Text("Protein Secondary Structure", font_size=20)
        structure_title.move_to(LEFT * 3.5 + UP * 1)

        protein = ProteinStructure()
        protein.move_to(LEFT * 3.5 + DOWN * 0.5)
        protein.scale(0.9)

        self.play(Write(structure_title))
        self.play(ShowCreation(protein), run_time=2)
        self.wait()

        # Protein interaction network
        network_title = Text("Protein-Protein Interactions", font_size=20)
        network_title.move_to(RIGHT * 2.5 + UP * 1)

        network = ProteinInteractionNetwork(n_proteins=6)
        network.move_to(RIGHT * 2.5 + DOWN * 0.3)
        network.scale(0.6)

        self.play(Write(network_title))
        self.play(FadeIn(network.edges))
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in network.proteins], lag_ratio=0.1))
        self.wait()

        # Highlight an interaction
        highlight = network.edges[0].copy()
        highlight.set_stroke(YELLOW, width=4)

        self.play(ShowCreation(highlight))
        self.play(FadeOut(highlight))
        self.wait()

        # Clear and show mass spec workflow
        self.play(*[FadeOut(m) for m in self.mobjects])

        ms_title = Text("Mass Spectrometry Proteomics", font_size=32, color=PROTEOMICS_COLOR)
        ms_title.to_edge(UP)

        self.play(Write(ms_title))

        # Sample preparation
        sample = Circle(radius=0.5)
        sample.set_fill(PROTEOMICS_COLOR, opacity=0.5)
        sample.set_stroke(WHITE, width=2)
        sample.move_to(LEFT * 5)
        sample_label = Text("Sample", font_size=14)
        sample_label.next_to(sample, DOWN)

        # Digestion
        digest_arrow = Arrow(LEFT * 4.3, LEFT * 3.3, buff=0)
        digest_label = Text("Digest", font_size=12)
        digest_label.next_to(digest_arrow, UP, buff=0.1)

        # Peptides
        peptides = VGroup()
        for i in range(4):
            p = Line(ORIGIN, RIGHT * 0.4, stroke_width=3)
            p.set_color(PROTEOMICS_COLOR)
            p.move_to(LEFT * 2.8 + UP * (0.3 - i * 0.2))
            peptides.add(p)
        peptides_label = Text("Peptides", font_size=14)
        peptides_label.next_to(peptides, DOWN, buff=0.2)

        # MS instrument
        ms_box = Rectangle(width=2, height=1.5)
        ms_box.set_fill(GREY_D, opacity=0.5)
        ms_box.set_stroke(WHITE, width=2)
        ms_box.move_to(ORIGIN)
        ms_text = Text("Mass\nSpectrometer", font_size=12)
        ms_text.move_to(ms_box.get_center())

        ms_arrow = Arrow(LEFT * 1.8, LEFT * 1.1, buff=0)

        # Spectrum
        spectrum = VGroup()
        spectrum_box = Rectangle(width=2.5, height=1.5)
        spectrum_box.set_stroke(WHITE, width=1)
        spectrum_box.move_to(RIGHT * 3)

        # Add peaks
        peaks = VGroup()
        peak_heights = [0.3, 0.8, 0.5, 1.0, 0.4, 0.6]
        for i, h in enumerate(peak_heights):
            peak = Line(ORIGIN, UP * h * 1.2, stroke_width=2)
            peak.set_color(PROTEOMICS_COLOR)
            peak.move_to(RIGHT * (1.9 + i * 0.35) + DOWN * 0.5)
            peaks.add(peak)

        # m/z axis
        mz_axis = Arrow(RIGHT * 1.8 + DOWN * 0.5, RIGHT * 4.2 + DOWN * 0.5, buff=0, stroke_width=1)
        mz_label = Text("m/z", font_size=12)
        mz_label.next_to(mz_axis, DOWN, buff=0.1)

        spectrum.add(spectrum_box, peaks, mz_axis, mz_label)

        spec_arrow = Arrow(RIGHT * 1.1, RIGHT * 1.7, buff=0)

        # Animate workflow
        self.play(FadeIn(sample), Write(sample_label))
        self.play(ShowCreation(digest_arrow), Write(digest_label))
        self.play(FadeIn(peptides), Write(peptides_label))
        self.play(ShowCreation(ms_arrow))
        self.play(FadeIn(ms_box), Write(ms_text))
        self.play(ShowCreation(spec_arrow))
        self.play(
            FadeIn(spectrum_box),
            LaggedStart(*[ShowCreation(p) for p in peaks], lag_ratio=0.1),
            ShowCreation(mz_axis), Write(mz_label)
        )

        # Data analysis
        data_label = Text("Protein Identification\n& Quantification", font_size=14)
        data_label.move_to(RIGHT * 3 + DOWN * 1.8)

        self.play(Write(data_label))
        self.wait(2)


class MetabolomicsScene(Scene):
    """Visualization of metabolomic concepts: metabolites and pathways."""

    def construct(self):
        # Title
        title = Text("Metabolomics", font_size=48)
        title.set_color(METABOLOMICS_COLOR)
        title.to_edge(UP)

        subtitle = Text("Small Molecules & Metabolic Pathways", font_size=24)
        subtitle.next_to(title, DOWN)
        subtitle.set_color(GREY)

        self.play(Write(title), FadeIn(subtitle, shift=UP))
        self.wait()

        # Metabolic pathway (Glycolysis simplified)
        pathway_title = Text("Glycolysis Pathway", font_size=24)
        pathway_title.move_to(UP * 1)

        pathway = MetabolicPathway()
        pathway.move_to(DOWN * 0.5)
        pathway.scale(0.85)

        self.play(Write(pathway_title))
        self.play(FadeIn(pathway.compounds))
        self.play(
            LaggedStart(*[ShowCreation(a) for a in pathway.arrows], lag_ratio=0.2),
            LaggedStart(*[FadeIn(e) for e in pathway.enzymes], lag_ratio=0.2)
        )
        self.wait()

        # Energy yield
        atp_box = VGroup()
        atp_rect = RoundedRectangle(width=2, height=0.8, corner_radius=0.1)
        atp_rect.set_fill(YELLOW, opacity=0.3)
        atp_rect.set_stroke(YELLOW, width=2)
        atp_text = Text("2 ATP + 2 NADH", font_size=14)
        atp_text.move_to(atp_rect.get_center())
        atp_box.add(atp_rect, atp_text)
        atp_box.move_to(RIGHT * 3.5 + DOWN * 1.5)

        yield_arrow = Arrow(
            pathway.compounds[-1].get_center() + DOWN * 0.3,
            atp_box.get_left(),
            buff=0.1
        )
        yield_arrow.set_color(YELLOW)

        self.play(ShowCreation(yield_arrow), FadeIn(atp_box))
        self.wait()

        # Clear and show metabolite diversity
        self.play(*[FadeOut(m) for m in self.mobjects])

        diversity_title = Text("Metabolite Classes", font_size=32, color=METABOLOMICS_COLOR)
        diversity_title.to_edge(UP)

        self.play(Write(diversity_title))

        # Show different metabolite types
        classes = [
            ("Amino Acids", "Building blocks", BLUE),
            ("Lipids", "Energy storage", YELLOW),
            ("Carbohydrates", "Energy source", GREEN),
            ("Nucleotides", "Genetic info", RED),
            ("Organic Acids", "Metabolism", PURPLE),
        ]

        class_mobjects = VGroup()
        for i, (name, desc, color) in enumerate(classes):
            row = i // 3
            col = i % 3

            x = -4 + col * 4
            y = 1 - row * 2.5

            # Molecule representation
            mol = SmallMolecule(structure="hexagon" if i % 2 == 0 else "chain")
            mol.move_to([x, y, 0])
            mol.set_color(color)

            name_text = Text(name, font_size=16, color=color)
            name_text.next_to(mol, DOWN, buff=0.2)

            desc_text = Text(desc, font_size=12, color=GREY)
            desc_text.next_to(name_text, DOWN, buff=0.1)

            class_mobjects.add(VGroup(mol, name_text, desc_text))

        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in class_mobjects], lag_ratio=0.2))
        self.wait()

        # Show concentration differences
        self.play(*[FadeOut(m) for m in self.mobjects if m != diversity_title])

        bar_title = Text("Metabolite Concentrations", font_size=24)
        bar_title.move_to(UP * 2)

        # Simple bar chart
        metabolites = ["Glucose", "Lactate", "Pyruvate", "ATP", "ADP"]
        values = [5.0, 1.5, 0.1, 3.0, 0.3]
        max_val = max(values)

        bars = VGroup()
        labels = VGroup()

        for i, (met, val) in enumerate(zip(metabolites, values)):
            bar_height = (val / max_val) * 2.5
            bar = Rectangle(width=0.6, height=bar_height)
            bar.set_fill(METABOLOMICS_COLOR, opacity=0.7)
            bar.set_stroke(WHITE, width=1)
            bar.move_to(LEFT * 3 + RIGHT * i * 1.2 + DOWN * (1.5 - bar_height / 2))

            label = Text(met, font_size=12)
            label.next_to(bar, DOWN, buff=0.1)
            label.rotate(PI / 6)

            val_label = Text(f"{val}", font_size=10)
            val_label.next_to(bar, UP, buff=0.05)

            bars.add(bar)
            labels.add(VGroup(label, val_label))

        self.play(Write(bar_title))
        self.play(
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.1),
            LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.1)
        )

        # Y-axis
        y_axis = Arrow(LEFT * 3.5 + DOWN * 1.5, LEFT * 3.5 + UP * 1.5, buff=0, stroke_width=2)
        y_label = Text("Concentration (mM)", font_size=12)
        y_label.next_to(y_axis, LEFT, buff=0.1)
        y_label.rotate(PI / 2)

        self.play(ShowCreation(y_axis), Write(y_label))
        self.wait(2)


class MultiomicsOverview(Scene):
    """Comprehensive overview showing all omics layers and their integration."""

    def construct(self):
        # Main title
        title = Text("Multi-omics Integration", font_size=48)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait()

        # Central dogma flow with all omics layers
        # DNA (Genomics)
        dna_circle = Circle(radius=0.8)
        dna_circle.set_fill(GENOMICS_COLOR, opacity=0.3)
        dna_circle.set_stroke(GENOMICS_COLOR, width=3)
        dna_circle.move_to(LEFT * 4.5 + UP * 0.5)

        dna_label = Text("DNA", font_size=20, color=GENOMICS_COLOR)
        dna_label.move_to(dna_circle.get_center())

        genomics_label = Text("Genomics", font_size=14)
        genomics_label.next_to(dna_circle, DOWN, buff=0.1)
        genomics_label.set_color(GENOMICS_COLOR)

        dna_group = VGroup(dna_circle, dna_label, genomics_label)

        # Epigenomics layer (surrounding DNA)
        epi_ring = Annulus(inner_radius=0.9, outer_radius=1.1)
        epi_ring.set_fill(EPIGENOMICS_COLOR, opacity=0.4)
        epi_ring.set_stroke(EPIGENOMICS_COLOR, width=2)
        epi_ring.move_to(dna_circle.get_center())

        epi_label = Text("Epigenomics", font_size=12, color=EPIGENOMICS_COLOR)
        epi_label.next_to(epi_ring, UP, buff=0.1)

        epi_group = VGroup(epi_ring, epi_label)

        # RNA (Transcriptomics)
        rna_circle = Circle(radius=0.8)
        rna_circle.set_fill(TRANSCRIPTOMICS_COLOR, opacity=0.3)
        rna_circle.set_stroke(TRANSCRIPTOMICS_COLOR, width=3)
        rna_circle.move_to(LEFT * 1.5 + UP * 0.5)

        rna_label = Text("RNA", font_size=20, color=TRANSCRIPTOMICS_COLOR)
        rna_label.move_to(rna_circle.get_center())

        trans_label = Text("Transcriptomics", font_size=14)
        trans_label.next_to(rna_circle, DOWN, buff=0.1)
        trans_label.set_color(TRANSCRIPTOMICS_COLOR)

        rna_group = VGroup(rna_circle, rna_label, trans_label)

        # Protein (Proteomics)
        protein_circle = Circle(radius=0.8)
        protein_circle.set_fill(PROTEOMICS_COLOR, opacity=0.3)
        protein_circle.set_stroke(PROTEOMICS_COLOR, width=3)
        protein_circle.move_to(RIGHT * 1.5 + UP * 0.5)

        protein_label = Text("Protein", font_size=20, color=PROTEOMICS_COLOR)
        protein_label.move_to(protein_circle.get_center())

        prot_label = Text("Proteomics", font_size=14)
        prot_label.next_to(protein_circle, DOWN, buff=0.1)
        prot_label.set_color(PROTEOMICS_COLOR)

        protein_group = VGroup(protein_circle, protein_label, prot_label)

        # Metabolite (Metabolomics)
        metab_circle = Circle(radius=0.8)
        metab_circle.set_fill(METABOLOMICS_COLOR, opacity=0.3)
        metab_circle.set_stroke(METABOLOMICS_COLOR, width=3)
        metab_circle.move_to(RIGHT * 4.5 + UP * 0.5)

        metab_label = Text("Metabolite", font_size=18, color=METABOLOMICS_COLOR)
        metab_label.move_to(metab_circle.get_center())

        metabol_label = Text("Metabolomics", font_size=14)
        metabol_label.next_to(metab_circle, DOWN, buff=0.1)
        metabol_label.set_color(METABOLOMICS_COLOR)

        metab_group = VGroup(metab_circle, metab_label, metabol_label)

        # Arrows connecting layers
        arrow1 = Arrow(dna_circle.get_right(), rna_circle.get_left(), buff=0.1)
        arrow1.set_color(WHITE)
        arrow1_label = Text("Transcription", font_size=10)
        arrow1_label.next_to(arrow1, UP, buff=0.05)

        arrow2 = Arrow(rna_circle.get_right(), protein_circle.get_left(), buff=0.1)
        arrow2.set_color(WHITE)
        arrow2_label = Text("Translation", font_size=10)
        arrow2_label.next_to(arrow2, UP, buff=0.05)

        arrow3 = Arrow(protein_circle.get_right(), metab_circle.get_left(), buff=0.1)
        arrow3.set_color(WHITE)
        arrow3_label = Text("Catalysis", font_size=10)
        arrow3_label.next_to(arrow3, UP, buff=0.05)

        # Animate the central dogma
        self.play(FadeIn(epi_group))
        self.play(FadeIn(dna_group))
        self.play(ShowCreation(arrow1), Write(arrow1_label))
        self.play(FadeIn(rna_group))
        self.play(ShowCreation(arrow2), Write(arrow2_label))
        self.play(FadeIn(protein_group))
        self.play(ShowCreation(arrow3), Write(arrow3_label))
        self.play(FadeIn(metab_group))
        self.wait()

        # Show regulatory feedback loops
        feedback_title = Text("Regulatory Feedback", font_size=16, color=GREY)
        feedback_title.move_to(DOWN * 1.5)

        # Feedback arrows (metabolites regulate gene expression)
        feedback1 = CurvedArrow(
            metab_circle.get_bottom() + DOWN * 0.2,
            dna_circle.get_bottom() + DOWN * 0.2,
            angle=-PI/3
        )
        feedback1.set_color(METABOLOMICS_COLOR)
        feedback1.set_stroke(width=2)

        # Proteins regulate transcription
        feedback2 = CurvedArrow(
            protein_circle.get_top() + UP * 0.3,
            rna_circle.get_top() + UP * 0.3,
            angle=PI/4
        )
        feedback2.set_color(PROTEOMICS_COLOR)
        feedback2.set_stroke(width=2)

        self.play(Write(feedback_title))
        self.play(ShowCreation(feedback1), ShowCreation(feedback2))
        self.wait()

        # Clear and show integration visualization
        self.play(*[FadeOut(m) for m in self.mobjects])

        # Integration title
        int_title = Text("Multi-omics Data Integration", font_size=36)
        int_title.to_edge(UP)

        self.play(Write(int_title))

        # Show different data types as matrices
        matrices = VGroup()

        # Genomics matrix
        gen_matrix = self._create_data_matrix(4, 3, GENOMICS_COLOR, "Genomics\n(SNPs)")
        gen_matrix.move_to(LEFT * 4 + UP * 0.5)

        # Transcriptomics matrix
        trans_matrix = self._create_data_matrix(4, 3, TRANSCRIPTOMICS_COLOR, "Transcriptomics\n(Expression)")
        trans_matrix.move_to(LEFT * 1.3 + UP * 0.5)

        # Proteomics matrix
        prot_matrix = self._create_data_matrix(4, 3, PROTEOMICS_COLOR, "Proteomics\n(Abundance)")
        prot_matrix.move_to(RIGHT * 1.3 + UP * 0.5)

        # Metabolomics matrix
        metab_matrix = self._create_data_matrix(4, 3, METABOLOMICS_COLOR, "Metabolomics\n(Conc.)")
        metab_matrix.move_to(RIGHT * 4 + UP * 0.5)

        matrices.add(gen_matrix, trans_matrix, prot_matrix, metab_matrix)

        self.play(LaggedStart(*[FadeIn(m, scale=0.8) for m in matrices], lag_ratio=0.2))
        self.wait()

        # Integration method
        int_box = RoundedRectangle(width=3, height=1, corner_radius=0.1)
        int_box.set_fill(GREY_D, opacity=0.5)
        int_box.set_stroke(WHITE, width=2)
        int_box.move_to(DOWN * 1.5)

        int_text = Text("Integration\nAlgorithm", font_size=14)
        int_text.move_to(int_box.get_center())

        # Arrows to integration
        int_arrows = VGroup()
        for matrix in matrices:
            arrow = Arrow(
                matrix.get_bottom(),
                int_box.get_top(),
                buff=0.1,
                stroke_width=2
            )
            arrow.set_color(GREY)
            int_arrows.add(arrow)

        self.play(
            LaggedStart(*[ShowCreation(a) for a in int_arrows], lag_ratio=0.1),
            FadeIn(int_box), Write(int_text)
        )

        # Output: integrated view
        output_circle = Circle(radius=0.8)
        output_circle.set_fill(WHITE, opacity=0.2)
        output_circle.set_stroke(WHITE, width=2)
        output_circle.move_to(DOWN * 3.2)

        output_label = Text("Integrated\nBiomarkers", font_size=14)
        output_label.move_to(output_circle.get_center())

        output_arrow = Arrow(int_box.get_bottom(), output_circle.get_top(), buff=0.1)
        output_arrow.set_color(WHITE)

        self.play(ShowCreation(output_arrow))
        self.play(FadeIn(output_circle), Write(output_label))
        self.wait(2)

        # Final summary
        self.play(*[FadeOut(m) for m in self.mobjects])

        summary_title = Text("Multi-omics Analysis Enables", font_size=32)
        summary_title.to_edge(UP)

        benefits = VGroup(
            Text("Holistic understanding of biological systems", font_size=20),
            Text("Discovery of novel biomarkers", font_size=20),
            Text("Identification of disease mechanisms", font_size=20),
            Text("Personalized medicine approaches", font_size=20),
            Text("Drug target discovery", font_size=20),
        )
        benefits.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        benefits.move_to(ORIGIN)

        # Add bullet points
        for b in benefits:
            bullet = Dot(radius=0.08, color=WHITE)
            bullet.next_to(b, LEFT, buff=0.2)
            b.add_to_back(bullet)

        self.play(Write(summary_title))
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT) for b in benefits], lag_ratio=0.2))
        self.wait(2)

    def _create_data_matrix(self, rows, cols, color, label_text):
        """Helper to create a small data matrix visualization."""
        matrix = VGroup()

        for i in range(rows):
            for j in range(cols):
                cell = Square(side_length=0.3)
                cell.set_fill(color, opacity=np.random.uniform(0.2, 0.9))
                cell.set_stroke(WHITE, width=0.5)
                cell.move_to([j * 0.32, -i * 0.32, 0])
                matrix.add(cell)

        label = Text(label_text, font_size=10)
        label.next_to(matrix, DOWN, buff=0.2)
        label.set_color(color)

        group = VGroup(matrix, label)
        return group


class DataIntegrationMath(Scene):
    """Mathematical foundations of multi-omics data integration."""

    def construct(self):
        # Title
        title = Text("Mathematical Foundations", font_size=40)
        title.to_edge(UP)

        subtitle = Text("Multi-omics Data Integration", font_size=24, color=GREY)
        subtitle.next_to(title, DOWN)

        self.play(Write(title), FadeIn(subtitle))
        self.wait()

        # Data representation
        data_title = Text("Data Representation", font_size=28)
        data_title.move_to(UP * 1.5)

        self.play(Write(data_title))

        # Matrices for each omics type
        matrix_eq = Tex(
            r"X_g \in \mathbb{R}^{n \times p_g}, \quad "
            r"X_t \in \mathbb{R}^{n \times p_t}, \quad "
            r"X_p \in \mathbb{R}^{n \times p_p}, \quad "
            r"X_m \in \mathbb{R}^{n \times p_m}",
            font_size=28
        )
        matrix_eq.move_to(UP * 0.5)

        self.play(Write(matrix_eq))

        # Explanation
        explanation = VGroup(
            Text("n = number of samples", font_size=18),
            Text("p = features (genes, proteins, metabolites)", font_size=18),
        )
        explanation.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation.move_to(DOWN * 0.5)
        explanation.set_color(GREY)

        self.play(FadeIn(explanation))
        self.wait()

        # Clear and show integration methods
        self.play(*[FadeOut(m) for m in self.mobjects if m != title])

        # Concatenation approach
        concat_title = Text("1. Early Integration (Concatenation)", font_size=24)
        concat_title.move_to(UP * 2)

        concat_eq = Tex(
            r"X_{concat} = [X_g | X_t | X_p | X_m] \in \mathbb{R}^{n \times (p_g + p_t + p_p + p_m)}",
            font_size=26
        )
        concat_eq.move_to(UP * 1)

        self.play(Write(concat_title))
        self.play(Write(concat_eq))
        self.wait()

        # Multi-view learning
        mv_title = Text("2. Multi-view Learning", font_size=24)
        mv_title.move_to(UP * 0)

        mv_eq = Tex(
            r"\min_{W_k, H} \sum_{k=1}^{K} \|X_k - W_k H\|_F^2 + \lambda \Omega(W, H)",
            font_size=26
        )
        mv_eq.move_to(DOWN * 1)

        self.play(Write(mv_title))
        self.play(Write(mv_eq))
        self.wait()

        # Network-based integration
        net_title = Text("3. Network Integration", font_size=24)
        net_title.move_to(DOWN * 2)

        net_eq = Tex(
            r"G_{integrated} = \sum_{k=1}^{K} \alpha_k G_k, \quad \sum_k \alpha_k = 1",
            font_size=26
        )
        net_eq.move_to(DOWN * 3)

        self.play(Write(net_title))
        self.play(Write(net_eq))
        self.wait(2)

        # Clear and show similarity network fusion
        self.play(*[FadeOut(m) for m in self.mobjects])

        snf_title = Text("Similarity Network Fusion (SNF)", font_size=36)
        snf_title.to_edge(UP)

        self.play(Write(snf_title))

        # SNF steps
        steps = VGroup(
            Tex(r"\text{1. Compute similarity matrices: } W_k = \exp(-\rho^2(x_i, x_j) / \sigma)", font_size=22),
            Tex(r"\text{2. Create kernel matrices: } P_k = D_k^{-1} W_k", font_size=22),
            Tex(r"\text{3. Iteratively fuse: } P_k^{(t+1)} = S_k \times \left(\frac{\sum_{j \neq k} P_j^{(t)}}{K-1}\right) \times S_k^T", font_size=22),
            Tex(r"\text{4. Converge to unified: } P^* = \frac{1}{K} \sum_k P_k^{(\infty)}", font_size=22),
        )
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        steps.move_to(ORIGIN)

        self.play(LaggedStart(*[Write(s) for s in steps], lag_ratio=0.5))
        self.wait(2)

        # PCA visualization concept
        self.play(*[FadeOut(m) for m in self.mobjects])

        pca_title = Text("Dimensionality Reduction", font_size=36)
        pca_title.to_edge(UP)

        self.play(Write(pca_title))

        # Show high-dim to low-dim
        high_dim = VGroup()
        for i in range(20):
            dot = Dot(radius=0.05)
            dot.move_to([
                np.random.uniform(-2, 0),
                np.random.uniform(-1, 1),
                0
            ])
            dot.set_color(interpolate_color(BLUE, RED, i / 20))
            high_dim.add(dot)

        high_label = Text("High-dimensional\nomics data", font_size=14)
        high_label.move_to(LEFT * 3 + DOWN * 2)

        # Arrow
        transform_arrow = Arrow(LEFT * 0.5, RIGHT * 0.5, buff=0)
        transform_label = Text("PCA/UMAP/t-SNE", font_size=12)
        transform_label.next_to(transform_arrow, UP)

        # Low-dim representation with clusters
        low_dim = VGroup()
        colors = [GENOMICS_COLOR, TRANSCRIPTOMICS_COLOR, PROTEOMICS_COLOR]
        centers = [RIGHT * 2 + UP * 0.5, RIGHT * 3 + DOWN * 0.3, RIGHT * 2.5 + DOWN * 0.8]

        for j, (center, color) in enumerate(zip(centers, colors)):
            for i in range(7):
                dot = Dot(radius=0.08)
                offset = np.array([
                    np.random.uniform(-0.3, 0.3),
                    np.random.uniform(-0.3, 0.3),
                    0
                ])
                dot.move_to(center + offset)
                dot.set_color(color)
                low_dim.add(dot)

        low_label = Text("Low-dimensional\nembedding", font_size=14)
        low_label.move_to(RIGHT * 3 + DOWN * 2)

        self.play(FadeIn(high_dim), Write(high_label))
        self.play(ShowCreation(transform_arrow), Write(transform_label))
        self.play(
            Transform(high_dim.copy(), low_dim),
            FadeIn(low_dim),
            Write(low_label)
        )
        self.wait(2)


class ClinicalApplications(Scene):
    """Clinical applications of multi-omics analysis."""

    def construct(self):
        # Title
        title = Text("Clinical Applications", font_size=48)
        title.to_edge(UP)

        self.play(Write(title))
        self.wait()

        # Application areas
        applications = [
            ("Cancer\nSubtyping", TRANSCRIPTOMICS_COLOR, LEFT * 4 + UP * 0.5),
            ("Drug\nResponse", PROTEOMICS_COLOR, LEFT * 1.3 + UP * 0.5),
            ("Disease\nBiomarkers", METABOLOMICS_COLOR, RIGHT * 1.3 + UP * 0.5),
            ("Precision\nMedicine", GENOMICS_COLOR, RIGHT * 4 + UP * 0.5),
        ]

        app_mobjects = VGroup()
        for name, color, pos in applications:
            box = RoundedRectangle(width=2, height=1.5, corner_radius=0.1)
            box.set_fill(color, opacity=0.3)
            box.set_stroke(color, width=2)
            box.move_to(pos)

            label = Text(name, font_size=16)
            label.move_to(box.get_center())

            app_mobjects.add(VGroup(box, label))

        self.play(LaggedStart(*[FadeIn(a, scale=0.8) for a in app_mobjects], lag_ratio=0.2))
        self.wait()

        # Patient stratification example
        self.play(*[FadeOut(m) for m in self.mobjects if m != title])

        strat_title = Text("Patient Stratification Example", font_size=28)
        strat_title.move_to(UP * 2)

        self.play(Write(strat_title))

        # Show patient clusters
        np.random.seed(42)

        cluster_colors = [BLUE, GREEN, RED]
        cluster_centers = [LEFT * 2.5, ORIGIN, RIGHT * 2.5]
        cluster_labels = ["Subtype A", "Subtype B", "Subtype C"]

        all_patients = VGroup()

        for color, center, label in zip(cluster_colors, cluster_centers, cluster_labels):
            cluster = VGroup()
            for _ in range(15):
                patient = Dot(radius=0.1)
                offset = np.array([
                    np.random.uniform(-0.8, 0.8),
                    np.random.uniform(-0.6, 0.6),
                    0
                ])
                patient.move_to(center + offset)
                patient.set_color(color)
                cluster.add(patient)

            label_text = Text(label, font_size=14, color=color)
            label_text.next_to(cluster, DOWN, buff=0.3)

            all_patients.add(VGroup(cluster, label_text))

        self.play(LaggedStart(*[FadeIn(p) for p in all_patients], lag_ratio=0.3))

        # Show treatment assignment
        treatments = VGroup()
        treatment_texts = ["Treatment X", "Treatment Y", "Treatment Z"]

        for i, (center, text, color) in enumerate(zip(cluster_centers, treatment_texts, cluster_colors)):
            arrow = Arrow(center + DOWN * 1.2, center + DOWN * 2, buff=0)
            arrow.set_color(color)

            treat_label = Text(text, font_size=12, color=color)
            treat_label.next_to(arrow, DOWN, buff=0.1)

            treatments.add(VGroup(arrow, treat_label))

        self.play(LaggedStart(*[ShowCreation(t) for t in treatments], lag_ratio=0.2))
        self.wait(2)

        # Outcome visualization
        outcome_title = Text("Treatment Outcomes", font_size=20)
        outcome_title.move_to(DOWN * 3.2 + LEFT * 4)

        # Bar chart for outcomes
        outcomes = VGroup()
        response_rates = [0.85, 0.72, 0.68]

        for i, (rate, color) in enumerate(zip(response_rates, cluster_colors)):
            bar = Rectangle(width=0.4, height=rate * 1.5)
            bar.set_fill(color, opacity=0.7)
            bar.set_stroke(WHITE, width=1)
            bar.move_to(DOWN * 3 + LEFT * (2.5 - i * 0.6) + UP * rate * 0.75)

            percent = Text(f"{int(rate*100)}%", font_size=10)
            percent.next_to(bar, UP, buff=0.05)

            outcomes.add(VGroup(bar, percent))

        self.play(Write(outcome_title))
        self.play(LaggedStart(*[GrowFromEdge(o[0], DOWN) for o in outcomes], lag_ratio=0.1))
        self.play(*[Write(o[1]) for o in outcomes])
        self.wait(2)


# Run instructions
if __name__ == "__main__":
    print("""
    Multi-omics Visualization Scenes
    ================================

    Available scenes:
    - GenomicsScene: DNA structure and genetic variations
    - EpigenomicsScene: DNA methylation and histone modifications
    - TranscriptomicsScene: RNA expression analysis
    - ProteomicsScene: Protein structure and interactions
    - MetabolomicsScene: Metabolic pathways and small molecules
    - MultiomicsOverview: Comprehensive integration overview
    - DataIntegrationMath: Mathematical foundations
    - ClinicalApplications: Clinical use cases

    Run with:
    manimgl multiomics_visualization.py <SceneName>

    Examples:
    manimgl multiomics_visualization.py MultiomicsOverview
    manimgl multiomics_visualization.py GenomicsScene
    manimgl multiomics_visualization.py DataIntegrationMath
    """)
