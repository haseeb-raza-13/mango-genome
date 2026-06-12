export default function Work() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Mango Genome Database</h1>

      {[
        {
          title: "Objective and Purpose",
          body: `To create the first website particularly for Mango Genome and the first-ever Pakistani website which
will provide the scientific community and general public with bioinformatics resources related to Mango genomic
sequence information and bioinformatics tools for retrieval and analysis of genomic sequences of different Mango
cultivars (varieties).`,
        },
        {
          title: "Relevant Background Information",
          body: `Mango, being the most important subtropical/tropical fruit crop, stands at the fifth position worldwide
with major production in India and South-East Asia. Due to difficulties in fertilization, mango cultivation still
relies mainly on natural selection rather than hybridization and evaluation. Recently, mango genomics has become
a worldwide interest to generate tools for Marker Assisted Selection and trait association. Although large data on
the Mango Genome have been reported by many countries since 2014, no dedicated platform was established
specifically for mango to make this valuable data available to the scientific community.`,
        },
        {
          title: "Scope of the Work",
          body: `Fruit Science is an important sector of agriculture. With the growing population, demand for fruits is
gradually increasing. One of the major challenges in many fruit species is the lack of well-defined genetic
studies. This website contains analyzed information of Mango Genome datasets of different cultivars and consists
of many useful tools that provide accurate and useful results for research, academic work, development, analysis,
and other biological needs.`,
        },
        {
          title: "Timeline",
          body: "The whole project was developed within one year, including planning, analysis, development, and testing.",
        },
      ].map(({ title, body }) => (
        <section key={title}>
          <h2 className="text-base font-semibold text-accent mb-2">{title}</h2>
          <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">{body}</p>
        </section>
      ))}

      <section>
        <h2 className="text-base font-semibold text-accent mb-3">Experience and Qualifications</h2>
        <ul className="space-y-2 text-sm text-slate-300">
          <li><strong className="text-white">Expert:</strong> Dr. Kamran Azim — Professor, Dean (Faculty of Life Sciences), HOD (Biosciences)</li>
          <li><strong className="text-white">Senior:</strong> Dr. Uzma Mehmood — Assistant Professor, HOD (Bioinformatics)</li>
          <li><strong className="text-white">Senior:</strong> Ms. Rabia Faizan — Lecturer, Bioinformatics</li>
        </ul>
      </section>
    </div>
  );
}
