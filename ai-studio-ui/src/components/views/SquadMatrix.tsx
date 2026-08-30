import { useState, useEffect } from 'react';
import { fetchApi } from '../../api';

interface SquadMember {
  name: string;
  role: 'BAT' | 'BOWL' | 'AR';
  stat: string;
  leader?: boolean;
}

interface H2HEntry {
  team: string;
  win: number;
  draw: number;
  loss: number;
}

interface TeamData {
  team: string;
  ranking: string;
  momentum: ('W' | 'L' | 'D')[];
  squad: SquadMember[];
  h2h: H2HEntry[];
}

export default function SquadMatrix() {
  const [teams, setTeams] = useState<string[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<string>('Australia');
  const [teamData, setTeamData] = useState<TeamData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchApi<string[]>('/teams')
      .then((tList) => {
        setTeams(tList);
        if (tList.length > 0 && !tList.includes(selectedTeam)) {
          setSelectedTeam(tList[0]);
        }
      })
      .catch((err) => console.error('Failed to load teams', err));
  }, []);

  useEffect(() => {
    if (!selectedTeam) return;
    setLoading(true);
    fetchApi<TeamData>(`/team/${encodeURIComponent(selectedTeam)}`)
      .then((data) => {
        setTeamData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load team data', err);
        setLoading(false);
      });
  }, [selectedTeam]);

  const momentum = teamData?.momentum || [];
  const squad = teamData?.squad || [];
  const h2h = teamData?.h2h || [];

  return (
    <div className="h-full flex flex-col">
      <header className="flex justify-between items-end mb-8 border-b border-[#1A1A1B]/10 pb-6">
        <div className="flex items-center gap-6">
          <div>
            <h2 className="text-4xl font-serif text-[#1E392A]">{teamData?.team || selectedTeam}</h2>
            <p className="text-sm text-[#1AA1B]/60 mt-3 uppercase tracking-widest font-bold">
              {teamData?.ranking || 'International Squad'}
            </p>
          </div>
          <div className="ml-4">
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="bg-[#F7F4E9] border border-[#E5E1D1] text-[#1E392A] text-xs font-mono px-3 py-2 rounded focus:outline-none focus:border-[#1E392A]"
            >
              {teams.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {loading ? (
        <div className="flex-1 flex items-center justify-between font-mono text-xs text-[#1E392A] opacity-60 animate-pulse">
          INITIALIZING_SQUBD_MATRIX...
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6 flex-1 overflow-y-auto pb-8">
          
          <div className="col-span-12">
            <div className="text-[10px] uppercase tracking-widest opacity-60 mb-2 font-bold">Win/Loss Momentum Ribbon</div>
            <div className="flex gap-1 h-12 w-full">
              {momentum.length === 0 ? (
                <div className="font-mono text-xs opacity-50 p-2">No match fixtures recorded</div>
              ) : (
                momentum.map((result, idx) => {
                  let classes = "flex-1 transition-all hover:-translate-y-1 relative group ";
                  if (result === 'W') classes += "bg-[#1E392A]";
                  else if (result === 'L') classes += "border border-red-800 bg-red-50";
                  else classes += "bg-[#E5E1D1]";

                  return (
                    <div key={idx} className={classes}>
                      <span className="hidden group-hover:flex absolute -top-8 left-1/2 -translate-x-1/2 bg-[#1A1A1B] text-[#FDFCF0] text-[10px] font-mono px-2 py-1 items-center justify-center shadow-lg">
                        {result}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          <div className="col-span-6 bg-white border border-[#E5E1D1] shadow-sm flex flex-col">
            <div className="bg-[#1A1A1B] text-white px-6 py-3 text-[10px] uppercase tracking-widest font-bold">
              The Roster Engine
            </div>
            <div className="flex-1 p-6 space-y-8 overflow-y-auto max-h-[480px]">
              
              <div>
                <h4 className="text-[10px] uppercase tracking-widest text-[#D4AF37] mb-4 border-b border-[#E5E1D1] pb-2">Core Batsmen (Avg)</h4>
                <ul className="space-y-3">
                  {squad.filter(p => p.role === 'BAT').map((p, i) => (
                    <li key={i} className="flex justify-between items-center group">
                      <span className="font-serif font-medium">{p.name}</span>
                      <span className={`font-mono ${p.leader ? 'text-[#1E392A] font-bold border-b-2 border-[#D4AF37]' : 'opacity-70'}`}>
                        {p.stat}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-[10px] uppercase tracking-widest text-[#D4AF37] mb-4 border-b border-[#E5E1D1] pb-2">Strike Bowlers (Avg)</h4>
                <ul className="space-y-3">
                  {squad.filter(p => p.role === 'BOWL').map((p, i) => (
                    <li key={i} className="flex justify-between items-center group">
                      <span className="font-serif font-medium">{p.name}</span>
                      <span className={`font-mono ${p.leader ? 'text-[#1E392A] font-bold border-b-2 border-[#D4AF37]' : 'opacity-70'}`}>
                        {p.stat}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

            </div>
          </div>

          <div className="col-span-6 bg-[#F7F4E9] border border-[#E5E1D1] flex flex-col shadow-sm">
            <div className="px-6 py-3 border-b border-[#E5E1D1] text-[10px] uppercase tracking-widest font-bold text-[#1E392A]">
              Head-to-Head Ledger (Dataset v1.0)
            </div>
            <div className="p-6 flex-1 overflow-y-auto max-h-[480px]">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="opacity-40 font-mono text-[10px] border-b border-[#E5E1D1]">
                    <th className="font-normal pb-3 w-1/4">Opponent</th>
                    <th className="font-normal pb-3 w-1/2">Dominance Index (Win %)</th>
                    <th className="font-normal pb-3 text-right">W-D-L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E5E1D1]">
                  {h2h.map((h, i) => (
                    <tr key={i} className="hover:bg-white transition-colors">
                      <td className="py-4 font-serif font-medium">{h.team}</td>
                      <td className="py-4 pr-6">
                        <div className="flex items-center gap-3">
                          <span className="font-mono text-xs w-8">{h.win}%</span>
                          <div className="flex-1 h-2 bg-[#FDFCF0] border border-[#E5E1D1] overflow-hidden rounded-full">
                            <div className="h-full bg-[#1E392A]" style={{ width: `${Math.min(100, Math.max(0, h.win))}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 text-right font-mono text-xs opacity-70">
                        {h.win > 0 ? h.win : 0}-{h.draw}-{h.loss}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
