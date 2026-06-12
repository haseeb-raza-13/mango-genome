export default function Literature() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Literature</h1>

      {[
        {
          title: "About Mango",
          body: `Mango is known as the "The king of the fruits," because it is nutritionally rich with unique flavor, taste,
health-promoting qualities and aroma making it superior among new functional foods, often labeled as "super fruits".
This exotic fruit belongs to the family of Anacardiaceae — a family that also includes numerous species of tropical
fruiting trees in the flowering plants such as cashew, pistachio.`,
        },
        {
          title: "Mango Aroma",
          body: `Aroma is a complex mixture of a large number of volatile compounds, whose composition is specific to species
and often to the variety of fruit. The most important aroma compounds include amino acid-derived compounds, lipid-derived
compounds, phenolic derivatives, and mono- and sesquiterpenes. Mango (Mangifera indica L.) possesses a very attractive
flavor characteristic. More than 270 aroma volatile compounds in different mango varieties have been identified in free
form. Monoterpenes are the most important compounds contributing to mango flavor.`,
        },
        {
          title: "Aroma Compounds",
          body: `Mango aroma is mainly formed by a complex mixture of compounds, but some authors consider terpenes, especially
δ-3-carene, as the most important aroma constituents. The terpene hydrocarbons are considered to be important contributors
to the flavour of Florida, Brazilian and Venezuelan mango varieties. The hydrocarbons (Z)- and (E)-β-ocimene have a warm,
herbaceous, and floral odor, whereas the odor of δ-3-carene was sweet, reminiscent of refined limonene.`,
        },
        {
          title: "Mango Flavor",
          body: `Flavor volatiles are derived from an array of compounds including phytonutrients such as fatty acids, amino acids,
carotenoids, phenols and terpenoids. Fruit volatile compounds are mainly comprised of diverse classes of chemicals, including
esters, alcohols, aldehydes, ketones, lactones, and terpenoids. Volatile terpenoid compounds, potentially derived from
carotenoids, are important components of flavor and aroma in many fruits.`,
        },
        {
          title: "Flavor Compounds",
          body: `Mango (Mangifera indica L.) possesses a very attractive flavor characteristic. More than 270 aroma volatile
compounds in different mango varieties have been identified in free form. Monoterpenes such as α-pinene, myrcene,
α-phelladrene, σ-3-carene, p-cymene, limonene and terpinolene, esters including ethyl-2-methyl propanoate, ethyl butanoate,
as well as (E,Z)-2,6-nonadienal, (E)-2-nonenal, methyl benzoate, (E)-β-ionone, decanal, and
2,5-dimethyl-4-methoxy-3(2H)-furanone are the most important compounds contributing to mango flavor.`,
        },
      ].map(({ title, body }) => (
        <section key={title}>
          <h2 className="text-base font-semibold text-accent mb-2">{title}</h2>
          <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">{body}</p>
        </section>
      ))}

      <section>
        <h2 className="text-base font-semibold text-accent mb-3">References</h2>
        <ul className="space-y-2 text-xs text-slate-400 list-disc list-inside">
          <li>Muna Ahmed Mohamed El Hadi et al. (2013). Advances in Fruit Aroma Volatile Research. <em>Molecules</em>, 18, 8200–8229.</li>
          <li>Pino, J. A., Mesa, J., Munoz, Y., et al. (2005). Volatile components from mango cultivars. <em>J Agric Food Chem</em>, 53(6), 2213–2223.</li>
          <li>T.M.M. Malundo et al. (2001). Sugars and Acids Influence Flavor Properties of Mango. <em>J Am Soc Hortic Sci</em>, 126(1), 115–121.</li>
          <li>Clara E. Quijano et al. (2007). Aroma volatile constituents of Colombian varieties of mango. <em>Flavour and Fragrance</em>, 22, 401–406.</li>
          <li>Jorge A. Pino et al. (2005). Volatile Components from Mango Cultivars. <em>J Agric Food Chem</em>, 53(6), 2213–2223.</li>
        </ul>
      </section>
    </div>
  );
}
