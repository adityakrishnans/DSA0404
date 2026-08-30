import { useState, useEffect } from 'react';
import { fetchApi } from '../../api';

interface InningsEntry {
  score: number;
  status: 'century' | 'fifty' | 'duck' | 'normal' | 'notOut';
  balls: number;
  opponent: string;
}

interface TrajectoryPoint {
  inning: number;
  average: number;
}

interface VenueSplitRow {
  condition: string;
  inns: number;
  runs: number;
  avg: number;
}

interface InningsSplitRow {
  innings: string;
  inns: number;
  runs: number;
  avg: number;
}

interface PlayerProfileData {
  name: string;
  team: string;
  role: string;
  profileId: string;
  batting: {
    Matches?: number;
    Innings?: number;
    Runs?: number;
    Average?: number;
    Highest?: number;
    '100s'?: number;
    '50s'?: number;
    Strike_Rate?: number;
  };
  bowling: {
    Matches?: number;
    Innings?: number;
    Wickets?: number;
    Average?: number;
    Economy?: number;
    Best_Figures?: string;
  };
  innings: InningsEntry[];
  trajectory: TrajectoryPoint[];
  venueSplit: VenueSplitRow[];
  inningsSplit: InningsSplitRow[];
}

export default function Dossier() {
  const [players, setPlayers] = useState<string[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<string>('SPD Smith');
  const [playerData, setPlayerData] = useState<PlayerProfileData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchApi<string[]>('/players')
      .then((list) => {
        setPlayers(list);
        if (list.length > 0 && !list.includes(selectedPlayer)) {
          setSelectedPlayer(list[0]);
        }
      })
      .catch((err) => console.error('Failed to load players', err));
  }, []);

  useEffect(() => {
    if (!selectedPlayer) return;
    setLoading(true);
    fetchApi<PlayerProfileData>('/player/' + encodeURIComponent(selectedPlayer))
      .then((data) => {
        setPlayerData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load player profile', err);
        setLoading(false);
      });
  }, [selectedPlayer]);

  const batting = playerData?.batting || {};
  const innings = playerData?.innings || [];
  const trajectory = playerData?.trajectory || [];
  const venueSplit = playerData?.venueSplit || [];
  const inningsSplit = playerData?.inningsSplit || [];

  return (
    <div className="h-full flex flex-col">
      <header className="flex justify-between items-end mb-8 border-b border-[#1AA1B]/10 pb-6">
        <div className="flex items-center gap-6">
          <div>
            <h2 className="text-4xl font-serif text-[#1E392A]">{playerData?.name || selectedPlayer}</h2>
            <div className="flex gap-4 mt-3 text-[11px] uppercase tracking-widest opacity-70">
              <span>{playerData?.role || 'Top Order Batter'}</span>
              <span>|</span>
              <span>{playerData?.team || 'International'}</span>
            </div>
          </div>
          <div className="ml-4">
            <select
              value={selectedPlayer}
              onChange={(e) => setSelectedPlayer(e.target.value)}
              className="bg-[#F7F4E9] border border-[#E5E1D1] text-[#1E392A] text-xs font-mono px-3 py-2 rounded focus:outline-none focus:border-[#1E392A]">
              {players.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="text-right">
          <span className="block text-[10px] uppercase tracking-[0.2em] font-bold text-[#D4AF37]">Profile ID</span>
          <span className="font-mono text-sm">{playerData?.profileId || 'PLY-INT-001'}</span>
        </div>
      </header>

      {loading ? (
        <div className="flex-1 flex items-center justify-between font-mono text-xs text-[#1E392A] opacity-60 animate-pulse">
          FETCHING_PLAYER_FORENSICS...
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6 flex-1 overflow-y-auto pb-8">
          <div className="col-span-4 bg-[#1A1ABW] text-[#BDFCF0] p-6 border border-[#1A1A1B] flex flex-col justify-between shadow-[inset_0_0_20px_rgba(0,0,0,0.5)]">
            <div className="flex justify-between items-center mb-8">
              <span className="text-[10px] uppercase tracking-widest text-[#D4AF37]">Career Ledger (Fact Table)</span>
              <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse" title="Active Record"></span>
            </div>
            
            <div className="grid grid-cols-2 gap-y-8 gap-x-4">
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Matches</div>
                <div className="font-mono text-3xl">{batting.Matches || 0}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Innings</div>
                <div className="font-mono text-3xl">{batting.Innings || 0}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Runs</div>
                <div className="font-mono text-3xl text-[#D4AF37]">{batting.Runs?.toLocaleString() || 0}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Average</div>
                <div className="font-mono text-3xl">{batting.Average || '0.00'}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Centuries (100s)</div>
                <div className="font-mono text-3xl">{batting['100s'] || 0}</div>
              </div>
              <div>
                <div className="text-[10px] uppercase opacity-50 mb-1">Highest Score</div>
                <div className="font-mono text-3xl">{batting.Highest || 0}</div>
              </div>
            </div>
          </div>

          <div className="col-span-8 flex flex-col gap-6">
            <div className="bg-white p-6 border border-[#E5E1D1] shadow-sm">
              <div className="flex justify-between items-end mb-6">
                <span className="text-[10px] uppercase tracking-widest font-bold opacity-60">Innings Form Array (Recorded Innings)</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {innings.length === 0 ? (
                  <span className="font-mono text-xs opacity-50">No batting innings recorded</span>
                ) : (
                  innings.map((inn, idx) => {
                    let blockClass = "bg-gray-200 text-[#1A1ABW]";
                    if (inn.status === 'century') blockClass = "bg-[#D4AF37] text-[#1A1A1B] font-bold";
                    else if (inn.status === 'fifty') blockClass = "bg-[#1E392A] text-white";
                    else if (inn.status === 'duck') blockClass = "border border-red-800 text-red-800 bg-red-50";

                    return (
                      <div 
                        key={idx} 
                        className={`w-10 h-10 flex items-center justify-center text-[11px] font-mono ${blockClass}`}
                        title={`vs ${inn.opponent} (${inn.balls} balls)`}
                      >
                        {inn.score}
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            <div className="bg-[#F7F4E9] p-6 border border-[#E5E1D1] flex-1 flex flex-col">
              <div className="flex justify-between items-end mb-6">
                <span className="text-[10px] uppercase tracking-widest font-bold text-[#1E392A]">Career Average Trajectory</span>
                <span className="font-mono text-xs opacity-50">{innings.length} Innings Progression</span>
              </div>
              <div className="flex-1 w-full relative min-h-[140px]">
                <svg viewBox="0 0 1000 200" preserveAspectRatio="none" className="w-full h-full overflow-visible">
                  <defs>
                    <linearGradient id="goldGradient" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.3"/>
                      <stop offset="100%" stopColor="#D4AF37" stopOpacity="0"/>
                    </linearGradient>
                  </defs>
                  <line x1="0" y1="100" x2="1000" y2="100" stroke="#1AA1B" strokeOpacity="0.2" strokeDasharray="4 4" />
                  <text x="0" y="95" fontSize="12" fill="#1A1A1B" opacity="0.5" fontFamily="monospace">Avg: {batting.Average || '0.0'}</text>
                  
                  {trajectory.length > 1 ? (
                    <>
                      <path 
                        d={trajectory.reduce((acc, pt, idx) => {
                          const x = (idx / (trajectory.length - 1)) * 1000;
                          const y = Math.max(20, Math.min(180, 200 - (pt.average * 2)));
                          return `${acc} ${idx === 0 ? 'M' : 'L'}${x},${y}`;
                        }, "") + ` L1000,200 L0,200 Z`} 
                        fill="url(#goldGradient)" 
                      />
                      <path 
                        d={trajectory.reduce((acc, pt, idx) => {
                          const x = (idx / (trajectory.length - 1)) * 1000;
                          const y = Math.max(20, Math.min(180, 200 - (pt.average * 2)));
                          return `${acc} ${idx === 0 ? 'M' : 'L'}${x},${y}`;
                        }, "")} 
                        fill="none" 
                        stroke="#D4AF37" 
                        strokeWidth="3" 
                      />
                    </>
                  ) : (
                    <line x1="0" y1="100" x2="1000" y2="100" stroke="#D4AF37" strokeWidth="3" />
                  )}
                </svg>
              </div>
            </div>
          </div>

          <div className="col-span-12 bg-white border border-[#E5E1D1] shadow-sm">
            <div className="bg-[#1E392A] text-white px-6 py-3 text-[10px] uppercase tracking-widest font-bold">
              Performance Split Matrix
            </div>
            <div className="grid grid-cols-2 divide-x divide-[#E5E1D1]">
              <div className="p-6">
                <h4 className="text-[10px] uppercase tracking-widest opacity-50 mb-4 border-b border-[#E5E1D1] pb-2">Venue Split</h4>
                <table className="w-full text-sm text-left">
                  <thead>
                    <tr className="opacity-40 font-mono text-[10px]">
                      <th className="font-normal pb-2">Venue</th>
                      <th className="font-normal pb-2">Inns</th>
                      <th className="font-mormal pb-2">Runs</th>
                      <th className="font-normal pb-2 text-right">Avg</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono divide-y divide-[#E5E1D1]/50">
                    {venueSplit.map((v, i) => (
                      <tr key={i}>
                        <td className="py-2 font-sans font-medium uppercase text-xs truncate max-w-[200px]">{v.condition}</td>
                        <td className="py-2">{v.inns}</td>
                        <td className="py-2">{v.runs}</td>
                        <td className="py-2 text-right font-bold text-[#1E392A]">{v.avg}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="p-6">
                <h4 className="text-[10px] uppercase tracking-widest opacity-50 mb-4 border-b border-[#E5E1D1] pb-2">Innings Split</h4>
                <table className="w-full text-sm text-left">
                  <thead>
                    <tr className="opacity-40 font-mono text-[10px]">
                      <th className="font-normal pb-2">Innings</th>
                      <th className="font-mormal pb-2">Inns</th>
                      <th className="font-normal pb-2">Runs</th>
                      <th className="font-normal pb-2 text-right">Avg</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono divide-y divide-[#E5E1D1]/50">
                    {inningsSplit.map((inn, i) => (
                      <tr key={i}>
                        <td className="py-2 font-sans font-medium uppercase text-xs">{inn.innings}</td>
                        <td className="py-2">{inn.inns}</td>
                        <td className="py-2">{inn.runs}</td>
                        <td className="py-2 text-right font-bold text-[#1E392A]">{inn.avg}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
