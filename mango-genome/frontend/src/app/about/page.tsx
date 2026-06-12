import Image from "next/image";

export default function AboutProject() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Mango Genome Database and Big Data Analysis Tool</h1>

      <section className="prose-sm text-slate-300 space-y-4 leading-relaxed">
        <p>
          Mango is the fifth most important subtropical/tropical fruit crop worldwide with production centered in
          India and South East Asia. Due to the difficulty of specific pollination, mango breeding is still
          predominantly the selection of trees with superior fruit traits rather than hybrid production and
          evaluation. Recently, there has been a worldwide interest in mango genomics to produce tools for Marker
          Assisted Selection and trait association. There are five transcriptomes produced respectively in Israel,
          India, Mexico, Pakistan and the US.
        </p>
        <p>
          Our project <strong className="text-accent">Mango Genome Database</strong> is constructed upon the
          completion of the Pakistan mango leaf transcriptome and chloroplast genome sequencing with the aim of
          providing the scientific community with accurate data and annotation of the mango genome sequence. Mango
          Genome Database contains annotated data including unigene of whole genome sequence of specie{" "}
          <em>Mangifera indica</em> L. (mango).
        </p>
        <p>
          The annotated sequence data can be browsed through the Gene Search page or queried using various
          categories in the search sites. The whole genome sequences can also be accessed and downloaded through
          Genome View. Mango Genome Database also provides online analysis tools such as Blast server for the
          Mango datasets, a sequence or gene search server, and Genome view detection tools.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-white mb-3">Purpose</h2>
        <p className="text-slate-300 text-sm leading-relaxed">
          Fruit Science is one of the important sectors of agriculture. With the growing population, demand for
          fruits is gradually increasing. One of the most important challenges in many fruit species is the
          unavailability of well-defined genetic studies. There is no database available for the Mango genome;
          thus, this particular platform will provide data and information about <em>Mangifera indica</em> L.
          cultivars from different countries and allow users to analyze their own data against our databases.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-white mb-4">
          Mango Genome of <em>Mangifera indica</em> L.
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { src: "/images/s1.jpg", caption: 'Mango (Mangifera indica L.) — "king of fruits" in Pakistan.' },
            { src: "/images/fc.jpg", caption: "Experimental procedure at ICCBS (UoK)." },
            { src: "/images/s3.jpg", caption: "Sir Syed University of Engineering and Technology, Karachi." },
            { src: "/images/s4.jpg", caption: "Mango Genome Database online project 2017." },
          ].map((img) => (
            <figure key={img.src} className="space-y-1.5">
              <div className="relative aspect-[4/3] rounded overflow-hidden border border-[#1e3054]">
                <Image src={img.src} alt={img.caption} fill className="object-cover" />
              </div>
              <figcaption className="text-xs text-slate-500 text-center leading-tight">{img.caption}</figcaption>
            </figure>
          ))}
        </div>
      </section>
    </div>
  );
}
