import { ViewState } from '../types';

interface SidebarProps {
  currentView: ViewState;
  setView: (view: ViewState) => void;
}

export default function Sidebar({ currentView, setView }: SidebarProps) {
  const navItems = [
    { id: ViewState.OBSERVATORY, num: '01', title: 'The Observatory', desc: 'Global Overview & Form' },
    { id: ViewState.DOSSIER, num: '02', title: 'The Dossier', desc: 'Player Profile & Forensics' },
    { id: ViewState.SQUAD, num: '03', title: 'The Squad Matrix', desc: 'Team Composition & H2H' },
    { id: ViewState.POST_MORTEM, num: '04', title: 'The Post-Mortem', desc: 'Match Analysis & Archives' },
  ];

  return (
    <aside className="w-[280px] bg-[#1E392A] text-[#FDFCF0] p-6 flex flex-col border-r border-[#14261C] shrink-0 h-full overflow-y-auto">
      <div className="mb-12">
        <h1 className="text-xl font-bold tracking-tight uppercase border-b border-[#FDFCF0]/20 pb-4">
          Cricket<br />Research Lab
        </h1>
        <p className="text-[10px] uppercase tracking-[0.2em] mt-3 opacity-60">
          Analytical Workspace
        </p>
      </div>

      <nav className="flex-1 space-y-2">
        <p className="text-[10px] uppercase tracking-[0.2em] mb-6 opacity-40 font-bold px-3">
          Lab Modules
        </p>
        
        <ul className="space-y-2">
          {navItems.map((item) => {
            const isActive = currentView === item.id;
            return (
              <li key={item.id}>
                <button
                  onClick={() => setView(item.id)}
                  className={`w-full text-left p-3 transition-all ${
                    isActive 
                      ? 'bg-[#FDFCF0]/10 border-l-4 border-[#D4AF37]' 
                      : 'border-l-4 border-transparent opacity-50 hover:opacity-100 hover:bg-[#FDFCF0]/5'
                  }`}
                >
                  <span className="block text-[11px] font-mono mb-1 text-[#D4AF37]">{item.num}</span>
                  <span className="block text-xs font-bold uppercase tracking-wider">{item.title}</span>
                  <span className="block text-[10px] opacity-60 italic mt-1">{item.desc}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="mt-auto pt-8 border-t border-[#FDFCF0]/10">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 rounded-full bg-[#D4AF37] animate-pulse"></div>
          <div>
            <span className="block text-[10px] uppercase tracking-widest opacity-60">System Status</span>
            <span className="block text-xs font-mono mt-1">DATA_SYNC_LIVE</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
