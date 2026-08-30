/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dossier from './components/views/Dossier';
import Observatory from './components/views/Observatory';
import PostMortem from './components/views/PostMortem';
import SquadMatrix from './components/views/SquadMatrix';
import { ViewState } from './types';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewState>(ViewState.OBSERVATORY);

  return (
    <div className='flex h-screen w-full bg-[#FDFCF0] text-[#1A1A1B] font-sans overflow-hidden'>
      <Sidebar currentView={currentView} setView={setCurrentView} />
      
      <main className='flex-1 flex flex-col p-8 bg-[#FDFCF0] overflow-hidden relative'>
        {/* Subtle noise/texture overlay mimicking old paper/canvas - optional but adds to the metaphor */}
        <div className="absolute inset-0 opacity-[0.02] pointer-events-none mix-blend-multiply" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }}></div>
        
        {currentView === ViewState.OBSERVATORY && <Observatory />}
        {currentView === ViewState.DOSSIER && <Dossier />}
        {currentView === ViewState.SQUAD && <SquadMatrix />}
        {currentView === ViewState.POST_MORTEM && <PostMortem />}
      </main>
    </div>
  );
}

