// SonicWave UI/Playback wiring and background effects
(function(){
  const $ = (sel, ctx=document) => ctx.querySelector(sel);
  const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

  const audio = $('#audio');
  const npTitle = $('#np-title');
  const npArtist = $('#np-artist');
  const btnPlay = $('#btn-play');
  const btnPrev = $('#btn-prev');
  const btnNext = $('#btn-next');
  const progress = $('#progress');
  const volume = $('#volume');
  const curTime = $('#cur-time');
  const durTime = $('#dur-time');
  const songGrid = $('#song-grid');
  const search = $('#search');
  const recoGrid = $('#reco-grid');

  let currentSong = null;
  let isPlaying = false;

  // Cursor-follow blob
  const cursorBlob = $('#cursor-blob');
  window.addEventListener('pointermove', (e)=>{
    cursorBlob.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
    cursorBlob.style.opacity = 0.45;
  });
  window.addEventListener('pointerleave', ()=>{
    cursorBlob.style.opacity = 0.2;
  });

  // Sidebar nav routing (basic client-side navigation for pages loaded server-side)
  document.querySelectorAll('.menu .menu-item').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const page = btn.dataset.page;
      if (!page) return;
      if (page === 'home') window.location.href = '/';
      if (page === 'library') window.location.href = '/'; // same as home grid for now
      if (page === 'playlists') window.location.href = '/playlists';
      if (page === 'favorites') window.location.href = '/favorites';
      if (page === 'history') window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});
    });
  });

  // Shooting star every ~10s
  const shootingStar = $('#shooting-star');
  setInterval(()=>{
    const y = Math.random()*window.innerHeight*0.6;
    shootingStar.style.top = `${y}px`;
    shootingStar.classList.remove('active');
    void shootingStar.offsetWidth; // reflow
    shootingStar.classList.add('active');
  }, 10000);

  // Onboarding with localStorage
  const onboarding = $('#onboarding');
  const obClose = $('#onboarding-close');
  if (onboarding && localStorage.getItem('nayaraOnboardingSeen') !== 'true') {
    onboarding.classList.remove('hidden');
  }
  obClose?.addEventListener('click', ()=>{
    localStorage.setItem('nayaraOnboardingSeen', 'true');
    onboarding.classList.add('hidden');
  });

  // Helpers
  function fmtTime(sec){
    if (!sec || isNaN(sec)) return '0:00';
    const m = Math.floor(sec/60);
    const s = Math.floor(sec%60).toString().padStart(2,'0');
    return `${m}:${s}`;
  }
  function setActiveCard(id){
    $$('.song-card').forEach(c=>c.classList.toggle('active', Number(c.dataset.id)===id));
  }
  function updateReco(id){
    if (!recoGrid) return;
    fetch(`/api/recommendations/${id}`).then(r=>r.json()).then(list=>{
      recoGrid.innerHTML = '';
      list.slice(0,6).forEach(s=>{
        const el = document.createElement('div');
        el.className = 'song-card';
        el.innerHTML = `
          <div class="thumb gradient"></div>
          <div class="info"><div class="title">${s.title}</div><div class="meta">${s.artist} • ${s.genre} • ${s.year}</div></div>
          <div class="actions"><button class="btn small play" data-id="${s.song_id}">▶</button></div>
        `;
        recoGrid.appendChild(el);
      })
    })
  }

  function playSongById(id){
    fetch(`/api/play/${id}`, {method:'POST'}).then(r=>r.json()).then(data=>{
      currentSong = data.song;
      audio.src = data.audio_url;
      audio.play();
      isPlaying = true;
      btnPlay.textContent = '⏸';
      npTitle.textContent = currentSong.title;
      npArtist.textContent = currentSong.artist || 'Unknown';
      setActiveCard(currentSong.song_id);
      updateReco(currentSong.song_id);
      // Nayara reaction
      const bubble = document.getElementById('nayara-bubble');
      if (bubble) bubble.textContent = `Now playing: ${currentSong.title}`;
    })
  }

  // Favorite toggle handler (works across pages)
  document.addEventListener('click', (e)=>{
    const t = e.target;
    if (t.classList && t.classList.contains('fav')){
      const id = Number(t.dataset.id);
      fetch(`/api/favorites/toggle/${id}`, {method:'POST'}).then(r=>r.json()).then(res=>{
        t.textContent = res.is_favorite ? '💜' : '🤍';
        // If on favorites page, refresh to reflect removal
        if (window.location.pathname.startsWith('/favorites')){
          window.location.reload();
        }
      })
    }
  });

  // Card buttons (play/queue)
  songGrid?.addEventListener('click', (e)=>{
    const t = e.target;
    if (t.classList.contains('play')){
      const id = Number(t.dataset.id);
      playSongById(id);
    }
    if (t.classList.contains('queue')){
      const id = Number(t.dataset.id);
      fetch(`/api/queue/add/${id}`, {method:'POST'});
    }
  });

  // History chips quick play
  $('#history-grid')?.addEventListener('click', (e)=>{
    const t = e.target;
    if (t.classList.contains('song-chip')){
      playSongById(Number(t.dataset.id));
    }
  })

  // Search
  search?.addEventListener('input', (e)=>{
    const q = e.target.value.trim();
    if (!q){
      // reset visibility
      $$('.song-card').forEach(c=>c.style.display='');
      return;
    }
    fetch(`/api/search?query=${encodeURIComponent(q)}`).then(r=>r.json()).then(list=>{
      const ids = new Set(list.map(s=>s.song_id));
      $$('.song-card').forEach(c=>{
        c.style.display = ids.has(Number(c.dataset.id)) ? '' : 'none';
      })
    })
  })

  // Genres filter
  $('#genres')?.addEventListener('click', (e)=>{
    const t = e.target;
    if (t.classList.contains('genre-pill')){
      const g = t.dataset.genre;
      fetch(`/api/genres/${encodeURIComponent(g)}`).then(r=>r.json()).then(list=>{
        const ids = new Set(list.map(s=>s.song_id));
        $$('.song-card').forEach(c=>{
          c.style.display = ids.has(Number(c.dataset.id)) ? '' : 'none';
        })
      })
    }
  })

  // Transport
  btnPlay?.addEventListener('click', ()=>{
    if (!audio.src && $$('.song-card')[0]){
      // Auto-start first
      playSongById(Number($$('.song-card')[0].dataset.id));
      return;
    }
    if (isPlaying){ audio.pause(); btnPlay.textContent = '▶'; isPlaying = false; }
    else { audio.play(); btnPlay.textContent = '⏸'; isPlaying = true; }
  })

  btnNext?.addEventListener('click', ()=>{
    fetch('/api/next', {method:'POST'}).then(r=>r.json()).then(data=>{
      currentSong = data.song; audio.src = data.audio_url; audio.play(); isPlaying = true; btnPlay.textContent = '⏸';
      npTitle.textContent = currentSong.title; npArtist.textContent = currentSong.artist || 'Unknown';
      setActiveCard(currentSong.song_id); updateReco(currentSong.song_id);
    })
  })

  btnPrev?.addEventListener('click', ()=>{
    fetch('/api/prev', {method:'POST'}).then(r=>r.json()).then(data=>{
      currentSong = data.song; audio.src = data.audio_url; audio.play(); isPlaying = true; btnPlay.textContent = '⏸';
      npTitle.textContent = currentSong.title; npArtist.textContent = currentSong.artist || 'Unknown';
      setActiveCard(currentSong.song_id); updateReco(currentSong.song_id);
    })
  })

  // Timeline & volume
  audio.addEventListener('timeupdate', ()=>{
    if (audio.duration) {
      progress.value = String((audio.currentTime / audio.duration) * 100);
      curTime.textContent = fmtTime(audio.currentTime);
      durTime.textContent = fmtTime(audio.duration);
    }
  })
  progress.addEventListener('input', ()=>{
    if (audio.duration) {
      const pct = Number(progress.value)/100; audio.currentTime = pct * audio.duration;
    }
  })
  volume.addEventListener('input', ()=>{ audio.volume = Number(volume.value); })

  // Ended → auto next
  audio.addEventListener('ended', ()=>{ btnNext.click(); })
})();