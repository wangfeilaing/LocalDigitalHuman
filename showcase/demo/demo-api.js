/* 在线演示层：把真实前端接到假数据上，且让「生成」跑出真实的进度观感。
 *
 * 原理：app.js 是经典脚本，所有请求都走全局 fetch / uploadApi。
 * 这里在 app.js 之前接管这两个入口，并重写媒体 URL 到本地静态素材，
 * 于是同一个前端既能连真后端，也能在纯静态站点上演示。
 *
 * 真后端的能力（真实语音合成、口型模型、4K 导出）需要 Windows + NVIDIA 显卡，
 * 无法在静态托管上运行，所以这里用等长的模拟流水线代替。
 */
(function () {
  'use strict';

  const DATA = window.__DEMO_DATA__ || {};
  const params = new URLSearchParams(location.search);
  const clone = value => JSON.parse(JSON.stringify(value));

  // ---------------------------------------------------------------- 模拟状态
  const state = {
    queue: clone(DATA.queue || { ok: true, items: [] }),
    job: clone(DATA['job-main'] || { kind: 'main', status: 'idle', progress: 0, log: [] }),
    cloneJob: clone(DATA['job-clone'] || { kind: 'clone', status: 'idle', progress: 0 }),
    previewJob: clone(DATA['job-preview'] || { kind: 'preview', status: 'idle', progress: 0 }),
    timer: null,
  };

  // 模拟流水线：阶段名 + 时长(ms) 刻意贴近真机实测（一条 6 分钟成片约 15-20 分钟）
  const STAGES = [
    ['校验参数与素材', 900],
    ['分段合成语音（IndexTTS-2 本地引擎）', 4200],
    ['字幕逐字对齐（faster-whisper large-v3-turbo）', 3000],
    ['口型同步（hdModule v2 · 1920 长边）', 5200],
    ['智能 B-roll 匹配（CLIP + bge 检索）', 1600],
    ['导出 4K 成片 + 自动封面', 2600],
  ];
  const STAGE_TOTAL = STAGES.reduce((sum, [, ms]) => sum + ms, 0);

  function stamp() {
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  function clearTimer() {
    if (state.timer) {
      clearInterval(state.timer);
      state.timer = null;
    }
  }

  // 启动一条模拟任务：逐阶段推进 job 与队列项的进度
  function startSimulation() {
    const pending = state.queue.items.find(item => item.status === 'pending');
    if (!pending || state.job.status === 'running') return;
    state.job = {
      kind: 'main', id: pending.id, status: 'running', progress: 0,
      stage: STAGES[0][0], message: '任务开始', error: null, result: null,
      cover: null, audio: null, outputDir: null, segmentsTotal: 3, segmentsDone: 0,
      startedAt: Math.floor(Date.now() / 1000), elapsedSeconds: 0,
      estimatedSeconds: Math.round(STAGE_TOTAL / 1000), log: [],
    };
    pending.status = 'running';
    pending.startedAt = Math.floor(Date.now() / 1000);
    pending.progress = 0;
    state.queue.status = 'running';
    state.queue.paused = false;

    const begun = Date.now();
    let stageIndex = 0;
    let stageStart = begun;
    state.timer = setInterval(() => {
      const now = Date.now();
      const elapsed = now - begun;
      const stageElapsed = now - stageStart;
      if (stageElapsed >= STAGES[stageIndex][1] && stageIndex < STAGES.length - 1) {
        stageIndex += 1;
        stageStart = now;
        state.job.log.push(`[${stamp()}] ${STAGES[stageIndex][0]}`);
        state.job.segmentsDone = Math.min(stageIndex, 2);
      }
      // 每个阶段内进度线性推进，阶段之间留一点"卡顿"更接近真机
      const within = Math.min(1, (now - stageStart) / STAGES[stageIndex][1]);
      const overall = Math.min(99.2, (() => {
        const before = STAGES.slice(0, stageIndex).reduce((s, [, ms]) => s + ms, 0);
        return (before + within * STAGES[stageIndex][1]) / STAGE_TOTAL * 100;
      })());
      state.job.stage = STAGES[stageIndex][0];
      state.job.progress = Number(overall.toFixed(1));
      state.job.elapsedSeconds = Math.round(elapsed / 1000);
      state.job.message = `${STAGES[stageIndex][0]} …`;
      pending.progress = state.job.progress;
      pending.stage = state.job.stage;
      if (elapsed >= STAGE_TOTAL) {
        clearTimer();
        state.job.status = 'done';
        state.job.progress = 100;
        state.job.stage = '已完成';
        state.job.message = '成片已导出';
        state.job.result = 'media/result.mp4';
        state.job.cover = 'media/result-cover.jpg';
        state.job.outputDir = 'D:\\数字人视频输出';
        state.job.log.push(`[${stamp()}] 导出完成：D:\\数字人视频输出\\${pending.title}.mp4`);
        pending.status = 'done';
        pending.progress = 100;
        pending.stage = '已完成';
        pending.result = 'media/result.mp4';
        pending.cover = 'media/result-cover.jpg';
        pending.finishedAt = Math.floor(Date.now() / 1000);
        state.queue.completed = state.queue.items.filter(i => i.status === 'done').length;
        state.queue.status = state.queue.items.some(i => i.status === 'pending') ? 'running' : 'done';
        state.queue.overallProgress = Number(
          (state.queue.items.reduce((s, i) => s + (i.status === 'done' ? 100 : i.progress || 0), 0) /
            Math.max(1, state.queue.items.length)).toFixed(1)
        );
        queueMicrotask(() => toast('演示流水线跑完：成片在「生成结果」里，可以直接播放。'));
        // 还原真实 worker 的行为：队列里还有等待中的任务就接着跑下一条
        if (state.queue.items.some(i => i.status === 'pending')) {
          setTimeout(startSimulation, 1200);
        }
      }
    }, 220);
  }

  // ---------------------------------------------------------------- 媒体重写
  function lookup(list, id) {
    return (list || []).find(entry => entry.id === id);
  }

  function rewriteMedia(url) {
    if (typeof url !== 'string' || !url) return url;
    if (url.startsWith('media/') || url.startsWith('../') || /^https?:/.test(url)) return url;
    if (url.indexOf('/api/media') === 0) return 'media/result.mp4';
    const match = url.match(/^\/api\/(avatar|broll|voice|music)-media\?(.*)$/);
    if (match) {
      const kind = match[1];
      const query = new URLSearchParams(match[2]);
      const id = query.get('id');
      const suffix = query.get('kind') === 'video' ? 'videoUrl' : 'posterUrl';
      if (kind === 'avatar') {
        const entry = lookup((DATA.avatars || {}).avatars, id);
        if (entry) return entry[suffix] || entry.posterUrl;
      }
      if (kind === 'broll') {
        const entry = lookup((DATA.broll || {}).assets, id);
        if (entry) return entry[suffix] || entry.posterUrl;
      }
      if (kind === 'voice') {
        const entry = lookup((DATA.voices || {}).voices, id);
        if (entry) return entry.previewUrl;
      }
      if (kind === 'music') {
        const entry = lookup((DATA.music || {}).music, id);
        if (entry) return entry.audioUrl;
      }
      return 'media/result-cover.jpg';
    }
    if (url === '/assets/app-icon.png') return '../assets/app-icon.png';
    return url;
  }

  function patchProperty(proto, prop) {
    const descriptor = Object.getOwnPropertyDescriptor(proto, prop);
    if (!descriptor || !descriptor.set) return;
    Object.defineProperty(proto, prop, {
      configurable: true,
      enumerable: descriptor.enumerable,
      get() { return descriptor.get.call(this); },
      set(value) { descriptor.set.call(this, rewriteMedia(value)); },
    });
  }
  patchProperty(HTMLMediaElement.prototype, 'src');
  patchProperty(HTMLImageElement.prototype, 'src');
  patchProperty(HTMLVideoElement.prototype, 'poster');

  // ---------------------------------------------------------------- 提示与横幅
  function toast(message) {
    if (typeof window.showToast === 'function') {
      try { window.showToast(message); return; } catch (_) { /* 忽略 */ }
    }
  }

  function mountBanner() {
    if (params.get('chrome') === '0' && params.get('debug') !== '1') return;
    const bar = document.createElement('div');
    bar.className = 'demo-banner';
    // 工作台是桌面端工具界面；窄屏下它按 1280 宽渲染再缩放，这里明确告知，避免被当成"页面崩了"
    const narrow = Math.min(window.screen?.width || 9999, window.innerWidth) < 900;
    bar.innerHTML =
      '<b>在线演示</b><span>前端为真实界面，数据是脱敏演示数据；点「开始生成」会跑一条模拟流水线。' +
      (narrow ? '<br>当前是窄屏：界面按桌面宽度缩放显示，<b style="color:#ffd479">建议用电脑打开</b>体验最佳。' : '') +
      '</span><a href="../index.html">← 返回项目介绍</a>';
    bar.style.cssText = [
      'position:fixed', 'left:18px', 'bottom:18px', 'z-index:99999',
      'display:flex', 'gap:10px', 'align-items:center', 'flex-wrap:wrap',
      'max-width:min(760px,calc(100vw - 36px))',
      'padding:10px 16px', 'border-radius:14px',
      'background:rgba(10,14,26,.92)', 'border:1px solid rgba(120,170,255,.35)',
      'box-shadow:0 12px 40px rgba(0,0,0,.45)', 'backdrop-filter:blur(10px)',
      'font-size:13px', 'line-height:1.5', 'color:#dbe6ff',
    ].join(';');
    bar.querySelector('b').style.cssText =
      'color:#7fb4ff;font-size:12px;letter-spacing:.08em;text-transform:uppercase';
    bar.querySelector('span').style.cssText = 'color:#9fb0cc';
    bar.querySelector('a').style.cssText =
      'color:#7fb4ff;text-decoration:none;border-bottom:1px dashed rgba(127,180,255,.5);white-space:nowrap';
    document.body.appendChild(bar);
    // ?debug=1 ：把演示层的运行状态实时打在横幅上，方便自检（也方便排查"点了没反应"）
    if (params.get('debug') === '1') {
      const probe = document.createElement('span');
      probe.style.cssText = 'color:#7de3a8;font-family:ui-monospace,Consolas,monospace';
      bar.appendChild(probe);
      setInterval(() => {
        const counts = state.queue.items.reduce((acc, item) => {
          acc[item.status] = (acc[item.status] || 0) + 1;
          return acc;
        }, {});
        probe.textContent =
          `items=${state.queue.items.length} ${JSON.stringify(counts)} ` +
          `job=${state.job.status}@${state.job.progress}%`;
      }, 500);
    }
  }

  // ---------------------------------------------------------------- 路由
  const response = (payload, status) => new Response(
    JSON.stringify(payload),
    { status: status || 200, headers: { 'Content-Type': 'application/json; charset=utf-8' } }
  );

  // 演示模式下不真正执行、但要给出可信反馈的动作
  const SOFT_OK = {
    '/api/pick': { ok: true, path: 'D:\\演示\\组件离线包' },
    '/api/setup/config': { ok: true },
    '/api/setup/install': { ok: true, steps: [] },
    '/api/setup/cancel': { ok: true },
    '/api/open-result': { ok: true },
    '/api/stop-models': { ok: true },
    '/api/voice/rename': { ok: true },
    '/api/voice/delete': { ok: true },
    '/api/avatar/delete': { ok: true },
    '/api/broll/delete': { ok: true },
    '/api/broll/update': { ok: true },
    '/api/asset/set-person': { ok: true },
    '/api/person/save': { ok: true },
    '/api/person/delete': { ok: true },
    '/api/voice/save-elevenlabs': { ok: true },
    '/api/voice/set-transcript': { ok: true, promptText: '这是演示用的对照文本。' },
    '/api/elevenlabs/account/save': { ok: true },
    '/api/elevenlabs/account/delete': { ok: true },
    '/api/elevenlabs/account/sync': { ok: true },
    '/api/output-folder/validate': { ok: true, exists: true, writable: true },
  };

  function routeJob(kind) {
    if (kind === 'clone') return state.cloneJob;
    if (kind === 'preview') return state.previewJob;
    if (kind === 'setup') return { kind: 'setup', status: 'idle', progress: 0, stage: '', log: [] };
    return state.job;
  }

  async function handle(path, url, init) {
    const method = ((init && init.method) || 'GET').toUpperCase();
    const body = (() => {
      try { return JSON.parse((init && init.body) || '{}'); } catch (_) { return {}; }
    })();

    switch (path) {
      case '/api/ping':
        return DATA.ping;
      case '/api/status':
        return DATA.status;
      case '/api/setup/steps':
        return DATA['setup-steps'];
      case '/api/persons':
        return DATA.persons;
      case '/api/voices':
        return DATA.voices;
      case '/api/avatars':
        return DATA.avatars;
      case '/api/broll':
        return DATA.broll;
      case '/api/music':
        return DATA.music;
      case '/api/elevenlabs/config':
        return DATA['elevenlabs-config'];
      case '/api/queue':
        return state.queue;
      case '/api/job':
        return routeJob(new URLSearchParams(url.split('?')[1] || '').get('kind') || 'main');

      // 生成链路：真实后端在这里由队列 worker 线程自动捡起 pending 任务，
      // 前端只负责调 /api/queue/add，所以演示层也要在返回后自己"启动 worker"。
      case '/api/queue/add': {
        const title = String(body.title || body.text || '未命名任务').slice(0, 24);
        const item = {
          id: `demo-${Date.now()}`, position: state.queue.items.length + 1,
          title, characters: String(body.text || '').replace(/\s/g, '').length,
          avatarId: body.avatarId || null, avatarName: '数字人顾问 01',
          voiceName: '沉稳男声 · 讲师A', voiceAccountName: '',
          elevenGenerationMode: '', elevenGenerationModeName: '',
          avatarPosterUrl: 'media/avatar-01.jpg', status: 'pending', progress: 0,
          stage: '排队中', result: null, cover: null, error: null,
          createdAt: Math.floor(Date.now() / 1000), startedAt: null, finishedAt: null,
          quality: body.quality || 'v2', resolution: body.resolution || '4k',
          brollEnabled: !!body.brollEnabled, musicId: body.musicId || '',
        };
        state.queue.items.push(item);
        state.queue.total = state.queue.items.length;
        state.queue.pending = state.queue.items.filter(i => i.status === 'pending').length;
        state.queue.status = 'running';
        setTimeout(startSimulation, 260);
        return { ok: true, queue: state.queue };
      }
      case '/api/start':
        startSimulation();
        return state.job;
      case '/api/queue/action': {
        const action = body.action || '';
        const item = state.queue.items.find(i => i.id === body.id);
        if (action === 'pause' || action === 'resume') {
          state.queue.paused = action === 'pause';
          state.queue.status = state.queue.paused ? 'paused' : 'running';
        } else if (action === 'start_item') {
          if (item && item.status !== 'done') {
            item.status = 'pending';
            state.queue.paused = false;
            state.queue.status = 'running';
            setTimeout(startSimulation, 260);
          }
        } else if (action === 'pause_item' && item) {
          item.status = 'paused';
          item.stage = '已暂停';
        } else if (action === 'cancel' && item) {
          clearTimer();
          item.status = 'cancelled';
          item.stage = '已停止';
          state.job.status = 'idle';
        } else if ((action === 'delete' || action === 'remove') && item) {
          clearTimer();
          state.queue.items = state.queue.items.filter(i => i.id !== body.id);
          state.queue.total = state.queue.items.length;
        } else if (action === 'clear_done') {
          state.queue.items = state.queue.items.filter(i => i.status !== 'done');
          state.queue.total = state.queue.items.length;
        }
        return state.queue;
      }
      case '/api/preview':
        state.previewJob = { kind: 'preview', status: 'done', progress: 100, audio: 'media/voice-01.mp3', error: null };
        return state.previewJob;
      case '/api/voice/clone': {
        state.cloneJob = { kind: 'clone', status: 'running', progress: 0, error: null };
        let progress = 0;
        const timer = setInterval(() => {
          progress += 12;
          if (progress >= 100) {
            clearInterval(timer);
            state.cloneJob = { kind: 'clone', status: 'done', progress: 100, error: null };
          } else {
            state.cloneJob = { kind: 'clone', status: 'running', progress, error: null };
          }
        }, 320);
        return state.cloneJob;
      }
      case '/api/voice/transcribe':
        return { ok: true, promptText: '（演示）识别出的样本对照文本，真实版由 FunASR SenseVoiceSmall 在 CPU 上转写。' };
      default:
        break;
    }

    if (SOFT_OK[path]) return SOFT_OK[path];
    return null;
  }

  const nativeFetch = window.fetch.bind(window);
  window.fetch = async function (input, init) {
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    const path = url.split('?')[0];
    if (path.indexOf('/api/') === 0) {
      const result = await handle(path, url, init);
      if (result) return response(result);
      return response({ ok: false, error: '演示模式：这个操作需要在本地完整版里执行（真实模型无法在静态站点运行）。' });
    }
    return nativeFetch(input, init);
  };

  // 上传类走 XHR，独立接管：模拟进度后返回成功或给出演示提示
  window.uploadApi = function (path, file, fields, onProgress) {
    const notices = {
      '/api/voice/upload-local': { ok: true, path: `D:\\演示\\${file.name}` },
      '/api/avatar/upload': { ok: true, id: 'demo-avatar-new', name: fields && fields.name },
      '/api/audio/upload': { ok: true, path: 'media/result.mp4', name: file.name, duration: 12.5 },
      '/api/broll/upload': { ok: true, id: 'B999' },
      '/api/music/upload': { ok: true, id: 'demo-music-new' },
    };
    return new Promise(resolve => {
      let progress = 0;
      const timer = setInterval(() => {
        progress = Math.min(100, progress + 14);
        if (onProgress) onProgress(progress);
        if (progress >= 100) {
          clearInterval(timer);
          toast('演示模式：上传已完成（文件只留在你本地，不会传到服务器）。');
          resolve(notices[path] || { ok: true });
        }
      }, 110);
    });
  };

  // ---------------------------------------------------------------- 启动
  // 冻结出某个进度的"生成中/已完成"状态，供截图与自检使用。
  // 为什么不靠真实跑一遍再截：无头浏览器的虚拟时间会加速计时器，
  // 而全新 profile 首次加载又慢，两者叠加根本没法稳定命中"跑到一半"的瞬间。
  // 这里直接构造状态并主动触发前端渲染，截图就完全确定了。
  function freezeAt(percent, done) {
    clearTimer();
    const now = Math.floor(Date.now() / 1000);
    let stage = STAGES[0][0];
    let accumulated = 0;
    for (const [name, ms] of STAGES) {
      accumulated += ms;
      stage = name;
      if (!done && percent <= accumulated / STAGE_TOTAL * 100) break;
    }
    if (done) stage = '已完成';

    const item = {
      id: `demo-freeze-${percent}`, position: state.queue.items.length + 1,
      title: '真正让人疲惫的，往往不是远方的山，而是鞋里的一粒沙',
      characters: 26, avatarId: (DATA.avatars.avatars[0] || {}).id,
      avatarName: '数字人顾问 01', voiceName: '沉稳男声 · 讲师A', voiceAccountName: '',
      elevenGenerationMode: '', elevenGenerationModeName: '',
      avatarPosterUrl: 'media/avatar-01.jpg',
      status: done ? 'done' : 'running',
      progress: done ? 100 : percent,
      stage,
      result: done ? 'media/result.mp4' : null,
      cover: done ? 'media/result-cover.jpg' : null,
      error: null,
      createdAt: now - (done ? 1300 : 420),
      startedAt: now - (done ? 1080 : 420),
      finishedAt: done ? now : null,
      quality: 'v2', resolution: '4k', brollEnabled: true, musicId: '',
    };
    state.queue.items.push(item);
    state.queue.total = state.queue.items.length;
    state.queue.pending = state.queue.items.filter(i => i.status === 'pending').length;
    state.queue.status = done ? 'done' : 'running';
    state.queue.paused = false;
    state.queue.overallProgress = Number(
      (state.queue.items.reduce((sum, i) => sum + (i.status === 'done' ? 100 : i.progress || 0), 0) /
        state.queue.items.length).toFixed(1)
    );
    state.job = {
      kind: 'main', id: item.id, status: done ? 'done' : 'running',
      progress: item.progress, stage, message: done ? '成片已导出' : `${stage} …`,
      error: null, result: item.result, cover: item.cover, audio: null,
      outputDir: done ? 'D:\\数字人视频输出' : null,
      segmentsTotal: 3, segmentsDone: done ? 3 : 2,
      startedAt: item.startedAt, elapsedSeconds: done ? 1080 : 420,
      estimatedSeconds: 1200, log: [],
    };
    // 主动触发一次真实渲染（pollQueue 之后会自己每 1.6s 轮询，状态不变所以画面稳定）
    try { window.pollQueue(); window.pollMain(); } catch (_) { /* 忽略 */ }
  }

  let booted = false;
  function boot() {
    if (booted) return;   // DOMContentLoaded 与 load 都会触发，只跑一次
    booted = true;
    mountBanner();
    const step = params.get('step');
    if (step) {
      setTimeout(() => {
        try { window.showStep(Number(step)); } catch (_) { /* 忽略 */ }
      }, 1200);
    }
    // ?scroll=bottom ：滚到面板底部（截图队列区域用）
    if (params.get('scroll') === 'bottom') {
      setTimeout(() => {
        const panel = document.querySelector('.panel.is-active') || document.body;
        if (panel && panel.scrollTo) panel.scrollTo(0, panel.scrollHeight);
        window.scrollTo(0, document.body.scrollHeight);
      }, 1800);
    }
    // ?freeze=46 / ?freeze=done ：冻结出确定性的"生成中/已完成"状态（截图与自检用）
    const freeze = params.get('freeze');
    if (freeze) {
      setTimeout(() => {
        const value = freeze === 'done' ? 100 : Number(freeze) || 46;
        freezeAt(value, freeze === 'done');
      }, 900);
    }
    // ?autostart=1 ：填好文案并点真实的「添加并自动开始」按钮，
    // 用来做端到端自检（验证 /api/queue/add 与 /api/start 都被演示层接管），也方便截"生成中"的图。
    if (params.get('autostart') === '1') {
      setTimeout(() => {
        // 队列 fixture 默认是"暂停"（为了展示暂停态），自检时按需恢复
        state.queue.paused = false;
        state.queue.status = 'running';
        const area = document.querySelector('#scriptText');
        if (area) {
          area.value = '真正让人疲惫的，往往不是远方的山，而是鞋里的一粒沙。';
          area.dispatchEvent(new Event('input', { bubbles: true }));
        }
        const toggle = document.querySelector('#pauseQueue');
        if (toggle && /继续/.test(toggle.textContent || '')) toggle.click();
        const button = document.querySelector('#startGenerate');
        if (button) button.click();
      }, 1600);
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
  window.addEventListener('load', () => setTimeout(boot, 600));
})();
