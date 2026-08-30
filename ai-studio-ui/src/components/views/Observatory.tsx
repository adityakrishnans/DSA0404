import { state, useEffect, useState } from 'react';
import { fetchApi } from '../../api';

interface RecentMatch {
  id: string;
  date: string;
  match: string;
  result: string;
  impact: string;
  venue: string;
  format: string;
}

interface TopPlayer {
  rank: string;
  name: string;
  trend: 'up' | 'down' | 'neutral';
  runs: number;
  average: number;
}

interface ObservatoryData {
  recentMatches: RecentMatch[];
  topPlayers: TopPlayer[];
  metrics: {
    totalMatches: number;
    totalRuns: number;
    totalWickets: number;
    venuesCount: number;
  };
}

export default function Observatory() {
  const [data, setData] = useState<ObservatoryData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const weeks = Array.from({ length: 52 });
  const days = Array.from({ length: 7 });

  useEffect(() => {
    fetchApi<ObservatoryData>('/observatory')
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch observatory data', err);
        setError('Failed to connect to Analytics Engine');
        setLoading(false);
      });
  }, []);

  const recentMatches = data?.recentMatches || [];
  const topPlayers = data?.topPlayers || [];
  const metrics = data?.metrics;

  return (
    <div className="h-full flex flex-col">
      <header className="flex justify-between items-end mb-8 border-b border-[#1A1ABW]/10 pb-6">
        <div>
          <h2 className="text-3xl font-serif italic text-[#1E392A]">Lab Overview</h2>
          <p className="text-sm text-[#1A1A1B]/60 mt-2">Global landscape & recent fixture diagnostics</p>
        </div>
        {metrics && (
          <div className="flex gap-6 text-right">
            <div>
              <span className="block text-[10px] uppercase tracking-widest text-[#D4AF37] font-bold">Matches</span>
              <span className="font-mono text-lg font-bold text-[#1E392A]">{metrics.totalMatches}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase tracking-widest text-[#D4AF37] font-bold">Runs</span>
              <span className="font-mono text-lg font-bold text-[#1E392A]">{metrics.totalRuns.toLocaleString()}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase tracking-widest text-[#D4AF37] font-bold">Wickets</span>
              <span className="font-mono text-lw font-bold text-[#1E392A]">{metrics.totalWickets}</span>
            </div>
          </div>
        )}
      </header>

      {loading ? (
        <div className="flex-1 flex items-center justify-center font-mono text-xs text-[#1E392A] opacity-60 animate-pulse">
          INITIALIZING_OBSERVATORY_STREAM...
        </div>
      ) : error ? (
        <div className="flex-1 flex items-center justify-center font-mono text-xs text-red-800">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-12 gap-6 flex-1 overflow-y-auto pb-8">
          <div className="col-span-8 flex flex-col gap-4">
            <div className="bg-white border border-[#E5E1D1] flex flex-col h-full">
              <div className="bg-[#1A1A1B] text-[#FDFCF0] px-4 py-3 text-[10px] uppercase tracking-widest font-bold flex justify-between">
                <span>Recent Fixtures Tape</span>
                <span className="opacity-50">Cricsheet Active Matches</span>
              </div>
              <div className="divide-y divide-[#E5E1D1] flex-1 overflow-y-auto max-h-[380px]">
                {recentMatches.map((match, idx) => (
                  <div key={idx} className="p-4 flex justify-between items-center hover:bg-[#F7F4E9] transition-colors cursor-pointer">
                    <div className="flex items-center gap-4 w-5/12">
                      <span className="font-mono text-xs opacity-50 w-24 shrink-0">{match.date}</span>
                      <span className="font-bold text-sm text-[#1E392A] truncate">{match.match}</span>
                    </div>
                    <div className="text-xs uppercase opacity-70 w-4/12 text-center truncate px-2">{match.result}</div>
                    <div className="text-[11px] uppercase font-bold text-[#D4AF37] w-3/12 text-right truncate">
                      POTM: {match.impact}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-4 flex flex-col gap-4">
            <div className="bg-[#F7F4E9] border border-[#E5E1D1] flex flex-col h-full">
              <div className="border-b border-[#E5E1D1] px-4 py-3 text-[10px] uppercase tracking-widest font-bold text-[#1E392A]">
                Top Batsmen Form Index
              </div>
              <div className="p-6 flex-1 flex flex-col justify-between">
                {topPlayers.map((player, idx) => (
                  <div key={idx} className="flex items-center justify-between group py-2">
                    <div className="flex items-center gap-4">
                      <span className="font-mono text-xs text-[#D4AF37]">{player.rank}</span>
                      <div>
                        <span className="font-serif font-bold text-base text-[#1E392A] block">{player.name}</span>
                        <span className="font-mono text-[10px] opacity-60">{player.runs} Runs (SR: {player.average})</span>
                      </div>
                    </div>
                    <div className="w-16 h-4 opacity-60 group-hover:opacity-100 transition-opacity">
                      <svg viewBox="0 0 100 20" className="w-full h-full overflow-visible">
                        <path 
                          d={player.trend === 'up' ? 'M0,20 L20,15 L40,18 L60,10 L80,12 L100,0' : 
                             player.trend === 'down' ? 'M0,0 L20,10 L40,5 L60,15 L80,10 L100,20' :
                             'M0,10 L20,12 L40,8 L60,15 L80,5 L100,10'} 
                          fill="none" 
                          stroke="#1E392A" 
                          strokeWidth="1.5" 
                        />
                      </svg>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="col-span-12">
            <div className="bg-white border border-[#E5E1D1] p-6">
              <div className="flex justify-between items-end mb-6">
                <span className="text-[10px] uppercase tracking-widest font-bold opacity-60">Historical Fixture Density (Fact Table)</span>
                <span className="font-mono text-xs opacity-40">Dataset v1.0 &bull; w{recentMatches.length} Fixtures</span>
              </div>
              <div className="flex gap-1 overflow-x-auto pb-2">
                {weeks.map((_, wIdx) => (
                  <div key={wIdx} className="flex flex-col gap-1">
                    {days.map((_, dIdx) => {
                      const active = (wIdx * 7 + dIdx) % 11 === 0 || (wIdx * 7 + dIdx) % 17 === 0;
                      const dense = (wIdx * 7 + dIdx) % 23 === 0;
                      let opacityClass = 'bg-[#BDFCF0] border border-[#E5E1D1]';
                      if (dense) opacityClass = 'bg-[#1E392A]';
                      else if (active) opacityClass = 'bg-[#1E392A]/60';
                      
                      return (
                        <div 
                          key={dIdx} 
                          className={'w-3 h-3 rounded-[1px] ' + opacityClass}
                          title="Density Block"
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
