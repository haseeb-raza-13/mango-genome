export default function AppFooter() {
  return (
    <footer className="border-t border-[#1e3054] py-4 mt-auto">
      <p className="text-center text-xs text-slate-500">
        Developed by{" "}
        <a
          href="https://www.bioinfoquant.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-accent hover:underline"
        >
          BioInfoQuant
        </a>
        {" "}·{" "}
        Department of Bioinformatics, SSUET, Karachi
      </p>
    </footer>
  );
}
