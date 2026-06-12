export default function UserGuide() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">User Guide</h1>
      <p className="text-slate-400 text-sm">
        Welcome to the <strong className="text-accent">Mango Genome Database</strong> user guide. This guide
        will help you navigate through the application and make the most out of its features.
      </p>

      {[
        {
          title: "BLAST Search",
          href: "/blast",
          steps: [
            "Navigate to the BLAST tab from the sidebar.",
            "Paste your query sequence in FASTA format, or upload a .fasta file.",
            "Select BLAST type: blastn for nucleotide sequences, blastp for protein sequences.",
            "Choose the target database (specific cultivar or combined All Genomes / All Proteomes).",
            "Click Run BLAST to start the search.",
            "View the tabular results — sortable by any column. Download as CSV.",
            "Explore the three alignment statistics plots (% Identity, E-value, Bit Score).",
          ],
        },
        {
          title: "Multiple Sequence Alignment (MSA)",
          href: "/msa",
          steps: [
            "Navigate to the MSA tab.",
            "Paste multiple sequences in multi-FASTA format, or upload multiple .fasta files.",
            "Click Run Alignment.",
            "View the visual alignment (with |, :, space symbols) or the raw aligned FASTA.",
            "Download the aligned FASTA or the plain-text alignment report.",
            "Explore the pairwise identity heatmap, base frequency chart, and dot plots.",
          ],
        },
        {
          title: "Downloads",
          href: "/downloads",
          steps: [
            "Navigate to the Downloads tab.",
            "Click any file link to download the corresponding FASTA dataset.",
            "Files include nucleotide and protein sequences for all five cultivars.",
          ],
        },
      ].map(({ title, href, steps }) => (
        <section key={title} className="card space-y-3">
          <h2 className="text-base font-semibold text-white">
            <a href={href} className="hover:text-accent transition-colors">{title}</a>
          </h2>
          <ol className="list-decimal list-inside space-y-1.5 text-sm text-slate-300">
            {steps.map((s, i) => <li key={i}>{s}</li>)}
          </ol>
        </section>
      ))}

      <section className="card text-sm text-slate-400">
        <p>
          All results from BLAST and MSA tools can be downloaded in CSV or FASTA formats. Plots can be downloaded
          as PNG images for publication. For additional support, visit the{" "}
          <a href="/help/contact" className="text-accent hover:underline">Contact Us</a> page.
        </p>
      </section>
    </div>
  );
}
