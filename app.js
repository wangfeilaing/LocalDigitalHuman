const ui = {
  steps: [...document.querySelectorAll('.step')],
  panels: [...document.querySelectorAll('.panel')],
  script: document.querySelector('#scriptText'),
  singleTitle: document.querySelector('#singleTitle'),
  singleScriptArea: document.querySelector('#singleScriptArea'),
  batchScriptArea: document.querySelector('#batchScriptArea'),
  batchScripts: [...document.querySelectorAll('.batch-script')],
  batchTitles: [...document.querySelectorAll('.batch-title')],
  batchMusicSearches: [...document.querySelectorAll('.batch-music-search')],
  batchMusicSelects: [...document.querySelectorAll('.batch-music-select')],
  batchMusicPreviewButtons: [...document.querySelectorAll('.batch-music-preview')],
  batchAvatarPickers: [...document.querySelectorAll('.batch-avatar-picker')],
  charCount: document.querySelector('#charCount'),
  textUpload: document.querySelector('#textUpload'),
  promptAudio: document.querySelector('#promptAudio'),
  promptText: document.querySelector('#promptText'),
  apiKey: document.querySelector('#apiKey'),
  voiceId: document.querySelector('#voiceId'),
  voiceGrid: document.querySelector('#voiceGrid'),
  addLocalVoice: document.querySelector('#addLocalVoice'),
  addElevenLabsVoice: document.querySelector('#addElevenLabsVoice'),
  localVoiceModal: document.querySelector('#localVoiceModal'),
  closeLocalVoiceModal: document.querySelector('#closeLocalVoiceModal'),
  cancelLocalVoiceModal: document.querySelector('#cancelLocalVoiceModal'),
  localVoiceName: document.querySelector('#localVoiceName'),
  localVoiceEngine: document.querySelector('#localVoiceEngine'),
  localVoicePath: document.querySelector('#localVoicePath'),
  localVoiceUpload: document.querySelector('#localVoiceUpload'),
  pickLocalVoiceSample: document.querySelector('#pickLocalVoiceSample'),
  localVoiceModeField: document.querySelector('#localVoiceModeField'),
  localVoiceTranscriptField: document.querySelector('#localVoiceTranscriptField'),
  localVoiceTranscript: document.querySelector('#localVoiceTranscript'),
  transcribeLocalVoice: document.querySelector('#transcribeLocalVoice'),
  renameTranscriptField: document.querySelector('#renameTranscriptField'),
  renameTranscript: document.querySelector('#renameTranscript'),
  transcribeRenamedVoice: document.querySelector('#transcribeRenamedVoice'),
  saveLocalVoice: document.querySelector('#saveLocalVoice'),
  voiceCloneProgress: document.querySelector('#voiceCloneProgress'),
  voiceCloneStage: document.querySelector('#voiceCloneStage'),
  voiceCloneValue: document.querySelector('#voiceCloneValue'),
  voiceCloneFill: document.querySelector('#voiceCloneFill'),
  voiceModal: document.querySelector('#voiceModal'),
  closeVoiceModal: document.querySelector('#closeVoiceModal'),
  cancelVoiceModal: document.querySelector('#cancelVoiceModal'),
  saveElevenLabsVoice: document.querySelector('#saveElevenLabsVoice'),
  voiceModalTitle: document.querySelector('#voiceModalTitle'),
  cloudVoiceRecordId: document.querySelector('#cloudVoiceRecordId'),
  cloudVoiceName: document.querySelector('#cloudVoiceName'),
  cloudVoiceId: document.querySelector('#cloudVoiceId'),
  cloudVoiceAccount: document.querySelector('#cloudVoiceAccount'),
  cloudVoiceRemote: document.querySelector('#cloudVoiceRemote'),
  cloudVoiceModel: document.querySelector('#cloudVoiceModel'),
  cloudVoiceOutputFormat: document.querySelector('#cloudVoiceOutputFormat'),
  cloudStability: document.querySelector('#cloudStability'),
  cloudStabilityValue: document.querySelector('#cloudStabilityValue'),
  cloudSimilarity: document.querySelector('#cloudSimilarity'),
  cloudSimilarityValue: document.querySelector('#cloudSimilarityValue'),
  cloudStyle: document.querySelector('#cloudStyle'),
  cloudStyleValue: document.querySelector('#cloudStyleValue'),
  cloudSpeakerBoost: document.querySelector('#cloudSpeakerBoost'),
  cloudVoiceConfigNote: document.querySelector('#cloudVoiceConfigNote'),
  editSelectedCloudVoice: document.querySelector('#editSelectedCloudVoice'),
  manageElevenAccounts: document.querySelector('#manageElevenAccounts'),
  quickAddElevenAccount: document.querySelector('#quickAddElevenAccount'),
  elevenSummary: document.querySelector('#elevenSummary'),
  elevenAccountStrip: document.querySelector('#elevenAccountStrip'),
  elevenAccountModal: document.querySelector('#elevenAccountModal'),
  closeElevenAccountModal: document.querySelector('#closeElevenAccountModal'),
  cancelElevenAccountModal: document.querySelector('#cancelElevenAccountModal'),
  elevenAccountList: document.querySelector('#elevenAccountList'),
  elevenAccountId: document.querySelector('#elevenAccountId'),
  elevenAccountName: document.querySelector('#elevenAccountName'),
  elevenApiKey: document.querySelector('#elevenApiKey'),
  elevenAccountPriority: document.querySelector('#elevenAccountPriority'),
  elevenAccountEnabled: document.querySelector('#elevenAccountEnabled'),
  newElevenAccount: document.querySelector('#newElevenAccount'),
  saveElevenAccount: document.querySelector('#saveElevenAccount'),
  renameModal: document.querySelector('#renameModal'),
  renameModalTitle: document.querySelector('#renameModalTitle'),
  renameName: document.querySelector('#renameName'),
  closeRenameModal: document.querySelector('#closeRenameModal'),
  cancelRenameModal: document.querySelector('#cancelRenameModal'),
  saveRename: document.querySelector('#saveRename'),
  avatarVideo: document.querySelector('#avatarVideo'),
  outputDir: document.querySelector('#outputDir'),
  avatarGrid: document.querySelector('#avatarGrid'),
  addAvatar: document.querySelector('#addAvatar'),
  avatarUpload: document.querySelector('#avatarUpload'),
  avatarModal: document.querySelector('#avatarModal'),
  avatarModalTitle: document.querySelector('#avatarModalTitle'),
  avatarPreviewVideo: document.querySelector('#avatarPreviewVideo'),
  closeAvatarModal: document.querySelector('#closeAvatarModal'),
  batchAvatarModal: document.querySelector('#batchAvatarModal'),
  batchAvatarModalTitle: document.querySelector('#batchAvatarModalTitle'),
  batchAvatarOptions: document.querySelector('#batchAvatarOptions'),
  closeBatchAvatarModal: document.querySelector('#closeBatchAvatarModal'),
  speed: document.querySelector('#speed'),
  speedValue: document.querySelector('#speedValue'),
  v2VoiceParams: document.querySelector('#v2VoiceParams'),
  voxcpmVoiceParams: document.querySelector('#voxcpmVoiceParams'),
  emotionWeight: document.querySelector('#emotionWeight'),
  emotionWeightValue: document.querySelector('#emotionWeightValue'),
  emotionText: document.querySelector('#emotionText'),
  cfgValue: document.querySelector('#cfgValue'),
  cfgValueValue: document.querySelector('#cfgValueValue'),
  inferenceTimesteps: document.querySelector('#inferenceTimesteps'),
  inferenceTimestepsValue: document.querySelector('#inferenceTimestepsValue'),
  elevenVoiceParams: document.querySelector('#elevenVoiceParams'),
  elevenStability: document.querySelector('#elevenStability'),
  elevenStabilityValue: document.querySelector('#elevenStabilityValue'),
  elevenSimilarity: document.querySelector('#elevenSimilarity'),
  elevenSimilarityValue: document.querySelector('#elevenSimilarityValue'),
  elevenStyle: document.querySelector('#elevenStyle'),
  elevenStyleValue: document.querySelector('#elevenStyleValue'),
  elevenSpeakerBoost: document.querySelector('#elevenSpeakerBoost'),
  elevenParamsNote: document.querySelector('#elevenParamsNote'),
  cloudFields: document.querySelector('#cloudVoiceFields'),
  workbenchElevenMode: document.querySelector('#workbenchElevenMode'),
  workbenchElevenModeHint: document.querySelector('#workbenchElevenModeHint'),
  workbenchElevenAccount: document.querySelector('#workbenchElevenAccount'),
  workbenchElevenAccountHint: document.querySelector('#workbenchElevenAccountHint'),
  previewButton: document.querySelector('#previewVoice'),
  audioPreview: document.querySelector('#audioPreview'),
  customAudioRow: document.querySelector('#customAudioRow'),
  customAudioFile: document.querySelector('#customAudioFile'),
  uploadCustomAudio: document.querySelector('#uploadCustomAudio'),
  customAudioName: document.querySelector('#customAudioName'),
  customAudioPreview: document.querySelector('#customAudioPreview'),
  startButton: document.querySelector('#startGenerate'),
  backButton: document.querySelector('#backFromGenerate'),
  taskArea: document.querySelector('#taskArea'),
  progressStage: document.querySelector('#progressStage'),
  progressValue: document.querySelector('#progressValue'),
  progressFill: document.querySelector('#progressFill'),
  queueList: document.querySelector('#queueList'),
  errorBox: document.querySelector('#errorBox'),
  resultArea: document.querySelector('#resultArea'),
  resultVideo: document.querySelector('#resultVideo'),
  openResult: document.querySelector('#openResult'),
  toast: document.querySelector('#toast'),
  deviceStatus: document.querySelector('#deviceStatus'),
  sourceResolutionChoice: document.querySelector('#sourceResolutionChoice'),
  subtitleEnabled: document.querySelector('#subtitleEnabled'),
  textFont: document.querySelector('#textFont'),
  textShadow: document.querySelector('#textShadow'),
  titleColorTop: document.querySelector('#titleColorTop'),
  titleColorBottom: document.querySelector('#titleColorBottom'),
  nameplateEnabled: document.querySelector('#nameplateEnabled'),
  speakerName: document.querySelector('#speakerName'),
  speakerDetails: document.querySelector('#speakerDetails'),
  brollEnabled: document.querySelector('#brollEnabled'),
  addBroll: document.querySelector('#addBroll'),
  brollUpload: document.querySelector('#brollUpload'),
  brollLibraryCount: document.querySelector('#brollLibraryCount'),
  brollUsableCount: document.querySelector('#brollUsableCount'),
  brollSearch: document.querySelector('#brollSearch'),
  brollCategory: document.querySelector('#brollCategory'),
  brollStatus: document.querySelector('#brollStatus'),
  brollUploadProgress: document.querySelector('#brollUploadProgress'),
  backFromBrollLibrary: document.querySelector('#backFromBrollLibrary'),
  brollLibraryGrid: document.querySelector('#brollLibraryGrid'),
  brollPreviewModal: document.querySelector('#brollPreviewModal'),
  brollPreviewTitle: document.querySelector('#brollPreviewTitle'),
  brollPreviewVideo: document.querySelector('#brollPreviewVideo'),
  brollPreviewMeta: document.querySelector('#brollPreviewMeta'),
  closeBrollPreview: document.querySelector('#closeBrollPreview'),
  addMusic: document.querySelector('#addMusic'),
  musicUpload: document.querySelector('#musicUpload'),
  musicLibraryCount: document.querySelector('#musicLibraryCount'),
  singleMusicSearch: document.querySelector('#singleMusicSearch'),
  singleMusicSelect: document.querySelector('#singleMusicSelect'),
  previewMusic: document.querySelector('#previewMusic'),
  musicPreview: document.querySelector('#musicPreview'),
  musicVolume: document.querySelector('#musicVolume'),
  musicVolumeValue: document.querySelector('#musicVolumeValue'),
  themeToggle: document.querySelector('#themeToggle'),
  draftStatus: document.querySelector('#draftStatus'),
  changeAvatar: document.querySelector('#changeAvatar'),
  selectedAvatarCard: document.querySelector('#selectedAvatarCard'),
  currentAvatarImage: document.querySelector('#currentAvatarImage'),
  currentAvatarName: document.querySelector('#currentAvatarName'),
  currentAvatarMeta: document.querySelector('#currentAvatarMeta'),
  changeVoice: document.querySelector('#changeVoice'),
  currentVoiceMeta: document.querySelector('#currentVoiceMeta'),
  voicePersonSelect: document.querySelector('#voicePersonSelect'),
  workbenchVoiceSelect: document.querySelector('#workbenchVoiceSelect'),
  avatarPersonSelect: document.querySelector('#avatarPersonSelect'),
  workbenchAvatarSelect: document.querySelector('#workbenchAvatarSelect'),
  managePersonsBtn1: document.querySelector('#managePersonsBtn1'),
  managePersonsBtn2: document.querySelector('#managePersonsBtn2'),
  personModal: document.querySelector('#personModal'),
  closePersonModal: document.querySelector('#closePersonModal'),
  cancelPersonModal: document.querySelector('#cancelPersonModal'),
  personList: document.querySelector('#personList'),
  personNameInput: document.querySelector('#personNameInput'),
  addPersonBtn: document.querySelector('#addPersonBtn'),
  renamePersonSelect: document.querySelector('#renamePersonSelect'),
  localVoicePerson: document.querySelector('#localVoicePerson'),
  cloudVoicePerson: document.querySelector('#cloudVoicePerson'),
  brollPersonFilter: document.querySelector('#brollPersonFilter'),
  brollEditPerson: document.querySelector('#brollEditPerson'),
  queueCountBadge: document.querySelector('#queueCountBadge'),
  queueSummary: document.querySelector('#queueSummary'),
  queueEmpty: document.querySelector('#queueEmpty'),
  pauseQueue: document.querySelector('#pauseQueue'),
  clearFinished: document.querySelector('#clearFinished'),
  backFromVoiceLibrary: document.querySelector('#backFromVoiceLibrary'),
  backFromAvatarLibrary: document.querySelector('#backFromAvatarLibrary'),
  voiceLibraryHint: document.querySelector('#voiceLibraryHint'),
  avatarLibraryHint: document.querySelector('#avatarLibraryHint'),
  outputPathModal: document.querySelector('#outputPathModal'),
  closeOutputPathModal: document.querySelector('#closeOutputPathModal'),
  cancelOutputPathModal: document.querySelector('#cancelOutputPathModal'),
  outputPathInput: document.querySelector('#outputPathInput'),
  browseOutputPath: document.querySelector('#browseOutputPath'),
  useDefaultOutputPath: document.querySelector('#useDefaultOutputPath'),
  saveOutputPath: document.querySelector('#saveOutputPath'),
  brollEditModal: document.querySelector('#brollEditModal'),
  closeBrollEditModal: document.querySelector('#closeBrollEditModal'),
  cancelBrollEditModal: document.querySelector('#cancelBrollEditModal'),
  brollEditName: document.querySelector('#brollEditName'),
  brollEditCategory: document.querySelector('#brollEditCategory'),
  brollEditTags: document.querySelector('#brollEditTags'),
  brollEditStatus: document.querySelector('#brollEditStatus'),
  saveBrollEdit: document.querySelector('#saveBrollEdit'),
  openSetup: document.querySelector('#openSetup'),
  setupModal: document.querySelector('#setupModal'),
  closeSetupModal: document.querySelector('#closeSetupModal'),
  closeSetupModalBottom: document.querySelector('#closeSetupModalBottom'),
  setupGpuText: document.querySelector('#setupGpuText'),
  setupGpuTweak: document.querySelector('#setupGpuTweak'),
  setupBundleText: document.querySelector('#setupBundleText'),
  setupBundlePick: document.querySelector('#setupBundlePick'),
  setupStepList: document.querySelector('#setupStepList'),
  setupProgress: document.querySelector('#setupProgress'),
  setupStage: document.querySelector('#setupStage'),
  setupValue: document.querySelector('#setupValue'),
  setupFill: document.querySelector('#setupFill'),
  setupLog: document.querySelector('#setupLog'),
  cancelSetupInstall: document.querySelector('#cancelSetupInstall'),
  startSetupInstall: document.querySelector('#startSetupInstall'),
};

let currentStep = 1;
let scriptMode = 'single';
let voiceMode = 'local';
let quality = 'v2';
let resolution = '4k';
let activeRunMode = 'single';
let avatars = [];
let selectedAvatarId = null;
let voices = [];
let persons = [];
let elevenConfig = { accounts: [], models: [], generationModes: [], outputFormats: [], readyAccounts: 0 };
let musicLibrary = [];
let selectedVoiceId = null;
let customAudioPath = '';
let customAudioName = '';
let selectedElevenAccountId = '';
let componentStatus = null;
let setupPollTimer = null;
let setupAutoOpened = false;
let selectedElevenGenerationMode = 'multilingual_v2';
let toastTimer = null;
let mainPollTimer = null;
let previewPollTimer = null;
let localVoiceFile = null;
let localVoiceCreatedId = null;
let voiceCloneBusy = false;
let renameTarget = null;
let batchAvatarIds = Array(10).fill('');
let activeBatchAvatarIndex = -1;
let brollAssets = [];
let queuePollActive = false;
let queuePaused = false;
let appReady = false;
let draftSaveTimer = null;
let librarySelectionContext = null;
let defaultOutputPath = '';
let brollEditTargetId = null;
const DRAFT_KEY = 'localDhWorkbenchDraftV1';
const ELEVEN_GENERATION_MODES = {
  multilingual_v2: {
    name: 'Multilingual v2 · 音色稳定',
    modelId: 'eleven_multilingual_v2',
    description: '中文长文稳定，优先保持本人音色。',
  },
  v3: {
    name: 'V3 · 情感优先',
    modelId: 'eleven_v3',
    description: '情绪和语气更丰富，音色可能比本人略有变化。',
  },
  turbo_v2: {
    name: 'Eleven Turbo v2 · 快速输出',
    modelId: 'eleven_turbo_v2',
    description: '生成速度快；这个版本偏英文，中文优先使用 Multilingual v2 或结合版。',
  },
  v3_voice_match: {
    name: 'V3情感＋本人音色',
    modelId: 'eleven_v3',
    description: '先生成V3情感，再转换回本人音色；处理两次，时间和额度消耗更高。',
  },
};

async function api(path, options = {}) {
  const config = { ...options };
  config.headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const response = await fetch(path, config);
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || '操作失败');
  }
  return data;
}

function uploadApi(path, file, fields = {}, onProgress = null) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append('file', file, file.name);
    Object.entries(fields).forEach(([key, value]) => form.append(key, String(value ?? '')));
    const request = new XMLHttpRequest();
    request.open('POST', path);
    request.responseType = 'json';
    request.upload.addEventListener('progress', event => {
      if (event.lengthComputable && onProgress) onProgress(Math.round(event.loaded / event.total * 100));
    });
    request.addEventListener('load', () => {
      let data = request.response;
      if (!data) {
        try { data = JSON.parse(request.responseText || '{}'); } catch { data = {}; }
      }
      if (request.status < 200 || request.status >= 300 || data.ok === false) {
        reject(new Error(data.error || '上传失败'));
      } else {
        resolve(data);
      }
    });
    request.addEventListener('error', () => reject(new Error('上传失败，请确认本地服务正在运行。')));
    request.addEventListener('abort', () => reject(new Error('上传已取消。')));
    request.send(form);
  });
}

function showToast(message) {
  clearTimeout(toastTimer);
  ui.toast.textContent = message;
  ui.toast.classList.remove('is-hidden');
  toastTimer = setTimeout(() => ui.toast.classList.add('is-hidden'), 3200);
}

function applyTheme(theme) {
  const value = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = value;
  localStorage.setItem('localDhTheme', value);
  if (ui.themeToggle) ui.themeToggle.title = value === 'dark' ? '切换为浅色主题' : '切换为深色主题';
}

function toggleTheme() {
  applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
}

function showStep(step) {
  currentStep = Number(step) === 4 ? 1 : Number(step);
  ui.steps.forEach(button => button.classList.toggle('is-active', Number(button.dataset.step) === currentStep));
  ui.panels.forEach(panel => panel.classList.toggle('is-active', Number(panel.dataset.panel) === currentStep));
  if (currentStep === 1) updateSummary();
}

function openLibraryForSelection(kind) {
  librarySelectionContext = kind;
  if (kind === 'avatar') {
    ui.avatarLibraryHint.textContent = '请选择要用于当前任务的数字人，选中后会自动返回工作台。';
    showStep(3);
  } else {
    ui.voiceLibraryHint.textContent = '请选择要用于当前任务的声音，选中后会自动返回工作台。';
    showStep(2);
  }
}

function resetLibrarySelectionContext() {
  librarySelectionContext = null;
  ui.avatarLibraryHint.textContent = '上传、预览、改名和管理所有可用形象。';
  ui.voiceLibraryHint.textContent = '本地声音与 ElevenLabs 云端声音统一管理，生成时直接选择。';
}

function leaveLibrarySelection() {
  resetLibrarySelectionContext();
  showStep(1);
}

function basename(path) {
  return String(path || '').split(/[\\/]/).filter(Boolean).pop() || '尚未选择';
}

function selectedAvatar() {
  return avatars.find(avatar => avatar.id === selectedAvatarId) || null;
}

function selectedVoice() {
  return voices.find(voice => voice.id === selectedVoiceId) || null;
}

function personById(personId) {
  return persons.find(person => person.id === personId) || null;
}

function personName(id) {
  return personById(id)?.name || '未分组';
}

// personId 为空或指向已删除人物时，统一按未分组处理
function knownPersonId(id) {
  return id && personById(id) ? id : '';
}

function groupByPerson(items) {
  const groups = [];
  persons.forEach(person => {
    const list = items.filter(item => item.personId === person.id);
    if (list.length) groups.push({ id: person.id, name: person.name, items: list });
  });
  const rest = items.filter(item => !knownPersonId(item.personId));
  if (rest.length) groups.push({ id: '', name: '未分组', items: rest });
  return groups;
}

function voicesByPerson() {
  return groupByPerson(voices);
}

function avatarsByPerson() {
  return groupByPerson(avatars);
}

// 填充"所属人物"下拉（未分组 + 所有人物），供各弹窗使用
function fillPersonSelect(select, currentId = '') {
  if (!select) return;
  select.replaceChildren(new Option('未分组', ''));
  persons.forEach(person => select.appendChild(new Option(person.name, person.id)));
  select.value = knownPersonId(currentId);
}

async function loadPersons() {
  const result = await api('/api/persons');
  persons = Array.isArray(result.persons) ? result.persons : [];
  afterPersonsChanged();
}

// persons 变化后统一重渲染：素材库分组、工作台下拉、B-roll 筛选
function afterPersonsChanged() {
  renderPersonList();
  renderVoices();
  renderAvatars();
  syncWorkbenchVoiceSelects();
  syncWorkbenchAvatarSelects();
  renderBrollPersonFilter();
  if (brollAssets.length) renderBrollLibrary();
}

function renderVoicePersonSelect() {
  if (!ui.voicePersonSelect) return;
  const groups = voicesByPerson();
  ui.voicePersonSelect.replaceChildren();
  if (!groups.length) {
    const option = new Option('暂无声音', '');
    option.disabled = true;
    ui.voicePersonSelect.appendChild(option);
  } else {
    groups.forEach(group => ui.voicePersonSelect.appendChild(new Option(group.name, group.id)));
  }
  // "自己录音"是声音来源的第三种选择：上传本人朗读音频，跳过语音合成
  ui.voicePersonSelect.appendChild(new Option('🎙 自己录音', '__upload__'));
  if (voiceMode === 'upload') {
    ui.voicePersonSelect.value = '__upload__';
    return;
  }
  if (!groups.length) return;
  const voice = selectedVoice();
  const groupId = voice ? knownPersonId(voice.personId) : '';
  ui.voicePersonSelect.value = groups.some(group => group.id === groupId) ? groupId : groups[0].id;
}

function renderWorkbenchVoiceOptions(personId) {
  if (!ui.workbenchVoiceSelect) return;
  if (personId === '__upload__') {
    ui.workbenchVoiceSelect.replaceChildren(new Option(
      customAudioName ? `我的录音：${customAudioName}` : '上传我的录音文件', '__upload__',
    ));
    return;
  }
  const groups = voicesByPerson();
  const group = groups.find(item => item.id === personId) || groups[0] || null;
  ui.workbenchVoiceSelect.replaceChildren();
  if (!group) {
    const option = new Option('暂无声音', '');
    option.disabled = true;
    ui.workbenchVoiceSelect.appendChild(option);
    return;
  }
  group.items.forEach(voice => {
    let label;
    let usable = true;
    if (voice.provider === 'local') {
      const engineLabel = voice.engineName || (voice.engine === 'voxcpm' ? 'VoxCPM 2 · 本地免费' : 'IndexTTS-2 · 本地免费');
      label = `${voice.name}（${engineLabel}）`;
      if (voice.status === 'pending') {
        label += ' · 克隆中';
        usable = false;
      } else if (voice.status === 'error') {
        label += ' · 克隆失败';
        usable = false;
      }
    } else {
      label = `${voice.name}（ElevenLabs · 付费）`;
    }
    const option = new Option(label, voice.id);
    option.disabled = !usable;
    ui.workbenchVoiceSelect.appendChild(option);
  });
  const voice = selectedVoice();
  if (voice && group.items.some(item => item.id === voice.id)) {
    ui.workbenchVoiceSelect.value = voice.id;
  } else {
    const firstUsable = group.items.find(item => item.provider !== 'local' || item.status === 'ready');
    ui.workbenchVoiceSelect.value = (firstUsable || group.items[0]).id;
  }
}

function syncWorkbenchVoiceSelects() {
  if (!ui.voicePersonSelect || !ui.workbenchVoiceSelect) return;
  renderVoicePersonSelect();
  renderWorkbenchVoiceOptions(ui.voicePersonSelect.value);
}

function renderAvatarPersonSelect() {
  if (!ui.avatarPersonSelect) return;
  const groups = avatarsByPerson();
  ui.avatarPersonSelect.replaceChildren();
  if (!groups.length) {
    const option = new Option('暂无形象', '');
    option.disabled = true;
    ui.avatarPersonSelect.appendChild(option);
    return;
  }
  groups.forEach(group => ui.avatarPersonSelect.appendChild(new Option(group.name, group.id)));
  const avatar = selectedAvatar();
  const groupId = avatar ? knownPersonId(avatar.personId) : '';
  ui.avatarPersonSelect.value = groups.some(group => group.id === groupId) ? groupId : groups[0].id;
}

function renderWorkbenchAvatarOptions(personId) {
  if (!ui.workbenchAvatarSelect) return;
  const groups = avatarsByPerson();
  const group = groups.find(item => item.id === personId) || groups[0] || null;
  ui.workbenchAvatarSelect.replaceChildren();
  if (!group) {
    const option = new Option('暂无形象', '');
    option.disabled = true;
    ui.workbenchAvatarSelect.appendChild(option);
    return;
  }
  group.items.forEach(avatar => {
    ui.workbenchAvatarSelect.appendChild(new Option(avatar.name, avatar.id));
  });
  const avatar = selectedAvatar();
  ui.workbenchAvatarSelect.value = avatar && group.items.some(item => item.id === avatar.id)
    ? avatar.id
    : group.items[0].id;
}

function syncWorkbenchAvatarSelects() {
  if (!ui.avatarPersonSelect || !ui.workbenchAvatarSelect) return;
  renderAvatarPersonSelect();
  renderWorkbenchAvatarOptions(ui.avatarPersonSelect.value);
}

function renderBrollPersonFilter() {
  if (!ui.brollPersonFilter) return;
  const selected = ui.brollPersonFilter.value;
  ui.brollPersonFilter.replaceChildren(new Option('全部人物', ''));
  persons.forEach(person => ui.brollPersonFilter.appendChild(new Option(person.name, person.id)));
  ui.brollPersonFilter.appendChild(new Option('未分组', '__ungrouped__'));
  if ([...ui.brollPersonFilter.options].some(option => option.value === selected)) {
    ui.brollPersonFilter.value = selected;
  }
}

function elevenGenerationMode(modeId = selectedElevenGenerationMode) {
  return ELEVEN_GENERATION_MODES[modeId] || ELEVEN_GENERATION_MODES.multilingual_v2;
}

function elevenGenerationModeForModel(modelId) {
  if (modelId === 'eleven_v3') return 'v3';
  if (modelId === 'eleven_turbo_v2') return 'turbo_v2';
  return 'multilingual_v2';
}

// 专业克隆（Professional Voice Clone）未在 ElevenLabs 上做微调时，
// multilingual_v2/turbo_v2 会被 API 拒绝（Voice is not fine-tuned），
// 只有 v3 系（eleven_v3 不要求微调）可用，默认走 v3_voice_match
function defaultElevenModeForVoice(voice) {
  if (voice?.category === 'professional') return 'v3_voice_match';
  return elevenGenerationModeForModel(voice?.modelId);
}

function setElevenGenerationMode(modeId, save = true) {
  const requested = ELEVEN_GENERATION_MODES[modeId] ? modeId : 'multilingual_v2';
  selectedElevenGenerationMode = requested;
  if (ui.workbenchElevenMode) ui.workbenchElevenMode.value = requested;
  const mode = elevenGenerationMode(requested);
  if (ui.workbenchElevenModeHint) {
    ui.workbenchElevenModeHint.textContent = mode.description;
    ui.workbenchElevenModeHint.classList.toggle('is-accent', requested === 'v3_voice_match');
  }
  const voice = selectedVoice();
  if (ui.currentVoiceMeta && voice?.provider === 'elevenlabs') {
    const account = elevenAccountById(selectedElevenAccountId);
    ui.currentVoiceMeta.textContent = `${account?.name || '自动选择账号'} · ${mode.name}`;
  }
  updateElevenParamsAvailability();
  updateSummary();
  if (save && appReady) scheduleDraftSave();
}

function musicById(musicId) {
  return musicLibrary.find(track => track.id === musicId) || null;
}

function collectBatchTasks() {
  return ui.batchScripts.map((input, index) => ({
    title: ui.batchTitles[index]?.value.trim() || '',
    text: input.value.trim(),
    musicId: ui.batchMusicSelects[index]?.value || '',
    avatarId: batchAvatarIds[index] || '',
    avatarVideo: avatars.find(item => item.id === batchAvatarIds[index])?.videoPath || '',
  }));
}

function collectData() {
  const tasks = collectBatchTasks();
  const voice = selectedVoice();
  const firstBatchTask = tasks.find(item => item.text) || { title: '', text: '', musicId: '' };
  const text = scriptMode === 'batch' ? firstBatchTask.text : ui.script.value.trim();
  const videoTitle = scriptMode === 'batch' ? firstBatchTask.title : ui.singleTitle.value.trim();
  const musicId = scriptMode === 'batch' ? firstBatchTask.musicId : ui.singleMusicSelect.value;
  return {
    text,
    texts: tasks.map(item => item.text),
    tasks,
    scriptMode,
    voiceMode,
    localVoiceId: voiceMode === 'local' ? (selectedVoiceId || '') : '',
    customAudio: voiceMode === 'upload' ? customAudioPath : '',
    promptAudio: ui.promptAudio.value.trim(),
    promptText: ui.promptText.value.trim(),
    apiKey: ui.apiKey.value.trim(),
    voiceId: ui.voiceId.value.trim(),
    elevenVoiceRecordId: voiceMode === 'elevenlabs' ? (voice?.id || '') : '',
    elevenAccountId: voiceMode === 'elevenlabs' ? selectedElevenAccountId : '',
    elevenGenerationMode: voiceMode === 'elevenlabs' ? selectedElevenGenerationMode : '',
    elevenModelId: voiceMode === 'elevenlabs'
      ? elevenGenerationMode().modelId
      : '',
    elevenOutputFormat: voiceMode === 'elevenlabs' ? (voice?.outputFormat || 'mp3_44100_128') : '',
    elevenSettings: voiceMode === 'elevenlabs' ? (voice?.settings || {}) : {},
    speed: Number(ui.speed.value),
    emotionWeight: Number(ui.emotionWeight.value),
    emotionText: ui.emotionText.value.trim(),
    cfgValue: Number(ui.cfgValue.value),
    inferenceTimesteps: Number(ui.inferenceTimesteps.value),
    quality,
    resolution,
    videoTitle,
    subtitleEnabled: ui.subtitleEnabled.checked,
    textFont: ui.textFont.value,
    textShadow: ui.textShadow.value,
    titleColorTop: ui.titleColorTop.value,
    titleColorBottom: ui.titleColorBottom.value,
    nameplateEnabled: ui.nameplateEnabled.checked,
    speakerName: ui.speakerName.value.trim(),
    speakerDetails: ui.speakerDetails.value.trim(),
    brollEnabled: ui.brollEnabled.checked,
    musicId,
    musicVolume: Number(ui.musicVolume.value),
    avatarId: selectedAvatarId || '',
    avatarVideo: ui.avatarVideo.value.trim(),
    outputDir: ui.outputDir.value.trim(),
  };
}

function draftPayload() {
  return {
    title: ui.singleTitle.value,
    text: ui.script.value,
    musicId: ui.singleMusicSelect.value,
    musicVolume: Number(ui.musicVolume.value),
    voiceId: selectedVoiceId || '',
    voiceUpload: voiceMode === 'upload',
    customAudioPath,
    customAudioName,
    elevenAccountId: selectedElevenAccountId,
    elevenGenerationMode: selectedElevenGenerationMode,
    avatarId: selectedAvatarId || '',
    speed: Number(ui.speed.value),
    quality,
    resolution,
    brollEnabled: ui.brollEnabled.checked,
    subtitleEnabled: ui.subtitleEnabled.checked,
    textFont: ui.textFont.value,
    textShadow: ui.textShadow.value,
    titleColorTop: ui.titleColorTop.value,
    titleColorBottom: ui.titleColorBottom.value,
    nameplateEnabled: ui.nameplateEnabled.checked,
    speakerName: ui.speakerName.value,
    speakerDetails: ui.speakerDetails.value,
    outputDir: ui.outputDir.value,
    savedAt: Date.now(),
  };
}

function saveDraft() {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draftPayload()));
    if (ui.draftStatus) ui.draftStatus.textContent = '草稿已保存';
  } catch {
    if (ui.draftStatus) ui.draftStatus.textContent = '草稿保存失败';
  }
}

function scheduleDraftSave() {
  clearTimeout(draftSaveTimer);
  if (ui.draftStatus) ui.draftStatus.textContent = '正在保存草稿';
  draftSaveTimer = setTimeout(saveDraft, 650);
}

function restoreDraft() {
  let draft = null;
  try { draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null'); } catch { draft = null; }
  if (!draft || typeof draft !== 'object') return;
  ui.singleTitle.value = String(draft.title || '');
  ui.script.value = String(draft.text || '');
  ui.charCount.textContent = `${ui.script.value.length} 字`;
  ui.musicVolume.value = String(Number(draft.musicVolume ?? 12));
  ui.musicVolumeValue.textContent = `${Number(ui.musicVolume.value)}%`;
  ui.speed.value = String(Number(draft.speed || 1));
  ui.speedValue.textContent = `${Number(ui.speed.value).toFixed(2)}×`;
  ui.brollEnabled.checked = Boolean(draft.brollEnabled);
  ui.subtitleEnabled.checked = draft.subtitleEnabled !== false;
  ui.nameplateEnabled.checked = draft.nameplateEnabled !== false;
  ui.textFont.value = draft.textFont || 'dongfangdakai';
  ui.textShadow.value = draft.textShadow || 'standard';
  ui.titleColorTop.value = draft.titleColorTop || '#FFFFFF';
  ui.titleColorBottom.value = draft.titleColorBottom || '#FFE66D';
  ui.speakerName.value = draft.speakerName || '讲师A';
  ui.speakerDetails.value = draft.speakerDetails || ui.speakerDetails.value;
  if (draft.outputDir) {
    // 2026-08-17 输出目录从工程内 视频输出 迁到 D 盘，旧草稿路径自动改写
    const legacyOutput = 'C:\\Users\\w1227\\Documents\\Codex\\2026-08-10\\wo\\outputs\\LocalDigitalHuman\\视频输出';
    ui.outputDir.value = draft.outputDir.toLowerCase() === legacyOutput.toLowerCase()
      ? (defaultOutputPath || draft.outputDir)
      : draft.outputDir;
  }
  setQuality(draft.quality || 'v2');
  setResolution(draft.resolution || '4k');
  if (voices.some(item => item.id === draft.voiceId)) setVoice(draft.voiceId, draft.elevenAccountId || '');
  if (draft.voiceUpload) {
    customAudioPath = String(draft.customAudioPath || '');
    customAudioName = String(draft.customAudioName || '');
    setUploadVoiceMode();
  }
  setElevenGenerationMode(
    draft.elevenGenerationMode
      || defaultElevenModeForVoice(selectedVoice()),
    false,
  );
  if (avatars.some(item => item.id === draft.avatarId)) setAvatar(draft.avatarId);
  if (musicLibrary.some(item => item.id === draft.musicId)) ui.singleMusicSelect.value = draft.musicId;
  if (ui.draftStatus) ui.draftStatus.textContent = ui.script.value ? '已恢复上次草稿' : '草稿已保存';
}

function clearTaskEditorAfterQueue() {
  ui.singleTitle.value = '';
  ui.script.value = '';
  ui.charCount.textContent = '0 字';
  ui.singleMusicSearch.value = '';
  fillMusicSelect(ui.singleMusicSelect, '');
  ui.singleMusicSelect.value = '';
  ui.brollEnabled.checked = false;
  if (avatars.length > 1) {
    const currentAvatarIndex = Math.max(0, avatars.findIndex(item => item.id === selectedAvatarId));
    setAvatar(avatars[(currentAvatarIndex + 1) % avatars.length].id);
  }
  ui.musicPreview.pause();
  ui.musicPreview.classList.add('is-hidden');
  localStorage.setItem(DRAFT_KEY, JSON.stringify(draftPayload()));
  if (ui.draftStatus) ui.draftStatus.textContent = '已创建下一条空白草稿';
  ui.singleTitle.focus();
}

function validateStep(step) {
  const data = collectData();
  if (step >= 1 && scriptMode === 'single' && !data.text && data.voiceMode !== 'upload') throw new Error('请先输入文案。');
  if (step >= 1 && scriptMode === 'batch' && !data.tasks.some(item => item.text)) throw new Error('请至少输入一条批量文案。');
  if (step >= 2) {
    if (data.voiceMode === 'upload') {
      if (!data.customAudio) throw new Error('请先上传你的录音文件。');
    } else {
      const voice = selectedVoice();
      if (!voice) throw new Error('请先选择一个声音。');
      if (voice.provider === 'local' && voice.status !== 'ready') throw new Error('这个声音还没有克隆完成。');
      if (data.voiceMode === 'local' && !data.promptAudio) throw new Error('请选择参考声音。');
      if (data.voiceMode === 'elevenlabs' && !data.voiceId) {
        throw new Error('这个云端声音缺少 Voice ID，请先完成设置。');
      }
      if (data.voiceMode === 'elevenlabs') {
        const compatible = compatibleElevenAccounts(voice);
        if (!compatible.length) {
          throw new Error('还没有可调用这个声音的 API 账号，请先绑定账号并同步声音。');
        }
        if (data.elevenAccountId && !compatible.some(account => account.id === data.elevenAccountId)) {
          throw new Error('当前选择的 API 账号不能调用这个声音，请重新选择。');
        }
      }
    }
  }
  if (step >= 3 && !data.avatarVideo) throw new Error('请选择数字人素材视频。');
  if (step >= 3 && !data.outputDir) throw new Error('请选择保存位置。');
  return data;
}

function updateSummary() {
  const data = collectData();
  const filledTasks = data.tasks.filter(item => item.text);
  const compactText = data.text.replace(/\s+/g, ' ') || '尚未输入';
  document.querySelector('#summaryText').textContent = scriptMode === 'batch'
    ? `批量生成 · ${filledTasks.length} 条文案`
    : `${data.videoTitle || '无标题'} · ${compactText}`;
  const voice = selectedVoice();
  const voiceAccount = elevenAccountById(data.elevenAccountId);
  document.querySelector('#summaryVoice').textContent = voiceMode === 'upload'
    ? `自己录音${customAudioName ? ` · ${customAudioName}` : ' · 未上传'}`
    : voice
    ? `${voice.name} · ${voice.provider === 'local'
        ? '本地克隆'
        : `ElevenLabs · ${voiceAccount?.name || '自动账号'} · ${elevenGenerationMode().name}`}`
    : '尚未选择';
  document.querySelector('#summaryAvatar').textContent = `${data.quality === 'v2' ? '高清模式' : '普通模式'} · ${selectedAvatar()?.name || basename(data.avatarVideo)}`;
  document.querySelector('#summaryResolution').textContent = ({ source: '保持原视频', '2k': '2K（长边 2560）', '4k': '4K（长边 3840）' })[data.resolution];
  const fontLabel = ui.textFont.options[ui.textFont.selectedIndex]?.text || '东方大楷';
  const shadowLabel = ui.textShadow.options[ui.textShadow.selectedIndex]?.text || '标准阴影';
  const titleLabel = data.videoTitle ? `标题“${data.videoTitle}”` : '无标题';
  const nameplateLabel = data.nameplateEnabled && data.speakerName ? `人名条“${data.speakerName}”` : '无人名条';
  document.querySelector('#summaryTextOverlay').textContent = `${titleLabel} · ${data.subtitleEnabled ? '自动字幕' : '无字幕'} · ${nameplateLabel} · ${fontLabel} · ${shadowLabel}`;
  document.querySelector('#summaryBroll').textContent = data.brollEnabled
    ? '自动匹配 · 4–7 秒 · 全屏 · 素材静音'
    : '不插入素材';
  if (scriptMode === 'batch') {
    const musicCount = filledTasks.filter(item => item.musicId).length;
    document.querySelector('#summaryMusic').textContent = `${musicCount}/${filledTasks.length} 条已选择 · 音量 ${data.musicVolume}%`;
  } else {
    document.querySelector('#summaryMusic').textContent = data.musicId
      ? `${musicById(data.musicId)?.name || '已选择音乐'} · 音量 ${data.musicVolume}%`
      : '不加音乐';
  }
  document.querySelector('#summaryOutput').textContent = data.outputDir || '尚未选择';
}

function setScriptMode(mode) {
  scriptMode = mode === 'batch' ? 'batch' : 'single';
  document.querySelectorAll('[data-script-mode]').forEach(button => {
    button.classList.toggle('is-selected', button.dataset.scriptMode === scriptMode);
  });
  ui.singleScriptArea.classList.toggle('is-hidden', scriptMode !== 'single');
  ui.batchScriptArea.classList.toggle('is-hidden', scriptMode !== 'batch');
}

async function pick(kind, target) {
  if (kind === 'folder' && target === 'outputDir') {
    openOutputPathModal();
    return;
  }
  const button = document.querySelector(`[data-pick="${kind}"][data-target="${target}"]`);
  if (button) button.disabled = true;
  try {
    const result = await api('/api/pick', {
      method: 'POST',
      body: JSON.stringify({ kind }),
    });
    if (!result.cancelled && result.path) document.querySelector(`#${target}`).value = result.path;
  } catch (error) {
    showToast(error.message);
  } finally {
    if (button) button.disabled = false;
  }
}

function openOutputPathModal() {
  ui.outputPathInput.value = ui.outputDir.value || defaultOutputPath;
  ui.outputPathModal.classList.remove('is-hidden');
  ui.outputPathInput.focus();
  ui.outputPathInput.select();
}

function closeOutputPathModal() {
  ui.outputPathModal.classList.add('is-hidden');
}

async function browseOutputFolder() {
  ui.browseOutputPath.disabled = true;
  ui.browseOutputPath.textContent = '正在打开';
  try {
    const result = await api('/api/pick', {
      method: 'POST',
      body: JSON.stringify({ kind: 'folder' }),
    });
    if (!result.cancelled && result.path) ui.outputPathInput.value = result.path;
  } catch (error) {
    showToast(`${error.message} 也可以直接输入完整路径。`);
  } finally {
    ui.browseOutputPath.disabled = false;
    ui.browseOutputPath.textContent = '浏览文件夹';
  }
}

async function saveOutputFolder() {
  ui.saveOutputPath.disabled = true;
  try {
    const result = await api('/api/output-folder/validate', {
      method: 'POST',
      body: JSON.stringify({ path: ui.outputPathInput.value }),
    });
    ui.outputDir.value = result.path;
    closeOutputPathModal();
    scheduleDraftSave();
    showToast('视频保存位置已更新。');
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.saveOutputPath.disabled = false;
  }
}

function importText() {
  ui.textUpload.value = '';
  ui.textUpload.click();
}

async function handleTextUpload() {
  const file = ui.textUpload.files?.[0];
  if (!file) return;
  try {
    ui.script.value = await file.text();
    ui.charCount.textContent = `${ui.script.value.length} 字`;
  } catch (error) {
    showToast(error.message);
  }
}

function brollStatusLabel(mode) {
  return ({ ready: '可自动调用', review: '需审核', disabled: '暂不调用' })[mode] || '需审核';
}

function closeBrollPreview() {
  ui.brollPreviewVideo.pause();
  ui.brollPreviewVideo.removeAttribute('src');
  ui.brollPreviewVideo.load();
  ui.brollPreviewModal.classList.add('is-hidden');
}

function openBrollPreview(asset) {
  ui.brollPreviewTitle.textContent = asset.summary || asset.name;
  ui.brollPreviewVideo.src = `${asset.videoUrl}&t=${Date.now()}`;
  ui.brollPreviewMeta.textContent = `${asset.category} · ${musicDurationLabel(asset.duration)} · ${asset.tags.join('、')}`;
  ui.brollPreviewModal.classList.remove('is-hidden');
  ui.brollPreviewVideo.play().catch(() => {});
}

function openBrollEditor(asset) {
  brollEditTargetId = asset.id;
  ui.brollEditName.value = asset.name || '';
  ui.brollEditCategory.value = asset.category || '';
  ui.brollEditTags.value = (asset.tags || []).join('、');
  ui.brollEditStatus.value = asset.useMode || 'review';
  fillPersonSelect(ui.brollEditPerson, asset.personId || '');
  ui.brollEditModal.classList.remove('is-hidden');
  ui.brollEditName.focus();
}

function closeBrollEditor() {
  brollEditTargetId = null;
  ui.brollEditModal.classList.add('is-hidden');
}

async function saveBrollEditor() {
  if (!brollEditTargetId) return;
  ui.saveBrollEdit.disabled = true;
  try {
    await api('/api/broll/update', {
      method: 'POST',
      body: JSON.stringify({
        id: brollEditTargetId,
        name: ui.brollEditName.value,
        category: ui.brollEditCategory.value,
        tags: ui.brollEditTags.value,
        useMode: ui.brollEditStatus.value,
      }),
    });
    await api('/api/asset/set-person', {
      method: 'POST',
      body: JSON.stringify({ kind: 'broll', id: brollEditTargetId, personId: ui.brollEditPerson.value }),
    });
    closeBrollEditor();
    await loadBrollLibrary();
    showToast('B-roll 素材信息已更新。');
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.saveBrollEdit.disabled = false;
  }
}

async function removeBrollAsset(asset) {
  const note = asset.uploaded
    ? '上传到素材库中的副本会同时移除。'
    : '只会从素材库索引中移除，不会删除原始文件。';
  if (!window.confirm(`确定删除 B-roll 素材“${asset.name}”吗？\n${note}`)) return;
  try {
    await api('/api/broll/delete', {
      method: 'POST',
      body: JSON.stringify({ id: asset.id }),
    });
    await loadBrollLibrary();
    showToast('B-roll 素材已删除。');
  } catch (error) {
    showToast(error.message);
  }
}

function renderBrollLibrary() {
  const query = ui.brollSearch.value.trim().toLocaleLowerCase();
  const category = ui.brollCategory.value;
  const status = ui.brollStatus.value;
  const personFilter = ui.brollPersonFilter ? ui.brollPersonFilter.value : '';
  const filtered = brollAssets.filter(asset => {
    const searchable = [asset.name, asset.summary, asset.category, ...(asset.tags || [])]
      .join(' ').toLocaleLowerCase();
    return (!query || searchable.includes(query))
      && (!category || asset.category === category)
      && (!status || asset.useMode === status)
      && (!personFilter
        || (personFilter === '__ungrouped__'
          ? !knownPersonId(asset.personId)
          : asset.personId === personFilter));
  });
  ui.brollLibraryGrid.replaceChildren();
  if (!filtered.length) {
    const empty = document.createElement('div');
    empty.className = 'broll-library-empty';
    empty.textContent = brollAssets.length ? '没有符合条件的素材' : '素材库还没有内容';
    ui.brollLibraryGrid.appendChild(empty);
    return;
  }
  filtered.forEach(asset => {
    const card = document.createElement('article');
    card.className = 'broll-library-card';
    const poster = document.createElement('div');
    poster.className = 'broll-library-poster';
    poster.tabIndex = 0;
    poster.setAttribute('role', 'button');
    poster.setAttribute('aria-label', `预览 ${asset.name}`);
    poster.addEventListener('click', () => openBrollPreview(asset));
    poster.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openBrollPreview(asset);
      }
    });
    const image = document.createElement('img');
    image.src = asset.posterUrl;
    image.alt = asset.summary || asset.name;
    image.loading = 'lazy';
    const state = document.createElement('span');
    state.className = `broll-state is-${asset.useMode}`;
    state.textContent = brollStatusLabel(asset.useMode);
    const duration = document.createElement('span');
    duration.className = 'broll-duration';
    duration.textContent = musicDurationLabel(asset.duration);
    const hoverActions = document.createElement('div');
    hoverActions.className = 'broll-hover-actions';
    const previewAction = document.createElement('button');
    previewAction.type = 'button';
    previewAction.textContent = '预览';
    previewAction.addEventListener('click', event => {
      event.stopPropagation();
      openBrollPreview(asset);
    });
    const editAction = document.createElement('button');
    editAction.type = 'button';
    editAction.textContent = '编辑';
    editAction.addEventListener('click', event => {
      event.stopPropagation();
      openBrollEditor(asset);
    });
    const deleteAction = document.createElement('button');
    deleteAction.type = 'button';
    deleteAction.className = 'is-danger';
    deleteAction.textContent = '删除';
    deleteAction.addEventListener('click', event => {
      event.stopPropagation();
      removeBrollAsset(asset);
    });
    hoverActions.append(previewAction, editAction, deleteAction);
    poster.append(image, state, duration, hoverActions);

    const content = document.createElement('div');
    content.className = 'broll-library-content';
    const name = document.createElement('strong');
    name.textContent = asset.name;
    name.title = asset.name;
    const categoryLabel = document.createElement('span');
    categoryLabel.className = 'broll-category-label';
    const personLabel = knownPersonId(asset.personId) ? personName(asset.personId) : '';
    categoryLabel.textContent = [asset.category, personLabel, asset.uploaded ? '用户上传' : '']
      .filter(Boolean).join(' · ');
    const summary = document.createElement('p');
    summary.className = 'broll-summary';
    summary.textContent = asset.summary;
    const tags = document.createElement('div');
    tags.className = 'broll-tags';
    (asset.tags || []).slice(0, 6).forEach(value => {
      const tag = document.createElement('span');
      tag.textContent = value;
      tags.appendChild(tag);
    });
    content.append(name, categoryLabel, summary, tags);
    card.append(poster, content);
    ui.brollLibraryGrid.appendChild(card);
  });
}

async function loadBrollLibrary() {
  const result = await api('/api/broll');
  brollAssets = Array.isArray(result.assets) ? result.assets : [];
  ui.brollLibraryCount.textContent = `${brollAssets.length} 条素材`;
  ui.brollUsableCount.textContent = `${Number(result.usable) || 0} 条可自动调用`;
  const selectedCategory = ui.brollCategory.value;
  ui.brollCategory.replaceChildren();
  const all = document.createElement('option');
  all.value = '';
  all.textContent = '全部分类';
  ui.brollCategory.appendChild(all);
  (result.categories || []).forEach(value => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    ui.brollCategory.appendChild(option);
  });
  if ([...ui.brollCategory.options].some(option => option.value === selectedCategory)) {
    ui.brollCategory.value = selectedCategory;
  }
  renderBrollLibrary();
}

function openBrollUpload() {
  ui.brollUpload.value = '';
  ui.brollUpload.click();
}

async function handleBrollUpload() {
  const files = [...(ui.brollUpload.files || [])];
  if (!files.length) return;
  ui.addBroll.disabled = true;
  ui.brollUploadProgress.classList.remove('is-hidden');
  try {
    for (let index = 0; index < files.length; index += 1) {
      const file = files[index];
      ui.brollUploadProgress.textContent = `正在上传 ${index + 1}/${files.length}：${file.name}`;
      await uploadApi('/api/broll/upload', file, {}, progress => {
        ui.brollUploadProgress.textContent = progress >= 100
          ? `正在识别画面、分类并建立标签：${file.name}`
          : `正在上传 ${index + 1}/${files.length}：${file.name} · ${progress}%`;
      });
    }
    await loadBrollLibrary();
    ui.brollUploadProgress.textContent = `已完成 ${files.length} 条素材的分类和索引。`;
    showToast('素材已上传并自动分类。');
    setTimeout(() => ui.brollUploadProgress.classList.add('is-hidden'), 3200);
  } catch (error) {
    ui.brollUploadProgress.textContent = error.message;
    showToast(error.message);
  } finally {
    ui.addBroll.disabled = false;
    ui.brollUpload.value = '';
  }
}

function musicDurationLabel(seconds) {
  const total = Math.max(0, Math.round(Number(seconds) || 0));
  const minutes = Math.floor(total / 60);
  return `${minutes}:${String(total % 60).padStart(2, '0')}`;
}

function fillMusicSelect(select, query = '') {
  const selected = select.value;
  const normalized = query.trim().toLocaleLowerCase();
  const tracks = musicLibrary.filter(track => !normalized || track.name.toLocaleLowerCase().includes(normalized));
  select.replaceChildren();
  const empty = document.createElement('option');
  empty.value = '';
  empty.textContent = tracks.length || !normalized ? '不加音乐' : '没有匹配的音乐';
  select.appendChild(empty);
  tracks.forEach(track => {
    const option = document.createElement('option');
    option.value = track.id;
    option.textContent = `${track.name} · ${musicDurationLabel(track.duration)}`;
    select.appendChild(option);
  });
  if (selected && musicLibrary.some(track => track.id === selected)) {
    if (![...select.options].some(option => option.value === selected)) {
      const track = musicById(selected);
      const option = document.createElement('option');
      option.value = track.id;
      option.textContent = `${track.name} · ${musicDurationLabel(track.duration)}`;
      select.appendChild(option);
    }
    select.value = selected;
  }
}

function refreshMusicPickers() {
  ui.musicLibraryCount.textContent = `${musicLibrary.length} 首`;
  fillMusicSelect(ui.singleMusicSelect, ui.singleMusicSearch.value);
  ui.batchMusicSelects.forEach((select, index) => {
    fillMusicSelect(select, ui.batchMusicSearches[index]?.value || '');
    if (ui.batchMusicPreviewButtons[index]) {
      ui.batchMusicPreviewButtons[index].disabled = !select.value;
    }
  });
}

async function loadMusicLibrary() {
  const result = await api('/api/music');
  musicLibrary = Array.isArray(result.music) ? result.music : [];
  refreshMusicPickers();
}

function openMusicUpload() {
  ui.musicUpload.value = '';
  ui.musicUpload.click();
}

async function handleMusicUpload() {
  const files = [...(ui.musicUpload.files || [])];
  if (!files.length) return;
  ui.addMusic.disabled = true;
  try {
    for (let index = 0; index < files.length; index += 1) {
      const file = files[index];
      showToast(`正在上传音乐 ${index + 1}/${files.length}：${file.name}`);
      await uploadApi('/api/music/upload', file, { name: file.name.replace(/\.[^.]+$/, '') });
    }
    await loadMusicLibrary();
    showToast(`已加入 ${files.length} 首音乐。`);
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.addMusic.disabled = false;
    ui.musicUpload.value = '';
  }
}

function playMusicTrack(track) {
  if (!track) {
    showToast('请先选择一首音乐。');
    return;
  }
  ui.musicPreview.src = `${track.audioUrl}&t=${Date.now()}`;
  ui.musicPreview.classList.remove('is-hidden');
  ui.musicPreview.play().catch(() => {});
}

function previewSelectedMusic() {
  playMusicTrack(musicById(ui.singleMusicSelect.value));
}

function previewBatchMusic(index) {
  playMusicTrack(musicById(ui.batchMusicSelects[index]?.value || ''));
}

function elevenAccountById(accountId) {
  return elevenConfig.accounts.find(account => account.id === accountId) || null;
}

function elevenModelById(modelId) {
  return elevenConfig.models.find(model => model.modelId === modelId) || null;
}

function accountCanCallVoice(account, voice) {
  if (!account || !voice || voice.provider !== 'elevenlabs') return false;
  if (!account.enabled || account.status !== 'ready' || !account.hasKey) return false;
  return (account.voices || []).some(item => item.voiceId === voice.voiceId);
}

function compatibleElevenAccounts(voice = selectedVoice()) {
  return elevenConfig.accounts.filter(account => accountCanCallVoice(account, voice));
}

function updateWorkbenchAccountHint() {
  const voice = selectedVoice();
  const compatible = compatibleElevenAccounts(voice);
  const selected = elevenAccountById(selectedElevenAccountId);
  ui.workbenchElevenAccountHint.classList.remove('is-ready', 'is-warning');
  if (!voice || voice.provider !== 'elevenlabs') {
    ui.workbenchElevenAccountHint.textContent = '选择云端声音后设置本次调用账号';
  } else if (!compatible.length) {
    ui.workbenchElevenAccountHint.textContent = '没有账号拥有这个声音，请先在后台同步或添加声音';
    ui.workbenchElevenAccountHint.classList.add('is-warning');
  } else if (selected && accountCanCallVoice(selected, voice)) {
    ui.workbenchElevenAccountHint.textContent = `本条任务将使用“${selected.name}”调用；加入队列后不会改变`;
    ui.workbenchElevenAccountHint.classList.add('is-ready');
  } else {
    ui.workbenchElevenAccountHint.textContent = `将从 ${compatible.length} 个兼容账号中自动选择；也可以手动指定`;
    ui.workbenchElevenAccountHint.classList.add('is-ready');
  }
}

function renderWorkbenchElevenAccounts(preferredId = selectedElevenAccountId) {
  const voice = selectedVoice();
  const compatible = compatibleElevenAccounts(voice);
  ui.workbenchElevenAccount.replaceChildren(new Option('自动选择兼容账号', ''));
  elevenConfig.accounts.forEach(account => {
    const usable = compatible.some(item => item.id === account.id);
    const suffix = usable
      ? ` · ${accountStatusText(account)}`
      : account.status === 'ready'
        ? ' · 没有这个声音'
        : ` · ${accountStatusText(account)}`;
    const option = new Option(`${account.name}${suffix}`, account.id);
    option.disabled = !usable;
    ui.workbenchElevenAccount.appendChild(option);
  });
  const requested = String(preferredId || '');
  selectedElevenAccountId = compatible.some(account => account.id === requested) ? requested : '';
  ui.workbenchElevenAccount.value = selectedElevenAccountId;
  ui.workbenchElevenAccount.disabled = !compatible.length;
  updateWorkbenchAccountHint();
}

function setWorkbenchElevenAccount(accountId, save = true) {
  const voice = selectedVoice();
  const compatible = compatibleElevenAccounts(voice);
  const requested = String(accountId || '');
  selectedElevenAccountId = compatible.some(account => account.id === requested) ? requested : '';
  ui.workbenchElevenAccount.value = selectedElevenAccountId;
  updateWorkbenchAccountHint();
  if (ui.currentVoiceMeta && voice?.provider === 'elevenlabs') {
    const account = elevenAccountById(selectedElevenAccountId);
    ui.currentVoiceMeta.textContent = `${account?.name || '自动选择账号'} · ${elevenGenerationMode().name}`;
  }
  updateSummary();
  if (save && appReady) scheduleDraftSave();
}

function accountStatusText(account) {
  if (!account?.hasKey) return '待绑定 API';
  if (account.status === 'ready') {
    const subscription = account.subscription || {};
    const used = Number(subscription.characterCount) || 0;
    const limit = Number(subscription.characterLimit) || 0;
    // payg（按量付费）超出基础配额后走付费 credits，limit-used 不代表真实余额
    if (subscription.tier === 'payg' || subscription.allowedToExtend) {
      return `按量付费 · 本月已用 ${used.toLocaleString()} 字符`;
    }
    if (limit > 0) {
      const remaining = Math.max(0, limit - used);
      return `可用 · 余量 ${remaining.toLocaleString()} 字符`;
    }
    return '连接正常';
  }
  if (account.status === 'error') return account.error || '连接异常';
  return '等待检测';
}

function renderElevenConfig() {
  ui.elevenAccountStrip.replaceChildren();
  if (!elevenConfig.accounts.length) {
    const empty = document.createElement('span');
    empty.className = 'eleven-account-empty';
    empty.textContent = '还没有账号，可以先建立空档案，以后再填写 API Key。';
    ui.elevenAccountStrip.appendChild(empty);
    ui.elevenSummary.textContent = '尚未绑定 API，不影响本地声音使用';
  } else {
    elevenConfig.accounts.forEach(account => {
      const pill = document.createElement('span');
      pill.className = `eleven-account-pill${account.status === 'ready' ? ' is-ready' : account.status === 'error' ? ' is-error' : ''}`;
      const name = document.createElement('b');
      name.textContent = account.name;
      const status = document.createElement('span');
      status.textContent = accountStatusText(account);
      pill.append(name, status);
      ui.elevenAccountStrip.appendChild(pill);
    });
    ui.elevenSummary.textContent = elevenConfig.readyAccounts
      ? `${elevenConfig.accounts.length} 个账号 · ${elevenConfig.readyAccounts} 个可用 · 支持自动选择`
      : `${elevenConfig.accounts.length} 个账号档案 · 尚无可用 API`;
  }
  renderAccountManager();
}

async function loadElevenConfig() {
  const result = await api('/api/elevenlabs/config');
  elevenConfig = {
    accounts: Array.isArray(result.accounts) ? result.accounts : [],
    models: Array.isArray(result.models) ? result.models : [],
    generationModes: Array.isArray(result.generationModes) ? result.generationModes : [],
    outputFormats: Array.isArray(result.outputFormats) ? result.outputFormats : [],
    readyAccounts: Number(result.readyAccounts || 0),
  };
  renderElevenConfig();
  if (voices.length) {
    renderVoices();
    if (selectedVoice()?.provider === 'elevenlabs') {
      setVoiceMode('elevenlabs');
      renderWorkbenchElevenAccounts(selectedElevenAccountId || selectedVoice()?.accountId || '');
    }
  }
  autoSyncStaleElevenAccounts();
}

let elevenAutoSyncRunning = false;

// 后台静默刷新超过 30 分钟没同步过的账号额度，避免本地记账虚高造成的陈旧显示
async function autoSyncStaleElevenAccounts() {
  if (elevenAutoSyncRunning) return;
  const staleMs = 30 * 60 * 1000;
  const now = Date.now();
  const stale = elevenConfig.accounts.filter(account => {
    if (!account.hasKey || account.status === 'error') return false;
    if (account.status === 'unchecked') return true;
    const checkedAt = Date.parse(String(account.lastCheckedAt || '').replace(' ', 'T'));
    return !Number.isFinite(checkedAt) || now - checkedAt > staleMs;
  });
  if (!stale.length) return;
  elevenAutoSyncRunning = true;
  try {
    for (const account of stale) {
      try {
        const result = await api('/api/elevenlabs/account/sync', {
          method: 'POST', body: JSON.stringify({ id: account.id }),
        });
        elevenConfig = { ...elevenConfig, ...result };
      } catch { /* 后台刷新失败不影响使用，下次进入工作台再试 */ }
    }
    renderElevenConfig();
    if (voices.length) {
      renderVoices();
      if (selectedVoice()?.provider === 'elevenlabs') {
        renderWorkbenchElevenAccounts(selectedElevenAccountId);
        setElevenGenerationMode(selectedElevenGenerationMode, false);
      }
    }
  } finally {
    elevenAutoSyncRunning = false;
  }
}

function resetElevenAccountEditor() {
  ui.elevenAccountId.value = '';
  ui.elevenAccountName.value = '';
  ui.elevenApiKey.value = '';
  ui.elevenApiKey.placeholder = '暂时没有可以留空，以后再补';
  ui.elevenAccountPriority.value = '10';
  ui.elevenAccountEnabled.checked = true;
  renderAccountManager();
  ui.elevenAccountName.focus();
}

function editElevenAccount(accountId) {
  const account = elevenAccountById(accountId);
  if (!account) return;
  ui.elevenAccountId.value = account.id;
  ui.elevenAccountName.value = account.name;
  ui.elevenApiKey.value = '';
  ui.elevenApiKey.placeholder = account.hasKey
    ? `已安全保存 · 末尾 ${account.keyPreview || '****'}；留空保持不变`
    : '输入 API Key，或暂时留空';
  ui.elevenAccountPriority.value = String(account.priority || 10);
  if (![...ui.elevenAccountPriority.options].some(option => option.value === ui.elevenAccountPriority.value)) {
    ui.elevenAccountPriority.value = '10';
  }
  ui.elevenAccountEnabled.checked = account.enabled !== false;
  renderAccountManager();
}

function renderAccountManager() {
  if (!ui.elevenAccountList) return;
  ui.elevenAccountList.replaceChildren();
  if (!elevenConfig.accounts.length) {
    const empty = document.createElement('div');
    empty.className = 'account-manager-empty';
    empty.textContent = '还没有账号档案。填写下方名称即可先保存，API Key 可以以后再补。';
    ui.elevenAccountList.appendChild(empty);
    return;
  }
  elevenConfig.accounts.forEach(account => {
    const item = document.createElement('div');
    item.className = `account-manager-item${ui.elevenAccountId.value === account.id ? ' is-selected' : ''}`;
    const name = document.createElement('strong');
    name.textContent = account.name;
    const meta = document.createElement('small');
    meta.textContent = accountStatusText(account);
    const actions = document.createElement('div');
    actions.className = 'voice-card-actions';
    const editButton = document.createElement('button');
    editButton.type = 'button';
    editButton.className = 'voice-text-button';
    editButton.textContent = '编辑';
    editButton.addEventListener('click', () => editElevenAccount(account.id));
    const syncButton = document.createElement('button');
    syncButton.type = 'button';
    syncButton.className = 'voice-text-button';
    syncButton.textContent = '检测';
    syncButton.disabled = !account.hasKey;
    syncButton.addEventListener('click', () => syncElevenAccount(account));
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'voice-text-button is-danger';
    deleteButton.textContent = '删除';
    deleteButton.addEventListener('click', () => removeElevenAccount(account));
    actions.append(editButton, syncButton, deleteButton);
    item.append(name, meta, actions);
    ui.elevenAccountList.appendChild(item);
  });
}

function openElevenAccountModal(accountId = '') {
  ui.elevenAccountModal.classList.remove('is-hidden');
  if (accountId && elevenAccountById(accountId)) editElevenAccount(accountId);
  else resetElevenAccountEditor();
}

function closeElevenAccountModal() {
  ui.elevenAccountModal.classList.add('is-hidden');
}

async function saveElevenAccount() {
  const name = ui.elevenAccountName.value.trim();
  if (!name) {
    showToast('请输入账号名称。');
    return;
  }
  ui.saveElevenAccount.disabled = true;
  try {
    const result = await api('/api/elevenlabs/account/save', {
      method: 'POST',
      body: JSON.stringify({
        id: ui.elevenAccountId.value,
        name,
        apiKey: ui.elevenApiKey.value.trim(),
        priority: Number(ui.elevenAccountPriority.value),
        enabled: ui.elevenAccountEnabled.checked,
        testConnection: true,
      }),
    });
    elevenConfig = { ...elevenConfig, ...result };
    renderElevenConfig();
    editElevenAccount(result.account.id);
    await loadVoices(selectedVoiceId);
    showToast(result.warning ? `账号已保存，但检测未通过：${result.warning}` : (result.account.hasKey ? '账号已保存并连接成功。' : '账号档案已保存，API Key 可以以后再补。'));
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.saveElevenAccount.disabled = false;
  }
}

async function syncElevenAccount(account) {
  try {
    const result = await api('/api/elevenlabs/account/sync', {
      method: 'POST', body: JSON.stringify({ id: account.id }),
    });
    elevenConfig = { ...elevenConfig, ...result };
    renderElevenConfig();
    editElevenAccount(account.id);
    await loadVoices(selectedVoiceId);
    showToast('账号、额度、模型和声音列表已刷新。');
  } catch (error) {
    await loadElevenConfig().catch(() => {});
    renderAccountManager();
    showToast(error.message);
  }
}

async function removeElevenAccount(account) {
  if (!window.confirm(`确定删除账号档案“${account.name}”吗？`)) return;
  try {
    const result = await api('/api/elevenlabs/account/delete', {
      method: 'POST', body: JSON.stringify({ id: account.id }),
    });
    elevenConfig = { ...elevenConfig, ...result };
    resetElevenAccountEditor();
    renderElevenConfig();
    await loadVoices(selectedVoiceId);
    showToast('账号档案已删除。');
  } catch (error) {
    showToast(error.message);
  }
}

function setVoiceMode(mode) {
  voiceMode = mode;
  ui.cloudFields.classList.toggle('is-hidden', mode !== 'elevenlabs');
  const isUpload = mode === 'upload';
  document.querySelector('.voice-speed-field')?.classList.toggle('is-hidden', isUpload);
  ui.previewButton?.classList.toggle('is-hidden', isUpload);
  if (mode === 'elevenlabs') {
    renderWorkbenchElevenAccounts(selectedElevenAccountId || selectedVoice()?.accountId || '');
  }
  ui.audioPreview.classList.add('is-hidden');
  ui.audioPreview.removeAttribute('src');
}

// "自己录音"模式：不选任何声音模型，整条任务直接用用户上传的朗读音频
function setUploadVoiceMode() {
  selectedVoiceId = null;
  localStorage.removeItem('localDhVoiceId');
  setVoiceMode('upload');
  renderVoiceEngineParams(null);
  if (ui.currentVoiceMeta) {
    ui.currentVoiceMeta.textContent = customAudioName
      ? `自己录音 · ${customAudioName}`
      : '自己录音 · 还没有上传文件';
  }
  if (customAudioPath && ui.customAudioPreview) {
    ui.customAudioName.textContent = customAudioName;
    ui.customAudioPreview.src = `/api/media?path=${encodeURIComponent(customAudioPath)}&t=${Date.now()}`;
    ui.customAudioPreview.classList.remove('is-hidden');
  }
  syncWorkbenchVoiceSelects();
  updateSummary();
  if (appReady) scheduleDraftSave();
}

function setQuality(value) {
  quality = value;
  document.querySelectorAll('[data-quality]').forEach(button => {
    button.classList.toggle('is-selected', button.dataset.quality === value);
  });
  ui.sourceResolutionChoice.classList.toggle('is-hidden', quality === 'v2');
  if (quality === 'v2' && !['2k', '4k'].includes(resolution)) setResolution('4k');
  if (appReady) scheduleDraftSave();
}

function setResolution(value) {
  const requested = ['source', '2k', '4k'].includes(value) ? value : '4k';
  resolution = quality === 'v2' && requested === 'source' ? '4k' : requested;
  document.querySelectorAll('[data-resolution]').forEach(button => {
    button.classList.toggle('is-selected', button.dataset.resolution === resolution);
  });
  if (appReady) scheduleDraftSave();
}

function renderVoices() {
  ui.voiceGrid.replaceChildren();
  if (!voices.length) {
    const empty = document.createElement('div');
    empty.className = 'voice-empty';
    empty.textContent = '还没有保存的声音';
    ui.voiceGrid.appendChild(empty);
    return;
  }
  voicesByPerson().forEach(group => {
    const section = document.createElement('section');
    section.className = 'library-person-section';
    const head = document.createElement('div');
    head.className = 'library-person-head';
    const title = document.createElement('strong');
    title.textContent = group.name;
    const count = document.createElement('span');
    count.textContent = `${group.items.length} 个声音`;
    head.append(title, count);
    const grid = document.createElement('div');
    grid.className = 'voice-grid';
    group.items.forEach(voice => {
    const compatibleAccounts = compatibleElevenAccounts(voice);
    const cloudUnavailable = voice.provider === 'elevenlabs' && !compatibleAccounts.length;
    const card = document.createElement('div');
    card.className = `voice-card${voice.id === selectedVoiceId ? ' is-selected' : ''}${cloudUnavailable ? ' is-unavailable' : ''}`;

    const selectButton = document.createElement('button');
    selectButton.type = 'button';
    selectButton.className = 'voice-select';
    selectButton.addEventListener('click', () => {
      setVoice(voice.id);
      if (librarySelectionContext === 'voice') {
        showToast(cloudUnavailable
          ? `已选择声音“${voice.name}”，生成前还需要选择兼容 API 账号。`
          : `已选择声音“${voice.name}”。`);
        leaveLibrarySelection();
      }
    });

    const symbol = document.createElement('span');
    symbol.className = `voice-symbol ${voice.provider === 'local' ? 'is-local' : 'is-cloud'}`;
    symbol.textContent = '◖▮◗';
    const content = document.createElement('span');
    content.className = 'voice-card-content';
    const name = document.createElement('strong');
    name.textContent = voice.name;
    const provider = document.createElement('small');
    if (voice.provider === 'local') {
      const engineLabel = voice.engineName || (voice.engine === 'voxcpm' ? 'VoxCPM 2 · 本地免费' : 'IndexTTS-2 · 本地免费');
      provider.textContent = voice.status === 'pending'
        ? `${engineLabel} · 正在克隆`
        : voice.status === 'error'
          ? `${engineLabel} · 克隆失败`
          : voice.previewUrl
            ? `${engineLabel} · 已克隆`
            : `${engineLabel} · 可直接使用`;
    } else {
      const model = elevenModelById(voice.modelId);
      provider.textContent = compatibleAccounts.length
        ? `ElevenLabs 付费 · ${compatibleAccounts.length} 个 API 可调用 · ${model?.name || voice.modelId}`
        : 'ElevenLabs 付费 · 暂无兼容 API 账号';
    }
    content.append(name, provider);
    const check = document.createElement('span');
    check.className = 'voice-check';
    check.textContent = '✓';
    selectButton.append(symbol, content, check);

    const actions = document.createElement('div');
    actions.className = 'voice-card-actions';
    const listenButton = document.createElement('button');
    listenButton.type = 'button';
    listenButton.className = 'voice-text-button';
    listenButton.textContent = '试听';
    listenButton.disabled = voice.provider === 'local'
      ? voice.status !== 'ready'
      : !voice.previewUrl && !compatibleAccounts.length;
    listenButton.addEventListener('click', () => previewSavedVoice(voice));
    const settingsButton = document.createElement('button');
    settingsButton.type = 'button';
    settingsButton.className = 'voice-text-button';
    settingsButton.textContent = '设置';
    settingsButton.addEventListener('click', () => openVoiceModal(voice));
    const renameButton = document.createElement('button');
    renameButton.type = 'button';
    renameButton.className = 'voice-text-button';
    renameButton.textContent = '改名';
    renameButton.addEventListener('click', () => renameSavedVoice(voice));
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'voice-text-button is-danger';
    deleteButton.textContent = '删除';
    deleteButton.addEventListener('click', () => removeVoice(voice));
    if (voice.provider === 'elevenlabs') actions.append(settingsButton);
    actions.append(renameButton, listenButton, deleteButton);
    card.append(selectButton, actions);
    grid.appendChild(card);
    });
    section.append(head, grid);
    ui.voiceGrid.appendChild(section);
  });
}

const VOICE_PARAMS_DEFAULTS = { speed: 1, emotionWeight: 1, emotionText: '', cfgValue: 2, inferenceTimesteps: 10 };
const ELEVEN_VOICE_PARAMS_DEFAULTS = { stability: 0.5, similarityBoost: 0.75, style: 0, speakerBoost: true };

function voiceParamsKey(voiceId) {
  return `localDhVoiceParams:${voiceId}`;
}

function loadVoiceParams(voiceId) {
  try { return JSON.parse(localStorage.getItem(voiceParamsKey(voiceId)) || 'null'); } catch { return null; }
}

function saveVoiceParams() {
  const voice = selectedVoice();
  if (!voice || !voice.id) return;
  let params = null;
  if (voice.provider === 'local') {
    params = {
      speed: Number(ui.speed.value),
      emotionWeight: Number(ui.emotionWeight.value),
      emotionText: ui.emotionText.value.trim(),
      cfgValue: Number(ui.cfgValue.value),
      inferenceTimesteps: Number(ui.inferenceTimesteps.value),
    };
  } else if (voice.provider === 'elevenlabs') {
    // 云端声音的 settings 写回声音记录（见 scheduleElevenSettingsSave），这里只记语速
    params = { speed: Number(ui.speed.value) };
  }
  if (!params) return;
  try { localStorage.setItem(voiceParamsKey(voice.id), JSON.stringify(params)); } catch { /* 存储失败不影响使用 */ }
}

function setSpeedValue(value) {
  const min = Number(ui.speed.min) || 0.5;
  const max = Number(ui.speed.max) || 2.0;
  const clamped = Math.min(max, Math.max(min, Number(value) || 1));
  ui.speed.value = String(clamped);
  ui.speedValue.textContent = `${clamped.toFixed(2)}×`;
}

function updateSpeedRange(provider) {
  // ElevenLabs API 的 speed 只支持 0.7–1.2；本地引擎支持 0.5–2.0
  const isEleven = provider === 'elevenlabs';
  ui.speed.min = isEleven ? '0.7' : '0.5';
  ui.speed.max = isEleven ? '1.2' : '2.0';
  setSpeedValue(ui.speed.value);
}

function applyVoiceParams(params) {
  const merged = { ...VOICE_PARAMS_DEFAULTS, ...(params || {}) };
  setSpeedValue(merged.speed);
  ui.emotionWeight.value = String(merged.emotionWeight);
  ui.emotionWeightValue.textContent = Number(ui.emotionWeight.value).toFixed(2);
  ui.emotionText.value = String(merged.emotionText || '');
  ui.cfgValue.value = String(merged.cfgValue);
  ui.cfgValueValue.textContent = Number(ui.cfgValue.value).toFixed(1);
  ui.inferenceTimesteps.value = String(merged.inferenceTimesteps);
  ui.inferenceTimestepsValue.textContent = String(Number(ui.inferenceTimesteps.value));
}

function applyElevenVoiceParams(settings) {
  const merged = { ...ELEVEN_VOICE_PARAMS_DEFAULTS, ...(settings || {}) };
  ui.elevenStability.value = String(Math.round(merged.stability * 100));
  ui.elevenStabilityValue.textContent = `${ui.elevenStability.value}%`;
  ui.elevenSimilarity.value = String(Math.round(merged.similarityBoost * 100));
  ui.elevenSimilarityValue.textContent = `${ui.elevenSimilarity.value}%`;
  ui.elevenStyle.value = String(Math.round(merged.style * 100));
  ui.elevenStyleValue.textContent = `${ui.elevenStyle.value}%`;
  ui.elevenSpeakerBoost.checked = Boolean(merged.speakerBoost);
}

function collectElevenSettings() {
  return {
    stability: Number(ui.elevenStability.value) / 100,
    similarityBoost: Number(ui.elevenSimilarity.value) / 100,
    style: Number(ui.elevenStyle.value) / 100,
    speakerBoost: ui.elevenSpeakerBoost.checked,
  };
}

function updateElevenParamsAvailability() {
  if (!ui.elevenVoiceParams) return;
  const voice = selectedVoice();
  if (voice?.provider !== 'elevenlabs') return;
  const model = elevenModelById(elevenGenerationMode().modelId) || {};
  // v3_voice_match 是双阶段流程：稳定性/相似度被服务端强制覆盖，只有语速真正生效
  const doublePass = selectedElevenGenerationMode === 'v3_voice_match';
  const styleSupported = !doublePass && model.supportsStyle !== false;
  const boostSupported = !doublePass && model.supportsSpeakerBoost !== false;
  ui.elevenStability.disabled = doublePass;
  ui.elevenSimilarity.disabled = doublePass;
  ui.elevenStyle.disabled = !styleSupported;
  ui.elevenSpeakerBoost.disabled = !boostSupported;
  let note = '';
  if (doublePass) {
    note = '双阶段模式：稳定性与相似度由流程自动控制，只有语速会生效。';
  } else if (!styleSupported || !boostSupported) {
    note = '当前模型不支持风格强度 / 说话者增强，相关选项已停用。';
  }
  ui.elevenParamsNote.textContent = note;
}

let elevenSettingsSaveTimer = null;

function scheduleElevenSettingsSave() {
  const voice = selectedVoice();
  if (!voice || voice.provider !== 'elevenlabs' || !voice.id) return;
  voice.settings = collectElevenSettings();
  clearTimeout(elevenSettingsSaveTimer);
  elevenSettingsSaveTimer = setTimeout(() => persistElevenSettings(voice.id), 800);
}

async function persistElevenSettings(voiceId) {
  const voice = voices.find(item => item.id === voiceId);
  if (!voice || voice.provider !== 'elevenlabs') return;
  try {
    const result = await api('/api/voice/save-elevenlabs', {
      method: 'POST',
      body: JSON.stringify({
        id: voice.id,
        name: voice.name,
        voiceId: voice.voiceId,
        accountId: voice.accountId || '',
        modelId: voice.modelId || 'eleven_multilingual_v2',
        outputFormat: voice.outputFormat || 'mp3_44100_128',
        previewUrl: voice.previewUrl || '',
        settings: voice.settings,
      }),
    });
    const index = voices.findIndex(item => item.id === voiceId);
    if (index >= 0 && result.voice) voices[index] = result.voice;
  } catch (error) {
    showToast(`声音参数保存失败：${error.message}`);
  }
}

function renderVoiceEngineParams(engine) {
  if (ui.v2VoiceParams) ui.v2VoiceParams.classList.toggle('is-hidden', engine !== 'v2');
  if (ui.voxcpmVoiceParams) ui.voxcpmVoiceParams.classList.toggle('is-hidden', engine !== 'voxcpm');
}

function setVoice(voiceId, preferredAccountId = null) {
  const voice = voices.find(item => item.id === voiceId) || null;
  const previousVoice = selectedVoice();
  selectedVoiceId = voice?.id || null;
  if (voice?.provider === 'local') {
    setVoiceMode('local');
    ui.promptAudio.value = voice.samplePath || '';
    ui.promptText.value = voice.promptText || '';
    ui.voiceId.value = '';
  } else if (voice) {
    setVoiceMode('elevenlabs');
    ui.promptAudio.value = '';
    ui.promptText.value = '';
    ui.voiceId.value = voice.voiceId || '';
    setElevenGenerationMode(
      previousVoice?.id === voice.id
        ? selectedElevenGenerationMode
        : defaultElevenModeForVoice(voice),
      false,
    );
    const accountChoice = preferredAccountId !== null
      ? preferredAccountId
      : previousVoice?.id === voice.id
        ? selectedElevenAccountId
        : voice.accountId || '';
    renderWorkbenchElevenAccounts(accountChoice);
  } else {
    setVoiceMode('local');
    ui.promptAudio.value = '';
    ui.promptText.value = '';
    ui.voiceId.value = '';
  }
  if (selectedVoiceId) localStorage.setItem('localDhVoiceId', selectedVoiceId);
  else localStorage.removeItem('localDhVoiceId');
  if (voice?.provider === 'local') {
    updateSpeedRange('local');
    renderVoiceEngineParams(voice.engine || 'v2');
    const storedParams = loadVoiceParams(voice.id);
    if (storedParams) applyVoiceParams(storedParams);
  } else if (voice?.provider === 'elevenlabs') {
    updateSpeedRange('elevenlabs');
    renderVoiceEngineParams(null);
    applyElevenVoiceParams(voice.settings);
    const storedParams = loadVoiceParams(voice.id);
    if (storedParams && typeof storedParams.speed === 'number') setSpeedValue(storedParams.speed);
    updateElevenParamsAvailability();
  } else {
    updateSpeedRange('local');
    renderVoiceEngineParams(null);
  }
  if (ui.currentVoiceMeta) {
    ui.currentVoiceMeta.textContent = voice
      ? (voice.provider === 'local'
          ? `本地克隆声音 · ${voice.engineName || 'IndexTTS-2 · 本地免费'}`
          : `${elevenAccountById(selectedElevenAccountId)?.name || '自动选择账号'} · ${elevenGenerationMode().name}`)
      : '请从声音模型中选择';
  }
  syncWorkbenchVoiceSelects();
  renderVoices();
  if (appReady) scheduleDraftSave();
}

async function loadVoices(preferredId = null) {
  const result = await api('/api/voices');
  voices = Array.isArray(result.voices) ? result.voices : [];
  const saved = preferredId || localStorage.getItem('localDhVoiceId');
  const selected = voices.find(item => item.id === saved && (item.provider !== 'local' || item.status === 'ready'))
    || voices.find(item => item.provider !== 'local' || item.status === 'ready')
    || voices[0]
    || null;
  setVoice(selected?.id || null);
}

function selectedLocalVoiceMode() {
  return document.querySelector('input[name="localVoiceMode"]:checked')?.value === 'reference' ? 'reference' : 'ultimate';
}

function updateLocalVoiceModeFields() {
  const isVoxcpm = ui.localVoiceEngine.value !== 'v2';
  ui.localVoiceModeField.classList.toggle('is-hidden', !isVoxcpm);
  // v2 引擎同样支持对照文本；VoxCPM 只有极致克隆模式需要
  const showTranscript = !isVoxcpm || selectedLocalVoiceMode() === 'ultimate';
  ui.localVoiceTranscriptField.classList.toggle('is-hidden', !showTranscript);
}

function openLocalVoiceModal() {
  ui.localVoiceName.value = '';
  ui.localVoiceEngine.value = 'voxcpm';
  fillPersonSelect(ui.localVoicePerson, '');
  ui.localVoicePath.value = '';
  ui.localVoiceUpload.value = '';
  ui.localVoiceTranscript.value = '';
  const ultimateRadio = document.querySelector('input[name="localVoiceMode"][value="ultimate"]');
  if (ultimateRadio) ultimateRadio.checked = true;
  updateLocalVoiceModeFields();
  ui.transcribeLocalVoice.disabled = false;
  ui.transcribeLocalVoice.textContent = '用本地模型转写';
  localVoiceFile = null;
  localVoiceCreatedId = null;
  voiceCloneBusy = false;
  setVoiceCloneProgress(false, 0, '正在准备声音克隆');
  ui.saveLocalVoice.textContent = '开始克隆';
  ui.localVoiceModal.classList.remove('is-hidden');
  ui.localVoiceName.focus();
}

function closeLocalVoiceModal() {
  if (voiceCloneBusy) return;
  ui.localVoiceModal.classList.add('is-hidden');
}

function setVoiceCloneProgress(visible, progress = 0, stage = '') {
  const value = Math.max(0, Math.min(100, Math.round(Number(progress) || 0)));
  ui.voiceCloneProgress.classList.toggle('is-hidden', !visible);
  ui.voiceCloneStage.textContent = stage || '正在处理';
  ui.voiceCloneValue.textContent = `${value}%`;
  ui.voiceCloneFill.style.width = `${value}%`;
}

async function waitForVoiceClone() {
  while (true) {
    const job = await api('/api/job?kind=clone');
    setVoiceCloneProgress(true, job.progress, job.stage);
    if (job.status === 'done') return job;
    if (job.status === 'error') throw new Error(job.error || '声音克隆失败。');
    await new Promise(resolve => setTimeout(resolve, 1500));
  }
}

function pickLocalVoiceSample() {
  ui.localVoiceUpload.value = '';
  ui.localVoiceUpload.click();
}

function handleLocalVoiceUpload() {
  const file = ui.localVoiceUpload.files?.[0] || null;
  localVoiceFile = file;
  ui.localVoicePath.value = file?.name || '';
  if (file && !ui.localVoiceName.value.trim()) {
    ui.localVoiceName.value = file.name.replace(/\.[^.]+$/, '');
  }
}

async function saveLocalVoice() {
  const name = ui.localVoiceName.value.trim();
  const engine = ui.localVoiceEngine.value === 'v2' ? 'v2' : 'voxcpm';
  if (!localVoiceFile && !localVoiceCreatedId) {
    showToast('请先上传声音样本。');
    return;
  }
  voiceCloneBusy = true;
  ui.saveLocalVoice.disabled = true;
  ui.cancelLocalVoiceModal.disabled = true;
  ui.closeLocalVoiceModal.disabled = true;
  ui.pickLocalVoiceSample.disabled = true;
  ui.localVoiceEngine.disabled = true;
  setVoiceCloneProgress(true, 1, '正在上传声音样本');
  try {
    if (!localVoiceCreatedId) {
      const result = await uploadApi('/api/voice/upload-local', localVoiceFile, {
        name,
        engine,
        personId: ui.localVoicePerson.value,
        promptText: ui.localVoiceTranscriptField.classList.contains('is-hidden') ? '' : ui.localVoiceTranscript.value.trim(),
      }, progress => {
        setVoiceCloneProgress(true, Math.min(8, Math.max(1, progress * 0.08)), progress >= 100 ? '正在处理声音样本' : `正在上传声音样本 ${progress}%`);
      });
      voices = Array.isArray(result.voices) ? result.voices : [];
      localVoiceCreatedId = result.voice.id;
      setVoice(localVoiceCreatedId);
    } else {
      const transcriptResult = await api('/api/voice/set-transcript', {
        method: 'POST',
        body: JSON.stringify({
          id: localVoiceCreatedId,
          promptText: ui.localVoiceTranscriptField.classList.contains('is-hidden') ? '' : ui.localVoiceTranscript.value.trim(),
        }),
      });
      voices = Array.isArray(transcriptResult.voices) ? transcriptResult.voices : voices;
    }
    setVoiceCloneProgress(true, 8, '正在启动声音克隆');
    await api('/api/voice/clone', {
      method: 'POST',
      body: JSON.stringify({ id: localVoiceCreatedId }),
    });
    await waitForVoiceClone();
    await loadVoices(localVoiceCreatedId);
    setVoiceCloneProgress(true, 100, '声音克隆完成');
    voiceCloneBusy = false;
    closeLocalVoiceModal();
    showToast('声音已克隆完成，以后直接选择使用。');
    if (librarySelectionContext === 'voice') leaveLibrarySelection();
  } catch (error) {
    setVoiceCloneProgress(true, 0, error.message || '声音克隆失败');
    showToast(error.message);
  } finally {
    voiceCloneBusy = false;
    ui.saveLocalVoice.disabled = false;
    ui.cancelLocalVoiceModal.disabled = false;
    ui.closeLocalVoiceModal.disabled = false;
    ui.pickLocalVoiceSample.disabled = false;
    ui.localVoiceEngine.disabled = false;
    ui.saveLocalVoice.textContent = localVoiceCreatedId ? '重新克隆' : '开始克隆';
  }
}

let voiceTranscribeBusy = false;

// 克隆弹窗里的"用本地模型转写"：必要时先上传样本建档案，再调本地 FunASR 转写
async function transcribeLocalSample() {
  if (voiceTranscribeBusy || voiceCloneBusy) return;
  if (!localVoiceFile && !localVoiceCreatedId) {
    showToast('请先上传声音样本。');
    return;
  }
  voiceTranscribeBusy = true;
  ui.transcribeLocalVoice.disabled = true;
  try {
    if (!localVoiceCreatedId) {
      ui.transcribeLocalVoice.textContent = '正在上传样本…';
      const name = ui.localVoiceName.value.trim() || localVoiceFile.name.replace(/\.[^.]+$/, '');
      const engine = ui.localVoiceEngine.value === 'v2' ? 'v2' : 'voxcpm';
      const result = await uploadApi('/api/voice/upload-local', localVoiceFile, {
        name, engine, personId: ui.localVoicePerson.value,
      });
      voices = Array.isArray(result.voices) ? result.voices : [];
      localVoiceCreatedId = result.voice.id;
      setVoice(localVoiceCreatedId);
      ui.saveLocalVoice.textContent = '开始克隆';
    }
    ui.transcribeLocalVoice.textContent = '正在转写（首次需下载模型）…';
    const result = await api('/api/voice/transcribe', {
      method: 'POST',
      body: JSON.stringify({ voiceId: localVoiceCreatedId }),
    });
    ui.localVoiceTranscript.value = result.text || '';
    showToast('转写完成，请校对文本后再开始克隆。');
  } catch (error) {
    showToast(error.message);
  } finally {
    voiceTranscribeBusy = false;
    ui.transcribeLocalVoice.disabled = false;
    ui.transcribeLocalVoice.textContent = '用本地模型转写';
  }
}

// 改名弹窗里为已有本地声音补录对照文本
async function transcribeRenamedVoiceSample() {
  if (voiceTranscribeBusy || !renameTarget) return;
  voiceTranscribeBusy = true;
  ui.transcribeRenamedVoice.disabled = true;
  ui.transcribeRenamedVoice.textContent = '正在转写（首次需下载模型）…';
  try {
    const result = await api('/api/voice/transcribe', {
      method: 'POST',
      body: JSON.stringify({ voiceId: renameTarget.id }),
    });
    ui.renameTranscript.value = result.text || '';
    showToast('转写完成，请校对文本。');
  } catch (error) {
    showToast(error.message);
  } finally {
    voiceTranscribeBusy = false;
    ui.transcribeRenamedVoice.disabled = false;
    ui.transcribeRenamedVoice.textContent = '用本地模型转写';
  }
}

function fillCloudVoiceSelectors(voice = null) {
  const accountId = voice?.accountId || ui.cloudVoiceAccount.value || '';
  ui.cloudVoiceAccount.replaceChildren(new Option('自动选择可用账号', ''));
  elevenConfig.accounts.forEach(account => {
    const suffix = account.status === 'ready' ? ' · 可用' : account.hasKey ? ' · 异常' : ' · 待绑定 API';
    ui.cloudVoiceAccount.appendChild(new Option(`${account.name}${suffix}`, account.id));
  });
  ui.cloudVoiceAccount.value = elevenAccountById(accountId) ? accountId : '';

  const modelId = voice?.modelId || ui.cloudVoiceModel.value || 'eleven_multilingual_v2';
  ui.cloudVoiceModel.replaceChildren();
  elevenConfig.models.forEach(model => {
    const suffix = model.recommended ? ' · 推荐' : '';
    ui.cloudVoiceModel.appendChild(new Option(`${model.name}${suffix}`, model.modelId));
  });
  if (!elevenConfig.models.length) {
    ui.cloudVoiceModel.appendChild(new Option('Multilingual v2 · 推荐', 'eleven_multilingual_v2'));
  }
  ui.cloudVoiceModel.value = [...ui.cloudVoiceModel.options].some(option => option.value === modelId)
    ? modelId : 'eleven_multilingual_v2';

  const outputFormat = voice?.outputFormat || ui.cloudVoiceOutputFormat.value || 'mp3_44100_128';
  ui.cloudVoiceOutputFormat.replaceChildren();
  (elevenConfig.outputFormats.length ? elevenConfig.outputFormats : [{ id: 'mp3_44100_128', name: 'MP3 44.1kHz · 标准' }])
    .forEach(format => ui.cloudVoiceOutputFormat.appendChild(new Option(format.name, format.id)));
  ui.cloudVoiceOutputFormat.value = [...ui.cloudVoiceOutputFormat.options].some(option => option.value === outputFormat)
    ? outputFormat : 'mp3_44100_128';
  fillRemoteVoiceOptions(voice?.voiceId || ui.cloudVoiceId.value);
}

function fillRemoteVoiceOptions(preferredVoiceId = '') {
  const account = elevenAccountById(ui.cloudVoiceAccount.value);
  ui.cloudVoiceRemote.replaceChildren(new Option('手动输入 Voice ID', ''));
  (account?.voices || []).forEach(voice => {
    ui.cloudVoiceRemote.appendChild(new Option(`${voice.name}${voice.category ? ` · ${voice.category}` : ''}`, voice.voiceId));
  });
  ui.cloudVoiceRemote.value = [...ui.cloudVoiceRemote.options].some(option => option.value === preferredVoiceId)
    ? preferredVoiceId : '';
  updateCloudVoiceNote();
}

function updateCloudParameterOutputs() {
  ui.cloudStabilityValue.textContent = `${ui.cloudStability.value}%`;
  ui.cloudSimilarityValue.textContent = `${ui.cloudSimilarity.value}%`;
  ui.cloudStyleValue.textContent = `${ui.cloudStyle.value}%`;
  const model = elevenModelById(ui.cloudVoiceModel.value);
  ui.cloudStyle.disabled = model?.supportsStyle === false;
  ui.cloudSpeakerBoost.disabled = model?.supportsSpeakerBoost === false;
}

function updateCloudVoiceNote() {
  const account = elevenAccountById(ui.cloudVoiceAccount.value);
  const model = elevenModelById(ui.cloudVoiceModel.value);
  if (!account) {
    ui.cloudVoiceConfigNote.textContent = elevenConfig.readyAccounts
      ? `生成时自动选择余量较多的可用账号 · ${model?.description || ''}`
      : '没有 API 也可以保存声音参数；真正生成前需要先绑定一个可用账号。';
  } else if (account.status === 'ready') {
    ui.cloudVoiceConfigNote.textContent = `${account.name} 连接正常 · ${model?.description || '参数会固定保存在这个声音中'}`;
  } else {
    ui.cloudVoiceConfigNote.textContent = `${account.name} ${accountStatusText(account)}；配置可以先保存，生成前需要完成 API 绑定。`;
  }
}

function openVoiceModal(voice = null) {
  const editing = voice?.provider === 'elevenlabs' ? voice : null;
  ui.voiceModalTitle.textContent = editing ? '编辑 ElevenLabs 声音' : '添加 ElevenLabs 声音';
  ui.cloudVoiceRecordId.value = editing?.id || '';
  ui.cloudVoiceName.value = editing?.name || '';
  fillPersonSelect(ui.cloudVoicePerson, editing?.personId || '');
  ui.cloudVoiceId.value = editing?.voiceId || '';
  const settings = editing?.settings || { stability: .5, similarityBoost: .75, style: 0, speakerBoost: true };
  ui.cloudStability.value = String(Math.round(Number(settings.stability ?? .5) * 100));
  ui.cloudSimilarity.value = String(Math.round(Number(settings.similarityBoost ?? .75) * 100));
  ui.cloudStyle.value = String(Math.round(Number(settings.style ?? 0) * 100));
  ui.cloudSpeakerBoost.checked = settings.speakerBoost !== false;
  fillCloudVoiceSelectors(editing);
  updateCloudParameterOutputs();
  ui.voiceModal.classList.remove('is-hidden');
  ui.cloudVoiceName.focus();
}

function closeVoiceModal() {
  ui.voiceModal.classList.add('is-hidden');
}

async function saveCloudVoice() {
  const name = ui.cloudVoiceName.value.trim();
  const voiceId = ui.cloudVoiceId.value.trim();
  if (!voiceId) {
    showToast('请输入 ElevenLabs Voice ID。');
    return;
  }
  ui.saveElevenLabsVoice.disabled = true;
  try {
    const selectedRemote = elevenAccountById(ui.cloudVoiceAccount.value)?.voices
      ?.find(voice => voice.voiceId === voiceId) || null;
    const result = await api('/api/voice/save-elevenlabs', {
      method: 'POST',
      body: JSON.stringify({
        id: ui.cloudVoiceRecordId.value,
        name,
        voiceId,
        personId: ui.cloudVoicePerson.value,
        accountId: ui.cloudVoiceAccount.value,
        modelId: ui.cloudVoiceModel.value,
        outputFormat: ui.cloudVoiceOutputFormat.value,
        previewUrl: selectedRemote?.previewUrl || '',
        settings: {
          stability: Number(ui.cloudStability.value) / 100,
          similarityBoost: Number(ui.cloudSimilarity.value) / 100,
          style: Number(ui.cloudStyle.value) / 100,
          speakerBoost: ui.cloudSpeakerBoost.checked,
        },
      }),
    });
    voices = Array.isArray(result.voices) ? result.voices : [];
    setVoice(result.voice.id);
    closeVoiceModal();
    showToast(result.voice.status === 'ready'
      ? 'ElevenLabs 声音和参数已保存。'
      : '声音配置已保存；绑定可用 API 后即可生成。');
    if (librarySelectionContext === 'voice') leaveLibrarySelection();
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.saveElevenLabsVoice.disabled = false;
  }
}

async function removeVoice(voice) {
  if (!window.confirm(`确定删除声音“${voice.name}”吗？`)) return;
  try {
    const result = await api('/api/voice/delete', {
      method: 'POST',
      body: JSON.stringify({ id: voice.id }),
    });
    voices = Array.isArray(result.voices) ? result.voices : [];
    if (selectedVoiceId === voice.id) setVoice(voices[0]?.id || null);
    else renderVoices();
    showToast('声音已删除。');
  } catch (error) {
    showToast(error.message);
  }
}

async function renameSavedVoice(voice) {
  openRenameModal('voice', voice);
}

function previewSavedVoice(voice) {
  setVoice(voice.id);
  if (voice.provider === 'local' && (voice.previewUrl || voice.sampleUrl)) {
    const mediaUrl = voice.previewUrl || voice.sampleUrl;
    ui.audioPreview.src = `${mediaUrl}&t=${Date.now()}`;
    ui.audioPreview.classList.remove('is-hidden');
    ui.audioPreview.play().catch(() => {});
  } else if (voice.provider === 'elevenlabs' && voice.previewUrl) {
    ui.audioPreview.src = voice.previewUrl;
    ui.audioPreview.classList.remove('is-hidden');
    ui.audioPreview.play().catch(() => {});
  } else {
    startPreview();
  }
}

function refreshBatchAvatarPickers() {
  ui.batchAvatarPickers.forEach((button, index) => {
    const avatar = avatars.find(item => item.id === batchAvatarIds[index]) || null;
    if (!avatar && batchAvatarIds[index]) batchAvatarIds[index] = '';
    const image = button.querySelector('img');
    const label = button.querySelector('span');
    if (avatar) {
      image.src = avatar.posterUrl || '/assets/app-icon.png';
      image.alt = avatar.name;
      image.hidden = false;
      label.textContent = avatar.name;
    } else {
      image.removeAttribute('src');
      image.alt = '';
      image.hidden = true;
      label.textContent = '自动轮换数字人';
    }
  });
}

function chooseBatchAvatar(index, avatarId = '') {
  if (index < 0 || index >= batchAvatarIds.length) return;
  batchAvatarIds[index] = avatars.some(item => item.id === avatarId) ? avatarId : '';
  refreshBatchAvatarPickers();
  closeBatchAvatarPicker();
}

function renderBatchAvatarOptions() {
  ui.batchAvatarOptions.replaceChildren();
  const autoButton = document.createElement('button');
  autoButton.type = 'button';
  autoButton.className = `batch-avatar-option is-auto${batchAvatarIds[activeBatchAvatarIndex] ? '' : ' is-selected'}`;
  autoButton.textContent = '自动轮换数字人';
  autoButton.addEventListener('click', () => chooseBatchAvatar(activeBatchAvatarIndex, ''));
  ui.batchAvatarOptions.appendChild(autoButton);
  avatars.forEach(avatar => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `batch-avatar-option${batchAvatarIds[activeBatchAvatarIndex] === avatar.id ? ' is-selected' : ''}`;
    const image = document.createElement('img');
    image.src = avatar.posterUrl || '/assets/app-icon.png';
    image.alt = avatar.name;
    image.loading = 'lazy';
    const label = document.createElement('span');
    label.textContent = avatar.name;
    button.append(image, label);
    button.addEventListener('click', () => chooseBatchAvatar(activeBatchAvatarIndex, avatar.id));
    ui.batchAvatarOptions.appendChild(button);
  });
}

function openBatchAvatarPicker(index) {
  activeBatchAvatarIndex = index;
  ui.batchAvatarModalTitle.textContent = `任务 ${index + 1} · 选择数字人`;
  renderBatchAvatarOptions();
  ui.batchAvatarModal.classList.remove('is-hidden');
}

function closeBatchAvatarPicker() {
  ui.batchAvatarModal.classList.add('is-hidden');
  activeBatchAvatarIndex = -1;
}

function renderAvatars() {
  ui.avatarGrid.replaceChildren();
  if (!avatars.length) {
    const empty = document.createElement('div');
    empty.className = 'avatar-empty';
    empty.textContent = '还没有数字人形象';
    ui.avatarGrid.appendChild(empty);
    return;
  }
  avatarsByPerson().forEach(group => {
    const section = document.createElement('section');
    section.className = 'library-person-section';
    const head = document.createElement('div');
    head.className = 'library-person-head';
    const title = document.createElement('strong');
    title.textContent = group.name;
    const count = document.createElement('span');
    count.textContent = `${group.items.length} 个形象`;
    head.append(title, count);
    const grid = document.createElement('div');
    grid.className = 'avatar-grid library-avatar-grid';
    group.items.forEach(avatar => {
    const card = document.createElement('div');
    card.className = `avatar-card${avatar.id === selectedAvatarId ? ' is-selected' : ''}`;

    const selectButton = document.createElement('button');
    selectButton.type = 'button';
    selectButton.className = 'avatar-select';
    selectButton.addEventListener('click', () => {
      setAvatar(avatar.id);
      if (librarySelectionContext === 'avatar') {
        showToast(`已选择数字人“${avatar.name}”。`);
        leaveLibrarySelection();
      }
    });

    const thumb = document.createElement('span');
    thumb.className = 'avatar-thumb';
    const image = document.createElement('img');
    image.src = avatar.posterUrl || '/assets/app-icon.png';
    image.alt = avatar.name;
    image.loading = 'lazy';
    thumb.appendChild(image);
    const check = document.createElement('span');
    check.className = 'avatar-check';
    check.textContent = '✓';
    thumb.appendChild(check);

    const name = document.createElement('span');
    name.className = 'avatar-card-name';
    name.textContent = avatar.name;
    selectButton.append(thumb, name);

    const previewButton = document.createElement('button');
    previewButton.type = 'button';
    previewButton.className = 'avatar-preview-button';
    previewButton.textContent = '预览';
    previewButton.addEventListener('click', () => openAvatarPreview(avatar));
    const renameButton = document.createElement('button');
    renameButton.type = 'button';
    renameButton.className = 'avatar-rename-button';
    renameButton.textContent = '改名';
    renameButton.setAttribute('aria-label', `修改 ${avatar.name} 的名称`);
    renameButton.addEventListener('click', () => renameAvatar(avatar));
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'avatar-delete-button';
    deleteButton.textContent = '删除';
    deleteButton.setAttribute('aria-label', `删除 ${avatar.name}`);
    deleteButton.addEventListener('click', () => removeAvatar(avatar));
    card.append(selectButton, previewButton, renameButton, deleteButton);
    grid.appendChild(card);
    });
    section.append(head, grid);
    ui.avatarGrid.appendChild(section);
  });
}

function setAvatar(avatarId) {
  const avatar = avatars.find(item => item.id === avatarId) || null;
  selectedAvatarId = avatar?.id || null;
  ui.avatarVideo.value = avatar?.videoPath || '';
  if (selectedAvatarId) localStorage.setItem('localDhAvatarId', selectedAvatarId);
  else localStorage.removeItem('localDhAvatarId');
  if (ui.currentAvatarName) {
    ui.currentAvatarName.textContent = avatar?.name || '尚未选择数字人';
    ui.currentAvatarMeta.textContent = avatar
      ? `${musicDurationLabel(avatar.duration || 0)} · 随机错帧已开启`
      : '请从形象库中选择';
    ui.currentAvatarImage.src = avatar?.posterUrl || '/assets/app-icon.png';
    ui.currentAvatarImage.alt = avatar?.name || '当前数字人';
  }
  syncWorkbenchAvatarSelects();
  renderAvatars();
  if (appReady) scheduleDraftSave();
}

async function loadAvatars(preferredId = null) {
  const result = await api('/api/avatars');
  avatars = Array.isArray(result.avatars) ? result.avatars : [];
  const saved = preferredId || localStorage.getItem('localDhAvatarId');
  const selected = avatars.find(item => item.id === saved) || avatars[0] || null;
  setAvatar(selected?.id || null);
  refreshBatchAvatarPickers();
}

function importAvatar() {
  ui.avatarUpload.value = '';
  ui.avatarUpload.click();
}

async function handleAvatarUpload() {
  const file = ui.avatarUpload.files?.[0];
  if (!file) return;
  ui.addAvatar.disabled = true;
  ui.addAvatar.textContent = '上传中';
  try {
    const result = await uploadApi('/api/avatar/upload', file, { name: file.name.replace(/\.[^.]+$/, '') }, progress => {
      ui.addAvatar.textContent = progress >= 100 ? '正在处理' : `上传 ${progress}%`;
    });
    if (result.avatar) {
      avatars = Array.isArray(result.avatars) ? result.avatars : [];
      setAvatar(result.avatar.id);
      showToast('数字人形象已上传。');
      if (librarySelectionContext === 'avatar') leaveLibrarySelection();
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.addAvatar.disabled = false;
    ui.addAvatar.textContent = '上传';
  }
}

async function removeAvatar(avatar) {
  if (!window.confirm(`确定删除“${avatar.name}”吗？`)) return;
  try {
    const result = await api('/api/avatar/delete', {
      method: 'POST',
      body: JSON.stringify({ id: avatar.id }),
    });
    avatars = Array.isArray(result.avatars) ? result.avatars : [];
    if (selectedAvatarId === avatar.id) setAvatar(avatars[0]?.id || null);
    else renderAvatars();
    showToast('数字人形象已删除。');
  } catch (error) {
    showToast(error.message);
  }
}

async function renameAvatar(avatar) {
  openRenameModal('avatar', avatar);
}

function openRenameModal(type, item) {
  renameTarget = { type, id: item.id };
  ui.renameModalTitle.textContent = type === 'voice' ? '编辑声音名称' : '编辑数字人形象名称';
  ui.renameName.value = item.name || '';
  fillPersonSelect(ui.renamePersonSelect, item.personId || '');
  const isLocalVoice = type === 'voice' && item.provider === 'local';
  ui.renameTranscriptField.classList.toggle('is-hidden', !isLocalVoice);
  ui.renameTranscript.value = isLocalVoice ? (item.promptText || '') : '';
  ui.renameModal.classList.remove('is-hidden');
  ui.renameName.focus();
  ui.renameName.select();
}

function closeRenameModal() {
  ui.renameModal.classList.add('is-hidden');
  ui.renameName.value = '';
  ui.renameTranscriptField.classList.add('is-hidden');
  ui.renameTranscript.value = '';
  renameTarget = null;
}

async function saveRenamedItem() {
  if (!renameTarget) return;
  const name = ui.renameName.value.trim();
  if (!name) {
    showToast('名称不能为空。');
    ui.renameName.focus();
    return;
  }
  const { type, id } = renameTarget;
  ui.saveRename.disabled = true;
  try {
    const result = await api(type === 'voice' ? '/api/voice/rename' : '/api/avatar/rename', {
      method: 'POST',
      body: JSON.stringify({ id, name }),
    });
    await api('/api/asset/set-person', {
      method: 'POST',
      body: JSON.stringify({ kind: type, id, personId: ui.renamePersonSelect.value }),
    });
    if (type === 'voice') {
      voices = Array.isArray(result.voices) ? result.voices : [];
      const target = voices.find(item => item.id === id);
      if (target) target.personId = ui.renamePersonSelect.value;
      if (!ui.renameTranscriptField.classList.contains('is-hidden')
          && target?.provider === 'local'
          && ui.renameTranscript.value.trim() !== (target.promptText || '')) {
        const transcriptResult = await api('/api/voice/set-transcript', {
          method: 'POST',
          body: JSON.stringify({ id, promptText: ui.renameTranscript.value.trim() }),
        });
        voices = Array.isArray(transcriptResult.voices) ? transcriptResult.voices : voices;
      }
      renderVoices();
      syncWorkbenchVoiceSelects();
    } else {
      avatars = Array.isArray(result.avatars) ? result.avatars : [];
      const target = avatars.find(item => item.id === id);
      if (target) target.personId = ui.renamePersonSelect.value;
      renderAvatars();
      syncWorkbenchAvatarSelects();
    }
    updateSummary();
    closeRenameModal();
    showToast(type === 'voice' ? '声音名称已修改。' : '数字人形象名称已修改。');
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.saveRename.disabled = false;
  }
}

function openPersonModal() {
  renderPersonList();
  ui.personNameInput.value = '';
  ui.personModal.classList.remove('is-hidden');
  ui.personNameInput.focus();
}

function closePersonModal() {
  ui.personModal.classList.add('is-hidden');
}

function renderPersonList() {
  if (!ui.personList) return;
  ui.personList.replaceChildren();
  if (!persons.length) {
    const empty = document.createElement('div');
    empty.className = 'account-manager-empty';
    empty.textContent = '还没有人物。添加后可以把声音、形象和 B-roll 素材归类到人物下。';
    ui.personList.appendChild(empty);
    return;
  }
  persons.forEach(person => {
    const item = document.createElement('div');
    item.className = 'account-manager-item';
    const name = document.createElement('strong');
    name.textContent = person.name;
    const meta = document.createElement('small');
    const voiceCount = voices.filter(voice => voice.personId === person.id).length;
    const avatarCount = avatars.filter(avatar => avatar.personId === person.id).length;
    meta.textContent = `${voiceCount} 个声音 · ${avatarCount} 个形象`;
    const actions = document.createElement('div');
    actions.className = 'voice-card-actions';
    const deleteButton = document.createElement('button');
    deleteButton.type = 'button';
    deleteButton.className = 'voice-text-button is-danger';
    deleteButton.textContent = '删除';
    deleteButton.addEventListener('click', () => removePerson(person));
    actions.append(deleteButton);
    item.append(name, meta, actions);
    ui.personList.appendChild(item);
  });
}

async function addPerson() {
  const name = ui.personNameInput.value.trim();
  if (!name) {
    showToast('请输入人物名称。');
    ui.personNameInput.focus();
    return;
  }
  ui.addPersonBtn.disabled = true;
  try {
    const result = await api('/api/person/save', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
    persons = Array.isArray(result.persons) ? result.persons : [];
    ui.personNameInput.value = '';
    afterPersonsChanged();
    showToast('人物已添加。');
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.addPersonBtn.disabled = false;
    ui.personNameInput.focus();
  }
}

async function removePerson(person) {
  if (!window.confirm(`确定删除人物“${person.name}”吗？\n其下的声音、形象和素材会移入未分组。`)) return;
  try {
    const result = await api('/api/person/delete', {
      method: 'POST',
      body: JSON.stringify({ id: person.id }),
    });
    persons = Array.isArray(result.persons) ? result.persons : [];
    afterPersonsChanged();
    showToast('人物已删除，其素材已移入未分组。');
  } catch (error) {
    showToast(error.message);
  }
}

function openAvatarPreview(avatar) {
  ui.avatarModalTitle.textContent = avatar.name;
  ui.avatarPreviewVideo.src = avatar.videoUrl;
  ui.avatarModal.classList.remove('is-hidden');
  ui.avatarPreviewVideo.play().catch(() => {});
}
function closeAvatarPreview() {
  ui.avatarPreviewVideo.pause();
  ui.avatarPreviewVideo.removeAttribute('src');
  ui.avatarPreviewVideo.load();
  ui.avatarModal.classList.add('is-hidden');
}

async function startPreview() {
  let data;
  try {
    data = validateStep(2);
  } catch (error) {
    showToast(error.message);
    return;
  }
  ui.previewButton.disabled = true;
  ui.previewButton.textContent = '正在生成试听';
  ui.audioPreview.classList.add('is-hidden');
  try {
    await api('/api/preview', { method: 'POST', body: JSON.stringify(data) });
    clearTimeout(previewPollTimer);
    pollPreview();
  } catch (error) {
    ui.previewButton.disabled = false;
    ui.previewButton.textContent = '试听声音';
    showToast(error.message);
  }
}

async function pollPreview() {
  try {
    const job = await api('/api/job?kind=preview');
    if (job.status === 'running') {
      ui.previewButton.textContent = job.stage || '正在生成试听';
      previewPollTimer = setTimeout(pollPreview, 1400);
      return;
    }
    ui.previewButton.disabled = false;
    ui.previewButton.textContent = '重新试听';
    if (job.status === 'done' && job.audio) {
      ui.audioPreview.src = `/api/media?path=${encodeURIComponent(job.audio)}&t=${Date.now()}`;
      ui.audioPreview.classList.remove('is-hidden');
      ui.audioPreview.play().catch(() => {});
    } else if (job.status === 'error') {
      showToast(job.error || '试听生成失败。');
    }
  } catch (error) {
    ui.previewButton.disabled = false;
    ui.previewButton.textContent = '试听声音';
    showToast(error.message);
  }
}

function resetTaskDisplay() {
  ui.taskArea.classList.remove('is-hidden');
  ui.errorBox.classList.add('is-hidden');
  ui.errorBox.textContent = '';
  ui.resultArea.classList.add('is-hidden');
  ui.resultVideo.removeAttribute('src');
  ui.openResult.classList.add('is-hidden');
  ui.queueList.classList.add('is-hidden');
  ui.queueList.replaceChildren();
  ui.progressFill.style.width = '0%';
  ui.progressValue.textContent = '0%';
  ui.progressStage.textContent = '正在准备';
}

async function startGenerate() {
  let data;
  try {
    data = validateStep(3);
  } catch (error) {
    showToast(error.message);
    return;
  }
  if (componentStatus && !coreComponentsReady()) {
    showToast('口型模型运行环境还没装好，请先完成安装。');
    openSetupModal();
    return;
  }
  ui.startButton.disabled = true;
  ui.startButton.textContent = '正在加入';
  try {
    activeRunMode = 'queue';
    const result = await api('/api/queue/add', { method: 'POST', body: JSON.stringify(data) });
    renderQueue(result.queue);
    clearTaskEditorAfterQueue();
    showToast('任务已加入并自动启动，无需再点开始。');
    startQueuePolling();
  } catch (error) {
    showToast(error.message);
  } finally {
    ui.startButton.disabled = false;
    ui.startButton.textContent = '添加并自动开始';
  }
}

function queuePhaseName(stage) {
  const value = String(stage || '');
  if (/声音|语音|音频|拆分|分段|voice/i.test(value)) return '声音合成';
  if (/素材|B-roll|匹配/.test(value)) return '素材匹配';
  if (/嘴型|数字人|人脸/.test(value)) return '嘴型合成';
  if (/导出|保存|字幕|标题|配乐|画面/.test(value)) return '视频导出';
  if (/加载.*模型|显存|GPU/i.test(value)) return '加载模型';
  return '准备任务';
}

function formatQueueElapsed(seconds) {
  const total = Math.max(0, Math.round(Number(seconds) || 0));
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  const secs = total % 60;
  if (hours > 0) return `${hours}小时${minutes}分`;
  if (minutes > 0) return `${minutes}分${secs}秒`;
  return `${secs}秒`;
}

function queueItemTiming(item) {
  if (!item.createdAt) return '';
  if (item.status === 'done' || item.status === 'error' || item.status === 'cancelled') {
    if (!item.finishedAt) return '';
    // 耗时不含排队等待：从开始生成算到结束；从未启动就结束的按提交时间兜底
    const start = item.startedAt || item.createdAt;
    return `耗时 ${formatQueueElapsed(item.finishedAt - start)}`;
  }
  const start = item.startedAt || item.createdAt;
  const elapsed = Date.now() / 1000 - start;
  return item.status === 'running'
    ? `已进行 ${formatQueueElapsed(elapsed)}`
    : `已等待 ${formatQueueElapsed(Date.now() / 1000 - item.createdAt)}`;
}

function queueStatusLabel(item, queue, pendingRank = -1, hasRunning = false) {
  if (item.status === 'running') {
    return `正在运行 · ${queuePhaseName(item.stage)} ${Math.round(Number(item.progress) || 0)}%`;
  }
  if (item.status === 'paused') return '已暂停';
  if (item.status === 'done') return '已完成';
  if (item.status === 'error') return '失败';
  if (item.status === 'cancelled') return '已取消';
  if (queue.paused) return '等待继续';
  if (pendingRank === 0 && !hasRunning) return '正在启动';
  return `排队第 ${pendingRank + 1} 位`;
}

function showQueueResult(path) {
  if (!path) return;
  ui.resultVideo.src = `/api/media?path=${encodeURIComponent(path)}&t=${Date.now()}`;
  ui.resultArea.classList.remove('is-hidden');
  ui.resultVideo.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function queueActionButton(label, action, item, extraClass = '') {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = `queue-action ${extraClass}`.trim();
  button.textContent = label;
  button.setAttribute('aria-label', `${label}任务：${item.title || `文案 ${item.position}`}`);
  button.addEventListener('click', async () => {
    if (action === 'delete' && !window.confirm(
      `确定从任务队列删除“${item.title || `文案 ${item.position}`}”吗？\n只删除队列记录，不会删除已经输出的视频文件。`,
    )) return;
    if (action === 'cancel' && !window.confirm(
      `确定停止“${item.title || `文案 ${item.position}`}”吗？\n正在运行的任务会立即终止并释放显存和 CPU；已合成的语音进度会保留，重新生成会断点续跑。`,
    )) return;
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = ({
      start_item: '正在启动', pause_item: '正在暂停', delete: '正在删除', cancel: '正在停止',
    })[action] || '处理中';
    const succeeded = await runQueueAction(action, item.id);
    if (!succeeded && button.isConnected) {
      button.disabled = false;
      button.textContent = originalText;
    }
  });
  return button;
}

async function runQueueAction(action, id = '') {
  try {
    const queue = await api('/api/queue/action', {
      method: 'POST',
      body: JSON.stringify({ action, id }),
    });
    renderQueue(queue);
    startQueuePolling();
    const message = ({
      start_item: '任务已启动，正在等待模型响应。',
      pause_item: '这条任务已暂停。',
      delete: '任务已从队列删除，已输出的视频不会被删除。',
      cancel: '正在停止当前任务，模型进程会终止并释放显存。',
      pause: '后续任务已暂停，当前正在生成的任务会继续完成。',
      resume: '队列已继续，等待任务会自动生成。',
    })[action];
    if (message) showToast(message);
    return true;
  } catch (error) {
    showToast(error.message);
    return false;
  }
}

function renderQueue(queue) {
  queuePaused = Boolean(queue.paused);
  ui.queueList.replaceChildren();
  ui.queueList.classList.toggle('is-hidden', !queue.items?.length);
  if (ui.queueEmpty) ui.queueEmpty.classList.toggle('is-hidden', Boolean(queue.items?.length));
  if (ui.queueCountBadge) ui.queueCountBadge.textContent = String(queue.total || 0);
  if (ui.pauseQueue) {
    ui.pauseQueue.textContent = queue.paused ? '继续全部任务' : '暂停后续任务';
    ui.pauseQueue.classList.toggle('is-paused', queue.paused);
  }
  if (ui.queueSummary) {
    if (!queue.total) ui.queueSummary.textContent = '还没有任务，添加后会自动开始。';
    else if (queue.paused) ui.queueSummary.textContent = `后续生成已暂停 · 点击“继续全部任务”即可恢复 · ${queue.pending || 0} 条等待`;
    else if ((queue.items || []).some(item => item.status === 'running')) ui.queueSummary.textContent = `正在生成 1 条 · 后面 ${queue.pending || 0} 条自动排队 · ${queue.completed || 0} 条完成`;
    else ui.queueSummary.textContent = `${queue.pending || 0} 条即将自动开始 · ${queue.pausedItems || 0} 条单独暂停 · ${queue.completed || 0} 条完成${queue.failed ? ` · ${queue.failed} 条失败` : ''}`;
  }

  const overall = Math.max(0, Math.min(100, Math.round(Number(queue.overallProgress) || 0)));
  const active = (queue.items || []).find(item => item.status === 'running');
  const pendingItems = (queue.items || []).filter(item => item.status === 'pending');
  ui.taskArea.classList.toggle('is-hidden', !queue.items?.length);
  ui.progressFill.style.width = `${overall}%`;
  ui.progressValue.textContent = `${overall}%`;
  ui.progressStage.textContent = active
    ? `${active.title || '当前任务'} · ${active.stage || '正在处理'}`
    : queue.paused
      ? '整个队列已暂停'
      : queue.pausedItems && !queue.pending
        ? `${queue.pausedItems} 条任务已单独暂停`
        : queue.total ? '等待下一项任务' : '等待任务';

  (queue.items || []).forEach((item, index) => {
    const row = document.createElement('div');
    row.className = `queue-item is-${item.status}`;
    if (item.status === 'running') {
      row.setAttribute('aria-current', 'step');
      row.setAttribute('aria-label', `正在运行：${item.title || `文案 ${item.position}`}`);
    }

    const number = document.createElement('span');
    number.className = 'queue-number';
    number.textContent = String(index + 1).padStart(2, '0');

    const avatar = document.createElement('span');
    avatar.className = 'queue-avatar';
    const avatarImage = document.createElement('img');
    avatarImage.src = item.avatarPosterUrl || '/assets/app-icon.png';
    avatarImage.alt = item.avatarName || '数字人形象';
    avatarImage.loading = 'lazy';
    avatarImage.addEventListener('error', () => {
      avatarImage.src = '/assets/app-icon.png';
    }, { once: true });
    avatar.appendChild(avatarImage);

    const content = document.createElement('span');
    content.className = 'queue-content';
    const title = document.createElement('strong');
    title.className = 'queue-title';
    title.textContent = item.title || `文案 ${item.position}`;
    title.title = item.title || `文案 ${item.position}`;
    const titleLine = document.createElement('span');
    titleLine.className = 'queue-title-line';
    if (item.status === 'running') {
      const liveMarker = document.createElement('span');
      liveMarker.className = 'queue-live-marker';
      const liveDot = document.createElement('i');
      liveDot.setAttribute('aria-hidden', 'true');
      liveMarker.append(liveDot, document.createTextNode('正在输出'));
      titleLine.appendChild(liveMarker);
    }
    titleLine.appendChild(title);
    const stageLine = document.createElement('span');
    stageLine.className = 'queue-stage-line';
    const pendingRank = pendingItems.findIndex(entry => entry.id === item.id);
    if (item.status === 'running') {
      stageLine.textContent = item.stage || '正在准备生成';
    } else if (item.status === 'pending' && queue.paused) {
      stageLine.textContent = '整个队列已暂停，点击上方“继续全部任务”';
    } else if (item.status === 'pending' && pendingRank === 0 && !active) {
      stageLine.textContent = '正在启动模型，请稍候';
    } else if (item.status === 'pending') {
      const ahead = pendingRank + (active ? 1 : 0);
      stageLine.textContent = ahead > 0 ? `自动排队中，前面还有 ${ahead} 条任务` : '即将自动开始';
    } else if (item.status === 'paused') {
      stageLine.textContent = '这条任务已单独暂停，点击“继续”恢复';
    } else if (item.status === 'done') {
      stageLine.textContent = '视频已生成完成';
    } else {
      stageLine.textContent = item.error || item.stage || '任务未完成';
    }
    const detail = document.createElement('small');
    detail.className = 'queue-meta-line';
    const settings = [
      item.avatarName,
      item.voiceName,
      item.voiceAccountName ? `API：${item.voiceAccountName}` : '',
      item.elevenGenerationModeName || '',
      item.quality === 'v2' ? 'V2' : 'V1',
      String(item.resolution || '').toUpperCase(),
      item.brollEnabled ? 'B-roll 开' : 'B-roll 关',
    ].filter(Boolean).join(' · ');
    detail.textContent = `${item.characters || 0} 字${settings ? ` · ${settings}` : ''}${queueItemTiming(item) ? ` · ${queueItemTiming(item)}` : ''}`;
    content.append(titleLine, stageLine, detail);

    const miniProgress = document.createElement('div');
    miniProgress.className = 'queue-mini-progress';
    const track = document.createElement('span');
    const fill = document.createElement('i');
    fill.style.width = `${Math.max(0, Math.min(100, Number(item.progress) || 0))}%`;
    track.appendChild(fill);
    const percent = document.createElement('b');
    percent.textContent = `${Math.round(Number(item.progress) || 0)}%`;
    miniProgress.append(track, percent);

    const status = document.createElement('span');
    status.className = `queue-status is-${item.status}`;
    status.textContent = queueStatusLabel(item, queue, pendingRank, Boolean(active));

    const actions = document.createElement('div');
    actions.className = 'queue-actions';
    if (item.status === 'pending') {
      actions.append(
        ...(queue.paused ? [queueActionButton('立即继续', 'start_item', item, 'is-primary')] : []),
        queueActionButton('暂停', 'pause_item', item),
        queueActionButton('上移', 'move_up', item),
        queueActionButton('下移', 'move_down', item),
        queueActionButton('删除', 'delete', item, 'is-danger'),
      );
    } else if (item.status === 'paused') {
      actions.append(
        queueActionButton('继续', 'start_item', item, 'is-primary'),
        queueActionButton('复制', 'duplicate', item),
        queueActionButton('删除', 'delete', item, 'is-danger'),
      );
    } else if (item.status === 'done') {
      if (item.result) {
        const view = document.createElement('button');
        view.type = 'button';
        view.className = 'queue-action';
        view.textContent = '查看';
        view.addEventListener('click', () => showQueueResult(item.result));
        actions.appendChild(view);
      }
      actions.append(
        queueActionButton('重新生成', 'start_item', item, 'is-primary'),
        queueActionButton('复制', 'duplicate', item),
        queueActionButton('删除', 'delete', item, 'is-danger'),
      );
    } else if (item.status === 'error' || item.status === 'cancelled') {
      actions.append(
        queueActionButton('重新生成', 'start_item', item, 'is-primary'),
        queueActionButton('复制', 'duplicate', item),
        queueActionButton('删除', 'delete', item, 'is-danger'),
      );
    } else if (item.status === 'running') {
      const runningBadge = document.createElement('span');
      runningBadge.className = 'queue-running-badge';
      runningBadge.textContent = '正在运行';
      actions.append(
        runningBadge,
        queueActionButton('停止', 'cancel', item, 'is-danger'),
      );
    }
    row.append(number, avatar, content, miniProgress, status, actions);
    ui.queueList.appendChild(row);
  });
}

async function pollQueue() {
  try {
    const queue = await api('/api/queue');
    renderQueue(queue);
    const completed = (queue.items || []).filter(item => item.status === 'done');
    const failed = (queue.items || []).filter(item => item.status === 'error');
    if (completed.length) ui.openResult.classList.remove('is-hidden');
    if (failed.length) {
      ui.errorBox.textContent = `${failed.length} 条任务失败，其余任务已继续生成。`;
      ui.errorBox.classList.remove('is-hidden');
    } else {
      ui.errorBox.classList.add('is-hidden');
    }
  } catch (error) {
    showToast(error.message);
  } finally {
    if (queuePollActive) mainPollTimer = setTimeout(pollQueue, 1600);
  }
}

function startQueuePolling() {
  if (queuePollActive) return;
  queuePollActive = true;
  clearTimeout(mainPollTimer);
  pollQueue();
}

function setTaskError(message) {
  ui.startButton.disabled = false;
  ui.startButton.textContent = '重新生成';
  ui.backButton.disabled = false;
  ui.errorBox.textContent = message || '生成失败。';
  ui.errorBox.classList.remove('is-hidden');
}

async function pollMain() {
  try {
    const job = await api('/api/job?kind=main');
    const progress = Math.max(0, Math.min(100, Math.round(Number(job.progress) || 0)));
    ui.taskArea.classList.remove('is-hidden');
    ui.progressFill.style.width = `${progress}%`;
    ui.progressValue.textContent = `${progress}%`;
    ui.progressStage.textContent = job.stage || '正在处理';
    if (job.status === 'running') {
      mainPollTimer = setTimeout(pollMain, 1500);
      return;
    }
    ui.startButton.disabled = false;
    ui.backButton.disabled = false;
    ui.startButton.textContent = '重新生成';
    if (job.status === 'done' && job.result) {
      ui.resultVideo.src = `/api/media?path=${encodeURIComponent(job.result)}&t=${Date.now()}`;
      ui.resultArea.classList.remove('is-hidden');
      ui.openResult.classList.remove('is-hidden');
    } else if (job.status === 'error') {
      setTaskError(job.error || '生成失败。');
    }
  } catch (error) {
    setTaskError(error.message);
  }
}

// ---------------------------------------------------------------------------
// 组件与下载（首启安装向导）
// ---------------------------------------------------------------------------
let setupStepsCache = [];

function applyComponentAvailability() {
  const c = componentStatus;
  if (!c) return;
  const v1Button = document.querySelector('[data-quality="v1"]');
  if (v1Button) {
    v1Button.classList.toggle('is-hidden', !c.humanModule);
    if (!c.humanModule && quality === 'v1') setQuality('v2');
  }
  if (ui.addLocalVoice) {
    ui.addLocalVoice.classList.toggle('is-hidden', !c.voiceV2Module && !c.voxcpm);
  }
}

function coreComponentsReady() {
  return Boolean(
    componentStatus
    && componentStatus.hdModule
    && componentStatus.hdModuleVenv
    && componentStatus.ffmpeg
  );
}

function updateSetupButtons(running) {
  ui.startSetupInstall.disabled = running;
  ui.cancelSetupInstall.classList.toggle('is-hidden', !running);
}

function stopSetupPolling() {
  if (setupPollTimer) {
    clearInterval(setupPollTimer);
    setupPollTimer = null;
  }
}

function startSetupPolling() {
  stopSetupPolling();
  updateSetupButtons(true);
  const tick = async () => {
    let job;
    try {
      job = await api('/api/job?kind=setup');
    } catch (error) {
      return;
    }
    ui.setupProgress.classList.remove('is-hidden');
    ui.setupStage.textContent = job.stage || '安装中';
    const progress = Math.max(0, Math.min(100, Math.round(job.progress || 0)));
    ui.setupValue.textContent = `${progress}%`;
    ui.setupFill.style.width = `${progress}%`;
    ui.setupLog.textContent = (job.log || []).slice(-8).join('\n');
    if (['done', 'error', 'cancelled'].includes(job.status)) {
      stopSetupPolling();
      updateSetupButtons(false);
      if (job.status === 'done') showToast('组件安装完成。');
      else if (job.status === 'error') showToast(job.error || '安装失败，请查看日志。');
      refreshSetupSteps().catch(() => {});
      loadStatus().catch(() => {});
    }
  };
  tick();
  setupPollTimer = setInterval(tick, 1500);
}

async function refreshSetupSteps() {
  const data = await api('/api/setup/steps');
  componentStatus = data.components || componentStatus;
  applyComponentAvailability();
  setupStepsCache = data.steps || [];
  const bundle = data.bundle || {};
  const bundleItems = bundle.items || {};
  if (bundle.available) {
    const found = Object.values(bundleItems).filter(Boolean).length;
    ui.setupBundleText.textContent = `离线组件包已识别（${found} 项内容）：${bundle.path}`;
  } else if (bundle.path) {
    ui.setupBundleText.textContent = `离线组件包路径无效或未识别到内容：${bundle.path}`;
  } else {
    ui.setupBundleText.textContent = '未指定离线组件包（也可以直接联网下载，源均为国内站点）';
  }
  // 各步骤离线就绪判定：pythonEnv 需 4 个安装文件齐全，其余看对应模型目录
  const offlineReady = {
    pythonEnv: Boolean(bundleItems.pythonInstaller && bundleItems.torch
      && bundleItems.torchvisionAudio && bundleItems.insightface),
    whisperModel: Boolean(bundleItems.whisper),
    brollModels: Boolean(bundleItems.bge && bundleItems.clip),
  };
  const gpu = data.gpu || {};
  ui.setupGpuText.textContent = gpu.available
    ? `显卡：${gpu.name}（显存 ${(gpu.totalMb / 1024).toFixed(0)}GB，当前空闲 ${(gpu.freeMb / 1024).toFixed(1)}GB）`
    : (gpu.label || '未检测到 NVIDIA 显卡，口型模型将无法运行');
  const showTweak = Boolean(
    gpu.available && gpu.totalMb > 0 && gpu.totalMb <= 9216
    && (componentStatus?.gpuMinFreeMB || 6500) > 5800
  );
  ui.setupGpuTweak.classList.toggle('is-hidden', !showTweak);
  ui.setupStepList.innerHTML = '';
  setupStepsCache.forEach(step => {
    const row = document.createElement('label');
    row.className = `setup-step-row${step.installed ? ' is-installed' : ''}`;
    const badge = step.installed
      ? '<span class="setup-step-badge is-ok">已安装</span>'
      : (step.required
        ? '<span class="setup-step-badge">必装</span>'
        : '<span class="setup-step-badge is-optional">可选</span>');
    row.innerHTML = `<input type="checkbox" data-setup-step="${step.id}"${step.required || step.installed ? ' checked' : ''}${step.required || step.installed ? ' disabled' : ''}>
      <span class="setup-step-main"><strong></strong><small></small></span>
      <span class="setup-step-side">${badge}<small></small></span>`;
    row.querySelector('.setup-step-main strong').textContent = step.name;
    row.querySelector('.setup-step-main small').textContent = step.description;
    row.querySelector('.setup-step-side small').textContent =
      step.sizeHint + (offlineReady[step.id] ? ' · 可离线安装' : '');
    ui.setupStepList.appendChild(row);
  });
  if (data.running) startSetupPolling();
}

async function startSetupInstallFlow() {
  const installed = new Set(setupStepsCache.filter(step => step.installed).map(step => step.id));
  const ids = [...ui.setupStepList.querySelectorAll('input[data-setup-step]:checked')]
    .map(input => input.dataset.setupStep)
    .filter(id => !installed.has(id));
  if (!ids.length) {
    showToast('选中的组件都已经装好了。');
    return;
  }
  await api('/api/setup/install', { method: 'POST', body: JSON.stringify({ steps: ids }) });
  ui.setupProgress.classList.remove('is-hidden');
  startSetupPolling();
}

function openSetupModal() {
  ui.setupModal.classList.remove('is-hidden');
  refreshSetupSteps().catch(error => showToast(error.message));
}

function closeSetupModal() {
  ui.setupModal.classList.add('is-hidden');
}

async function loadStatus() {
  try {
    const status = await api('/api/status');
    defaultOutputPath = status.defaultOutput || '';
    ui.outputDir.value = defaultOutputPath;
    componentStatus = status.components || null;
    applyComponentAvailability();
    const coreReady = !componentStatus || coreComponentsReady();
    if (status.gpu?.available && coreReady) {
      ui.deviceStatus.className = 'device-status is-ready';
      ui.deviceStatus.innerHTML = '<span class="status-dot"></span><span></span>';
      ui.deviceStatus.lastElementChild.textContent = status.gpu.label;
    } else if (status.gpu?.available && !coreReady) {
      ui.deviceStatus.className = 'device-status is-error';
      ui.deviceStatus.innerHTML = '<span class="status-dot"></span><span>待安装组件</span>';
    } else {
      ui.deviceStatus.className = 'device-status is-error';
      ui.deviceStatus.innerHTML = '<span class="status-dot"></span><span>模型环境异常</span>';
    }
    const queue = await api('/api/queue');
    renderQueue(queue);
    startQueuePolling();
    const running = await api('/api/job?kind=main');
    if (running.status === 'running' && !queue.items?.length) pollMain();
  } catch (error) {
    ui.deviceStatus.className = 'device-status is-error';
    ui.deviceStatus.innerHTML = '<span class="status-dot"></span><span>本地服务未连接</span>';
    showToast(error.message);
  }
}

ui.steps.forEach(button => button.addEventListener('click', () => {
  resetLibrarySelectionContext();
  showStep(button.dataset.step);
}));

document.querySelectorAll('[data-next]').forEach(button => {
  button.addEventListener('click', () => {
    const target = Number(button.dataset.next);
    if (target > currentStep) {
      try {
        validateStep(currentStep);
      } catch (error) {
        showToast(error.message);
        return;
      }
    }
    showStep(target);
  });
});

document.querySelectorAll('[data-pick]').forEach(button => {
  button.addEventListener('click', () => pick(button.dataset.pick, button.dataset.target));
});

document.querySelectorAll('[data-voice]').forEach(button => {
  button.addEventListener('click', () => setVoiceMode(button.dataset.voice));
});

document.querySelectorAll('[data-script-mode]').forEach(button => {
  button.addEventListener('click', () => setScriptMode(button.dataset.scriptMode));
});

document.querySelectorAll('[data-quality]').forEach(button => {
  button.addEventListener('click', () => setQuality(button.dataset.quality));
});

document.querySelectorAll('[data-resolution]').forEach(button => {
  button.addEventListener('click', () => setResolution(button.dataset.resolution));
});

ui.script.addEventListener('input', () => {
  ui.charCount.textContent = `${ui.script.value.length} 字`;
  scheduleDraftSave();
});
ui.singleTitle.addEventListener('input', scheduleDraftSave);

ui.batchScripts.forEach(input => {
  input.addEventListener('input', () => {
    input.closest('.batch-script-card').querySelector('small').textContent = `${input.value.length} 字`;
  });
});

ui.singleMusicSearch.addEventListener('input', () => {
  fillMusicSelect(ui.singleMusicSelect, ui.singleMusicSearch.value);
});
ui.singleMusicSelect.addEventListener('change', scheduleDraftSave);
ui.batchMusicSearches.forEach((input, index) => {
  input.addEventListener('input', () => {
    fillMusicSelect(ui.batchMusicSelects[index], input.value);
    ui.batchMusicPreviewButtons[index].disabled = !ui.batchMusicSelects[index].value;
  });
});
ui.batchMusicSelects.forEach((select, index) => {
  select.addEventListener('change', () => {
    ui.batchMusicPreviewButtons[index].disabled = !select.value;
  });
});
ui.batchMusicPreviewButtons.forEach((button, index) => {
  button.disabled = true;
  button.addEventListener('click', () => previewBatchMusic(index));
});
ui.batchAvatarPickers.forEach((button, index) => {
  button.addEventListener('click', () => openBatchAvatarPicker(index));
});

ui.musicVolume.addEventListener('input', () => {
  ui.musicVolumeValue.textContent = `${Number(ui.musicVolume.value)}%`;
  scheduleDraftSave();
});

ui.speed.addEventListener('input', () => {
  ui.speedValue.textContent = `${Number(ui.speed.value).toFixed(2)}×`;
  saveVoiceParams();
  scheduleDraftSave();
});

ui.emotionWeight.addEventListener('input', () => {
  ui.emotionWeightValue.textContent = Number(ui.emotionWeight.value).toFixed(2);
  saveVoiceParams();
  scheduleDraftSave();
});

ui.cfgValue.addEventListener('input', () => {
  ui.cfgValueValue.textContent = Number(ui.cfgValue.value).toFixed(1);
  saveVoiceParams();
  scheduleDraftSave();
});

ui.inferenceTimesteps.addEventListener('input', () => {
  ui.inferenceTimestepsValue.textContent = String(Number(ui.inferenceTimesteps.value));
  saveVoiceParams();
  scheduleDraftSave();
});

ui.emotionText.addEventListener('input', () => {
  saveVoiceParams();
  scheduleDraftSave();
});

[
  [ui.elevenStability, ui.elevenStabilityValue],
  [ui.elevenSimilarity, ui.elevenSimilarityValue],
  [ui.elevenStyle, ui.elevenStyleValue],
].forEach(([input, output]) => {
  input.addEventListener('input', () => {
    output.textContent = `${input.value}%`;
    scheduleElevenSettingsSave();
    scheduleDraftSave();
  });
});

ui.elevenSpeakerBoost.addEventListener('change', () => {
  scheduleElevenSettingsSave();
  scheduleDraftSave();
});

[ui.brollEnabled, ui.subtitleEnabled, ui.nameplateEnabled].forEach(input => {
  input.addEventListener('change', scheduleDraftSave);
});
[ui.textFont, ui.textShadow, ui.titleColorTop, ui.titleColorBottom, ui.speakerName, ui.speakerDetails].forEach(input => {
  input.addEventListener('input', scheduleDraftSave);
  input.addEventListener('change', scheduleDraftSave);
});

document.querySelector('#importText').addEventListener('click', importText);
ui.textUpload.addEventListener('change', handleTextUpload);
ui.addMusic.addEventListener('click', openMusicUpload);
ui.musicUpload.addEventListener('change', handleMusicUpload);
ui.previewMusic.addEventListener('click', previewSelectedMusic);
ui.previewButton.addEventListener('click', startPreview);
ui.addBroll.addEventListener('click', openBrollUpload);
ui.brollUpload.addEventListener('change', handleBrollUpload);
ui.brollSearch.addEventListener('input', renderBrollLibrary);
ui.brollCategory.addEventListener('change', renderBrollLibrary);
ui.brollPersonFilter.addEventListener('change', renderBrollLibrary);
ui.brollStatus.addEventListener('change', renderBrollLibrary);
ui.backFromBrollLibrary.addEventListener('click', () => showStep(1));
ui.closeBrollPreview.addEventListener('click', closeBrollPreview);
ui.brollPreviewModal.addEventListener('click', event => {
  if (event.target === ui.brollPreviewModal) closeBrollPreview();
});
ui.closeBrollEditModal.addEventListener('click', closeBrollEditor);
ui.cancelBrollEditModal.addEventListener('click', closeBrollEditor);
ui.saveBrollEdit.addEventListener('click', saveBrollEditor);
ui.brollEditName.addEventListener('keydown', event => {
  if (event.key === 'Enter') saveBrollEditor();
});
ui.brollEditModal.addEventListener('click', event => {
  if (event.target === ui.brollEditModal) closeBrollEditor();
});
ui.startButton.addEventListener('click', startGenerate);
ui.pauseQueue.addEventListener('click', () => runQueueAction(queuePaused ? 'resume' : 'pause'));
ui.clearFinished.addEventListener('click', () => runQueueAction('clear_finished'));
ui.themeToggle.addEventListener('click', toggleTheme);
ui.changeAvatar.addEventListener('click', () => showStep(3));
ui.selectedAvatarCard.addEventListener('click', () => showStep(3));
ui.changeVoice.addEventListener('click', () => showStep(2));
ui.voicePersonSelect.addEventListener('change', () => {
  if (ui.voicePersonSelect.value === '__upload__') {
    setUploadVoiceMode();
    return;
  }
  renderWorkbenchVoiceOptions(ui.voicePersonSelect.value);
  const firstUsable = [...ui.workbenchVoiceSelect.options].find(option => !option.disabled && option.value);
  if (firstUsable && firstUsable.value !== selectedVoiceId) setVoice(firstUsable.value);
});
ui.workbenchVoiceSelect.addEventListener('change', () => {
  if (ui.workbenchVoiceSelect.value === '__upload__') {
    setUploadVoiceMode();
    return;
  }
  if (ui.workbenchVoiceSelect.value) setVoice(ui.workbenchVoiceSelect.value);
});
ui.uploadCustomAudio.addEventListener('click', () => ui.customAudioFile.click());
ui.customAudioFile.addEventListener('change', async () => {
  const file = ui.customAudioFile.files?.[0];
  if (!file) return;
  ui.uploadCustomAudio.disabled = true;
  ui.customAudioName.textContent = '正在上传录音…';
  try {
    const result = await uploadApi('/api/audio/upload', file);
    customAudioPath = String(result.path || '');
    customAudioName = String(result.name || file.name);
    const seconds = Math.round(Number(result.duration) || 0);
    ui.customAudioName.textContent = `${customAudioName}${seconds ? ` · ${formatQueueElapsed(seconds)}` : ''}`;
    ui.customAudioPreview.src = `/api/media?path=${encodeURIComponent(customAudioPath)}&t=${Date.now()}`;
    ui.customAudioPreview.classList.remove('is-hidden');
    // 上传录音即视为要用自己的声音：自动切到"自己录音"模式
    if (voiceMode !== 'upload') {
      ui.voicePersonSelect.value = '__upload__';
      setUploadVoiceMode();
    }
    if (ui.currentVoiceMeta) ui.currentVoiceMeta.textContent = `自己录音 · ${customAudioName}`;
    renderWorkbenchVoiceOptions('__upload__');
    showToast('录音已上传，这条任务将直接用你的声音。');
  } catch (error) {
    ui.customAudioName.textContent = '上传失败，请重试';
    showToast(error.message);
  } finally {
    ui.uploadCustomAudio.disabled = false;
    ui.customAudioFile.value = '';
    updateSummary();
    if (appReady) scheduleDraftSave();
  }
});
ui.avatarPersonSelect.addEventListener('change', () => {
  renderWorkbenchAvatarOptions(ui.avatarPersonSelect.value);
  if (ui.workbenchAvatarSelect.value && ui.workbenchAvatarSelect.value !== selectedAvatarId) {
    setAvatar(ui.workbenchAvatarSelect.value);
  }
});
ui.workbenchAvatarSelect.addEventListener('change', () => {
  if (ui.workbenchAvatarSelect.value) setAvatar(ui.workbenchAvatarSelect.value);
});
ui.managePersonsBtn1.addEventListener('click', openPersonModal);
ui.managePersonsBtn2.addEventListener('click', openPersonModal);
ui.closePersonModal.addEventListener('click', closePersonModal);
ui.cancelPersonModal.addEventListener('click', closePersonModal);
ui.addPersonBtn.addEventListener('click', addPerson);
ui.personNameInput.addEventListener('keydown', event => {
  if (event.key === 'Enter') addPerson();
});
ui.personModal.addEventListener('click', event => {
  if (event.target === ui.personModal) closePersonModal();
});
ui.workbenchElevenMode.addEventListener('change', () => {
  setElevenGenerationMode(ui.workbenchElevenMode.value);
  showToast(`本条任务将使用“${elevenGenerationMode().name}”。`);
});
ui.workbenchElevenAccount.addEventListener('change', () => {
  setWorkbenchElevenAccount(ui.workbenchElevenAccount.value);
  const account = elevenAccountById(selectedElevenAccountId);
  showToast(account ? `本条任务已切换到“${account.name}”。` : '本条任务将自动选择兼容账号。');
});
ui.backFromAvatarLibrary.addEventListener('click', leaveLibrarySelection);
ui.backFromVoiceLibrary.addEventListener('click', leaveLibrarySelection);
ui.closeOutputPathModal.addEventListener('click', closeOutputPathModal);
ui.cancelOutputPathModal.addEventListener('click', closeOutputPathModal);
ui.browseOutputPath.addEventListener('click', browseOutputFolder);
ui.useDefaultOutputPath.addEventListener('click', () => {
  ui.outputPathInput.value = defaultOutputPath;
  ui.outputPathInput.focus();
});
ui.saveOutputPath.addEventListener('click', saveOutputFolder);
ui.outputPathInput.addEventListener('keydown', event => {
  if (event.key === 'Enter') saveOutputFolder();
});
ui.outputPathModal.addEventListener('click', event => {
  if (event.target === ui.outputPathModal) closeOutputPathModal();
});
ui.openResult.addEventListener('click', () => {
  api('/api/open-result', { method: 'POST', body: '{}' }).catch(error => showToast(error.message));
});

ui.addAvatar.addEventListener('click', importAvatar);
ui.avatarUpload.addEventListener('change', handleAvatarUpload);
ui.addLocalVoice.addEventListener('click', openLocalVoiceModal);
ui.pickLocalVoiceSample.addEventListener('click', pickLocalVoiceSample);
ui.localVoicePath.addEventListener('click', pickLocalVoiceSample);
ui.localVoiceUpload.addEventListener('change', handleLocalVoiceUpload);
ui.saveLocalVoice.addEventListener('click', saveLocalVoice);
ui.localVoiceEngine.addEventListener('change', updateLocalVoiceModeFields);
document.querySelectorAll('input[name="localVoiceMode"]').forEach(radio => {
  radio.addEventListener('change', updateLocalVoiceModeFields);
});
ui.transcribeLocalVoice.addEventListener('click', transcribeLocalSample);
ui.transcribeRenamedVoice.addEventListener('click', transcribeRenamedVoiceSample);
ui.closeLocalVoiceModal.addEventListener('click', closeLocalVoiceModal);
ui.cancelLocalVoiceModal.addEventListener('click', closeLocalVoiceModal);
ui.localVoiceModal.addEventListener('click', event => {
  if (event.target === ui.localVoiceModal) closeLocalVoiceModal();
});
ui.addElevenLabsVoice.addEventListener('click', () => openVoiceModal());
ui.editSelectedCloudVoice.addEventListener('click', () => {
  const voice = selectedVoice();
  if (voice?.provider === 'elevenlabs') openVoiceModal(voice);
});
ui.manageElevenAccounts.addEventListener('click', () => openElevenAccountModal());
ui.quickAddElevenAccount.addEventListener('click', () => openElevenAccountModal());
ui.closeElevenAccountModal.addEventListener('click', closeElevenAccountModal);
ui.cancelElevenAccountModal.addEventListener('click', closeElevenAccountModal);
ui.newElevenAccount.addEventListener('click', resetElevenAccountEditor);
ui.saveElevenAccount.addEventListener('click', saveElevenAccount);
ui.elevenAccountModal.addEventListener('click', event => {
  if (event.target === ui.elevenAccountModal) closeElevenAccountModal();
});
ui.cloudVoiceAccount.addEventListener('change', () => fillRemoteVoiceOptions(ui.cloudVoiceId.value));
ui.cloudVoiceRemote.addEventListener('change', () => {
  if (!ui.cloudVoiceRemote.value) return;
  ui.cloudVoiceId.value = ui.cloudVoiceRemote.value;
  const voice = elevenAccountById(ui.cloudVoiceAccount.value)?.voices
    ?.find(item => item.voiceId === ui.cloudVoiceRemote.value);
  if (voice && !ui.cloudVoiceName.value.trim()) ui.cloudVoiceName.value = voice.name;
});
ui.cloudVoiceModel.addEventListener('change', () => {
  updateCloudParameterOutputs();
  updateCloudVoiceNote();
});
[ui.cloudStability, ui.cloudSimilarity, ui.cloudStyle].forEach(input => {
  input.addEventListener('input', updateCloudParameterOutputs);
});
ui.closeVoiceModal.addEventListener('click', closeVoiceModal);
ui.cancelVoiceModal.addEventListener('click', closeVoiceModal);
ui.saveElevenLabsVoice.addEventListener('click', saveCloudVoice);
ui.voiceModal.addEventListener('click', event => {
  if (event.target === ui.voiceModal) closeVoiceModal();
});
ui.closeRenameModal.addEventListener('click', closeRenameModal);
ui.cancelRenameModal.addEventListener('click', closeRenameModal);
ui.saveRename.addEventListener('click', saveRenamedItem);
ui.renameName.addEventListener('keydown', event => {
  if (event.key === 'Enter') saveRenamedItem();
});
ui.renameModal.addEventListener('click', event => {
  if (event.target === ui.renameModal) closeRenameModal();
});
ui.closeAvatarModal.addEventListener('click', closeAvatarPreview);
ui.avatarModal.addEventListener('click', event => {
  if (event.target === ui.avatarModal) closeAvatarPreview();
});
ui.closeBatchAvatarModal.addEventListener('click', closeBatchAvatarPicker);
ui.batchAvatarModal.addEventListener('click', event => {
  if (event.target === ui.batchAvatarModal) closeBatchAvatarPicker();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !ui.avatarModal.classList.contains('is-hidden')) closeAvatarPreview();
  if (event.key === 'Escape' && !ui.voiceModal.classList.contains('is-hidden')) closeVoiceModal();
  if (event.key === 'Escape' && !ui.elevenAccountModal.classList.contains('is-hidden')) closeElevenAccountModal();
  if (event.key === 'Escape' && !ui.localVoiceModal.classList.contains('is-hidden')) closeLocalVoiceModal();
  if (event.key === 'Escape' && !ui.renameModal.classList.contains('is-hidden')) closeRenameModal();
  if (event.key === 'Escape' && !ui.personModal.classList.contains('is-hidden')) closePersonModal();
  if (event.key === 'Escape' && !ui.batchAvatarModal.classList.contains('is-hidden')) closeBatchAvatarPicker();
  if (event.key === 'Escape' && !ui.brollPreviewModal.classList.contains('is-hidden')) closeBrollPreview();
  if (event.key === 'Escape' && !ui.brollEditModal.classList.contains('is-hidden')) closeBrollEditor();
  if (event.key === 'Escape' && !ui.outputPathModal.classList.contains('is-hidden')) closeOutputPathModal();
  if (event.key === 'Escape' && !ui.setupModal.classList.contains('is-hidden')) closeSetupModal();
});

ui.openSetup.addEventListener('click', openSetupModal);
ui.closeSetupModal.addEventListener('click', closeSetupModal);
ui.closeSetupModalBottom.addEventListener('click', closeSetupModal);
ui.startSetupInstall.addEventListener('click', () => {
  startSetupInstallFlow().catch(error => showToast(error.message));
});
ui.cancelSetupInstall.addEventListener('click', () => {
  api('/api/setup/cancel', { method: 'POST', body: '{}' })
    .then(() => showToast('正在取消安装…'))
    .catch(error => showToast(error.message));
});
ui.setupGpuTweak.addEventListener('click', () => {
  api('/api/setup/config', { method: 'POST', body: JSON.stringify({ gpuMinFreeMB: 5800 }) })
    .then(() => {
      showToast('已按 8GB 显卡放宽显存门槛，立即生效。');
      refreshSetupSteps().catch(() => {});
    })
    .catch(error => showToast(error.message));
});
ui.setupBundlePick.addEventListener('click', () => {
  api('/api/pick', { method: 'POST', body: JSON.stringify({ kind: 'folder' }) })
    .then(result => {
      if (result.cancelled || !result.path) return null;
      return api('/api/setup/config', {
        method: 'POST',
        body: JSON.stringify({ setupBundleDir: result.path }),
      }).then(() => {
        showToast('已设置离线组件包目录。');
        refreshSetupSteps().catch(() => {});
      });
    })
    .catch(error => showToast(error.message));
});

async function initializeWorkbench() {
  // 2026-08-14 起默认深色主题（配合光束背景）；老用户已存的浅色偏好一次性迁移到深色，
  // 之后仍可用右上角开关自由切换，切换结果照常记忆。
  if (localStorage.getItem('localDhThemeV2') !== '1') {
    localStorage.setItem('localDhThemeV2', '1');
    applyTheme('dark');
  } else {
    applyTheme(localStorage.getItem('localDhTheme') || 'dark');
  }
  setScriptMode('single');
  setQuality('v2');
  setResolution('4k');
  const results = await Promise.allSettled([
    loadStatus(),
    loadAvatars(),
    loadElevenConfig(),
    loadVoices(),
    loadPersons(),
    loadMusicLibrary(),
    loadBrollLibrary(),
  ]);
  results.filter(result => result.status === 'rejected').forEach(result => showToast(result.reason?.message || '部分数据加载失败。'));
  restoreDraft();
  appReady = true;
  saveDraft();
  showStep(1);
  startQueuePolling();
  // 首次使用（口型运行环境未装）自动弹出安装向导，每台设备只主动弹一次
  if (componentStatus && !coreComponentsReady() && !setupAutoOpened) {
    setupAutoOpened = true;
    openSetupModal();
  }
}

initializeWorkbench().catch(error => showToast(error.message));
