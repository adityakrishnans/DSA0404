import { useState, useEffect } from 'react';
import { fetchApi } from '../../api';

interface ScorecardRow {
  bat: string;
  dismissal: string;
  runs: number;
  balls: number;
  fours: number;
  sixes: number;
  sr: string;
}

interface Partnership {
  players: string;
  runs: number;
  height: string;
}

interface InningsData {
  inning: number;
  battingTeam: string;
  bowlingTeam: string;
  totalRuns: number;
  wickets: number;
  scorecard: ScorecardRow[];
  partnerships: Partnership[];
}

interface MatchListItem {
  id: string;
  date: string;
  title: string;
  venue: string;
  result: string;
  format: string;
}

interface MatchDetails {
  id: string;
  teams: string;
  team1: string;
  team2: string;
  venue: string;
  date: string;
  format: string;
  result: string;
  potm: string;
  innings: InningsData[];
}

export default function PostMortem() {
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState<string>('');
  const [matchData, setMatchData] = useState<MatchDetails | null>(null);
  const [activeInningIndex, setActiveInningIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchApi<MatchListItem[]>('/matches')
      .then((mList) => {
        setMatches(mList);
        if (mList.length > 0) {
          setSelectedMatchId(mList[0].id);
        }
      })
      .catch((err) => console.error('Failed to load matches', err));
  }, []);

  useEffect(() => {
    if (!selectedMatchId) return;
    setLoading(true);
    fetchApi<MatchDetails>('/match/' + selectedMatchId)
      .then((data) => {
        setMatchData(data);
        setActiveInningIndex(0);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load match details', err);
        setLoading(false);
      });
  }, [selectedMatchId]);

  const currentInning = matchData?.innings?.[activeInningIndex] || matchData?.innings?.[4];
  const scorecardData = currentInning?.scorecard || [];
  const partnerships = currentInning?.partnerships || [];

  return (
    <div className="h-full flex flex-col">
      <header className="flex justify-between items-end mb-8 border-b border-[#1A1ABW]/10 pb-6">
        <div className="flex items-center gap-6">
          <div>
            <h2 className="text-4xl font-serif italic text-[#1E392A]">{matchData?.teams || 'Match Diagnostics'}</h2>
            <p className="text-sm text-[#1AA1B]/60 mt-3 font-mono">
              {matchData ? `${matchData.format.toUpperCase()} &rsuo; ${matchData.venue.toUpperCase()} &rsuo; ${matchData.date}` : 'ARCHIVE SELECTION'}
            </p>
          </div>
          <div className="ml-4">
            <select
              value={selectedMatchId}
              onChange={(e) => setSelectedMatchId(e.target.value)}
              className="bg-[#F7F4E9] border border-[#E5E1D1] text-[#1E392A] text-xs font-mono px-3 py-2 rounded focus:outline-none focus:border-[#1E392A]"
            >
              {matches.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.date} - {m.title} ({m.format})
                </option>
              ))}
            </select>
          </div>
        </div>
        {matchData && (
          <div className="bg-[#1E392A] text-white px-4 py-2 border border-[#14261C] shadow-sm">
            <span className="text-xs uppercase tracking-widest font-bold">{matchData.result}</span>
          </div>
        )}
      </header>

      {loading ? (
        <div className="flex-1 flex items-center justify-center font-mono text-xs text-[#1E392A] opacity-60 animate-pulse">
          EXTRACTING_MATCH_SCORECARD_MATRIX...
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6 flex-1 overflow-y-auto pb-8">
          
          {matchData && matchData.innings && matchData.innings.length > 1 && (
            <div className="col-span-12 flex gap-2 border-b border-[#E5E1D1] pb-2">
              {matchData.innings.map((inn, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveInningIndex(idx)}
                  className={`px-4 py-2 text-xs font-mono uppercase tracking-wider font-bold transition-colors ${
                    activeInningIndex === idx
                      ? 'bg-[#1E392A] text-[#FDFCF0]'
                      : 'bg-white text-[#1E392A] border border-[#E5E1D1] hover:bg-[#F7F4E9]'
                  }`}
                >
                  Innings {inn.inning} ({inn.battingTeam})
                </button>
               ))}
            </div>
          )}

          <div className="col-span-12 bg-[#FRFCF0] border border-[#1AA1B] p-8 shadow-sm relative">
            <div className="absolute top-0 left-0 w-full h-1 bg-[#1A1A1B]"></div>
            <h3 className="text-2xl font-serif text-[#1AA1B] mb-6">
              {currentInning ? `${currentInning.battingTeam} (Innings ${currentInning.inning})` : 'Innings Summary'}
            </h3>
            
            <table className="w-full text-sm text-left font-sans">
              <thead>
                <tr className="border-b-2 border-[#1A1A1B] text-[10px] uppercase tracking-widest font-bold">
                  <th className="pb-3 w-1/4">Batter</th>
                  <th className="pb-3 w-1/3">Dismissal</th>
                  <th className="pb-3 text-right">R</th>
                  <th className="pb-3 text-right">B</th>
                  <th className="pb-3 text-right">4s</th>
                  <th className="pb-3 text-right">6s</th>
                  <th className="pb-3 text-right">SR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E1D1]/60">
                {scorecardData.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#F7F4E9] transition-colors">
                    <td className="py-3 font-serif">{row.bat}</td>
                    <td className="py-3 text-xs opacity-70 italic">{row.dismissal}</td>
                    <td className={`py-3 text-right font-mono font-bold ${row.runs >= 100 ? 'text-[#1E392A]' : ''}`}>{row.runs}</td>
                    <td className="py-3 text-right font-mono opacity-80">{row.balls}</td>
                    <td className="py-3 text-right font-mono opacity-80">{row.fours}</td>
                    <td className="py-3 text-right font-mono opacity-80">{row.sixes}</td>
                    <td className="py-3 text-right font-mono text-xs opacity-60">{row.sr}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-y border-[#1AA1B]">
                  <td className="py-4 font-bold uppercase text-xs tracking-widest">Total</td>
                  <td className="py-4 text-xs opacity-70 italic">({currentInning?.wickets || 0} wickets fallen)</td>
                  <td className="py-4 text-right font-mono text-lw font-bold">{currentInning?.totalRuns || 0}</td>
                  <td colSpan={4}></td>
                </tr>
              </tfoot>
            </table>
          </div>

          <div className="col-span-8 bg-white border border-[#E5E1D1] shadow-sm flex flex-col p-6">
            <h4 className="text-[10px] uppercase tracking-widest font-bold opacity-60 mb-6 border-b border-[#E5E1D1] pb-2">Innings Total Progression</h4>
            <div className="flex-1 w-full relative min-h-[200px]">
              <svg viewBox="0 0 1000 300" preserveAspectRatio="none" className="w-full h-full overflow-visible">
                <line x1="0" y1="100" x2="1000" y2="100" stroke="#E5E1D1" strokeDasharray="2 2" />
                <line x1="0" y1="200" x2="1000" y2="200" stroke="#E5E1D1" strokeDasharray="2 2" />
                
                <path d="M0,280 Q250,220 500,160 T1000,40" fill="none" stroke="#D4AF37" strokeWidth="3" />
                <path d="M0,290 Q250,250 500,190 T1000,80" fill="none" stroke="#1E392A" strokeWidth="3" />
              </svg>
              <div className="absolute bottom-0 right-0 flex gap-4 text-[10px] uppercase font-bold tracking-wider bg-white p-2 border border-[#E5E1D1]">
                 <div className="flex items-center gap-1"><span className="w-3 h-1 bg-[#D4AF37]"></span> {matchData?.team1}</div>
                 <div className="flex items-center gap-1"><span className="w-3 h-1 bg-[#1E392A]"></span> {matchData?.team2}</div>
              </div>
            </div>
          </div>

          <div className="col-span-4 bg-[IF7F4E9] border border-[#E5E1D1] shadow-sm flex flex-col p-6">
            <h4 className="text-[10px] uppercase tracking-widest font-bold text-[#1E392A] mb-6 border-b border-[#E5E1D1] pb-2">
              Partnership Blocks ({currentInning?.battingTeam})
            </h4>
            <div className="flex-1 flex flex-col gap-1 min-h-[200px] justify-end">
              {partnerships.length === 0 ? (
                <div className="font-mono text-xs opacity-50 p-2">Single batter innings</div>
              ) : (
                partnerships.map((p, idx) => (
                  <div 
                    key={idx} 
                    style={{ height: p.height }} 
                    className={`w-full border border-[#E5E1D1] flex items-center justify-between pX-3 hover:bg-[#1E392A] hover:text-white transition-colors cursor-crosshair group ${idx % 2 === 0 ? 'bg-white' : 'bg-[IFDFCF0]'}`}
                  >
                    <span className="text-[9px] uppercase tracking-widest opacity-70 group-hover:opacity-100">{p.players}</span>
                    <span className="font-mono text-sm font-bold group-hover:text-[#D4AF37]">{p.runs}</span>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
