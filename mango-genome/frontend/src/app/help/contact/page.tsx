import { Mail, Phone, MapPin } from "lucide-react";

export default function ContactUs() {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Contact Us</h1>

      <div className="card space-y-4">
        <h2 className="text-base font-semibold text-accent">Department of Bioinformatics</h2>
        <div className="space-y-3 text-sm text-slate-300">
          <div className="flex items-start gap-3">
            <MapPin size={15} className="text-slate-500 mt-0.5 flex-shrink-0" />
            <span>
              Sir Syed University of Engineering &amp; Technology,<br />
              University Road, Karachi-75300, Pakistan
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Mail size={15} className="text-slate-500 flex-shrink-0" />
            <a href="mailto:qamartayyaba@yahoo.com" className="text-accent hover:underline">
              qamartayyaba@yahoo.com
            </a>
          </div>
          <div className="flex items-center gap-3">
            <Phone size={15} className="text-slate-500 flex-shrink-0" />
            <span>+92 336 2808926</span>
          </div>
        </div>
      </div>

      <div className="card space-y-3 border-accent/20">
        <h2 className="text-base font-semibold text-accent">Developed by BioInfoQuant</h2>
        <div className="space-y-2 text-sm text-slate-300">
          <div className="flex items-center gap-3">
            <Mail size={15} className="text-slate-500 flex-shrink-0" />
            <a href="mailto:contact@bioinfoquant.com" className="text-accent hover:underline">
              contact@bioinfoquant.com
            </a>
          </div>
          <div className="flex items-center gap-3">
            <Phone size={15} className="text-slate-500 flex-shrink-0" />
            <span>+92 339 4116531</span>
          </div>
        </div>
      </div>
    </div>
  );
}
