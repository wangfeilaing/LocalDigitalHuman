// 本文件由 showcase/build/build_showcase.py 自动生成，请勿手改。
// 数据来源：真实后端接口抓包 -> 脱敏（密钥尾号/真人姓名/云端 Voice ID 全部替换）-> 裁剪。
// 生成时间：2026-10-10 15:49:17
window.__DEMO_DATA__ = {
 "status": {
  "ok": true,
  "gpu": {
   "available": true,
   "name": "NVIDIA GeForce RTX 3080",
   "totalMb": 10240,
   "freeMb": 9118,
   "label": "NVIDIA GeForce RTX 3080 · 就绪"
  },
  "modules": {
   "voiceV2Module": true,
   "humanModule": false,
   "hdModule": true
  },
  "modulesRoot": "D:\\LocalDigitalHuman\\modules",
  "defaultOutput": "D:\\数字人视频输出",
  "components": {
   "ffmpeg": true,
   "hdModule": true,
   "hdModuleVenv": true,
   "humanModule": false,
   "voiceV2Module": true,
   "voxcpm": true,
   "whisperModel": true,
   "whisperPython": true,
   "brollMatcherModel": true,
   "brollClassifierModel": true,
   "gpuMinFreeMB": 6500
  }
 },
 "setup-steps": {
  "ok": true,
  "steps": [
   {
    "name": "口型模型运行环境",
    "description": "Python 3.10 + PyTorch（CUDA 版）+ 口型模型依赖。没有它无法生成数字人画面，必装。",
    "sizeHint": "下载约 3.5GB",
    "required": true,
    "id": "pythonEnv",
    "installed": true
   },
   {
    "name": "字幕逐字对齐模型",
    "description": "faster-whisper large-v3-turbo。不装也能出片，但字幕与 B-roll 的时间轴会明显不准，推荐安装。",
    "sizeHint": "下载约 1.7GB",
    "required": false,
    "id": "whisperModel",
    "installed": true
   },
   {
    "name": "B-roll 智能匹配模型",
    "description": "文案理解 + 画面分类模型。只在使用 B-roll 智能插入画面时需要，不用可以不装。",
    "sizeHint": "下载约 0.7GB",
    "required": false,
    "id": "brollModels",
    "installed": true
   }
  ],
  "running": false,
  "gpu": {
   "available": true,
   "name": "NVIDIA GeForce RTX 3080",
   "totalMb": 10240,
   "freeMb": 9118,
   "label": "NVIDIA GeForce RTX 3080 · 就绪"
  },
  "components": {
   "ffmpeg": true,
   "hdModule": true,
   "hdModuleVenv": true,
   "humanModule": false,
   "voiceV2Module": true,
   "voxcpm": true,
   "whisperModel": true,
   "whisperPython": true,
   "brollMatcherModel": true,
   "brollClassifierModel": true,
   "gpuMinFreeMB": 6500
  },
  "bundle": {
   "path": "",
   "available": false,
   "items": {
    "pythonInstaller": false,
    "torch": false,
    "torchvisionAudio": false,
    "insightface": false,
    "whisper": false,
    "bge": false,
    "clip": false
   }
  }
 },
 "persons": {
  "ok": true,
  "persons": [
   {
    "id": "讲师A",
    "name": "讲师A",
    "createdAt": "2026-08-13 20:18:54"
   },
   {
    "id": "讲师B",
    "name": "讲师B",
    "createdAt": "2026-08-13 20:18:54"
   },
   {
    "id": "讲师C",
    "name": "讲师C",
    "createdAt": "2026-08-13 20:18:54"
   },
   {
    "id": "讲师D",
    "name": "讲师D",
    "createdAt": "2026-08-13 20:18:54"
   }
  ]
 },
 "voices": {
  "ok": true,
  "voices": [
   {
    "id": "07b87ebf318c485481dd73d60c91822d",
    "name": "沉稳男声 · 讲师A",
    "provider": "local",
    "personId": "讲师A",
    "createdAt": "2026-08-11 13:11:22",
    "sampleUrl": "media/voice-01.mp3",
    "previewUrl": "media/voice-01.mp3",
    "promptText": "",
    "status": "ready",
    "clonedAt": "2026-08-11 13:11:31",
    "cloneError": "",
    "engine": "v2",
    "engineName": "IndexTTS-2 · 本地免费"
   },
   {
    "id": "1df8d19d76a4480cab980358050b40a5",
    "name": "亲切女声 · 讲师B",
    "provider": "local",
    "personId": "讲师B",
    "createdAt": "2026-08-11 13:11:22",
    "sampleUrl": "media/voice-02.mp3",
    "previewUrl": "media/voice-02.mp3",
    "promptText": "",
    "status": "ready",
    "clonedAt": "2026-08-11 13:11:31",
    "cloneError": "",
    "engine": "voxcpm",
    "engineName": "VoxCPM2 · 本地免费"
   },
   {
    "id": "3bf0090343e84a48830653a0399d20bc",
    "name": "磁性男声 · 讲师C",
    "provider": "local",
    "personId": "讲师C",
    "createdAt": "2026-08-11 13:11:22",
    "sampleUrl": "media/voice-03.mp3",
    "previewUrl": "media/voice-03.mp3",
    "promptText": "",
    "status": "ready",
    "clonedAt": "2026-08-11 13:11:31",
    "cloneError": "",
    "engine": "v2",
    "engineName": "IndexTTS-2 · 本地免费"
   },
   {
    "id": "demo-eleven-voice-0001",
    "name": "云端克隆 · 讲师D",
    "provider": "elevenlabs",
    "personId": "讲师D",
    "createdAt": "2026-08-12 23:14:32",
    "voiceId": "DEMO_VOICE_ID_NOT_REAL",
    "accountId": "demo-eleven-account",
    "accountName": "ElevenLabs 演示账号",
    "accountStatus": "ready",
    "status": "ready",
    "category": "professional",
    "engine": "elevenlabs",
    "engineName": "ElevenLabs 云端",
    "sampleUrl": "media/voice-01.mp3",
    "previewUrl": "media/voice-01.mp3",
    "promptText": "",
    "cloneError": ""
   }
  ]
 },
 "avatars": {
  "ok": true,
  "avatars": [
   {
    "id": "fa346f6b6c5946dc9338b254e51172d9",
    "name": "数字人顾问 01",
    "posterUrl": "media/avatar-01.jpg",
    "videoUrl": "media/avatar-01.mp4",
    "personId": "讲师A",
    "createdAt": "2026-08-11 17:05:33",
    "duration": 237.4,
    "usageCount": 4,
    "lastStartOffset": 80.0
   },
   {
    "id": "841ae75f4f8f4b86bbdb18e88750adbe",
    "name": "数字人顾问 02",
    "posterUrl": "media/avatar-02.jpg",
    "videoUrl": "media/avatar-01.mp4",
    "personId": "讲师B",
    "createdAt": "2026-08-11 18:05:33",
    "duration": 274.8,
    "usageCount": 5,
    "lastStartOffset": 100.0
   },
   {
    "id": "bb6bd72de2b247fab91aa21c52278d31",
    "name": "数字人顾问 03",
    "posterUrl": "media/avatar-03.jpg",
    "videoUrl": "media/avatar-02.mp4",
    "personId": "讲师C",
    "createdAt": "2026-08-11 16:05:33",
    "duration": 312.2,
    "usageCount": 6,
    "lastStartOffset": 120.0
   },
   {
    "id": "6f7d0090279b4d1d8cef4984e0938d2d",
    "name": "数字人顾问 04",
    "posterUrl": "media/avatar-03.jpg",
    "videoUrl": "media/avatar-02.mp4",
    "personId": "讲师D",
    "createdAt": "2026-08-11 17:05:33",
    "duration": 349.6,
    "usageCount": 7,
    "lastStartOffset": 140.0
   },
   {
    "id": "fa35d2eb6ade42ba8e4ef58172471296",
    "name": "数字人顾问 05",
    "posterUrl": "media/avatar-03.jpg",
    "videoUrl": "media/avatar-03.mp4",
    "personId": "讲师A",
    "createdAt": "2026-08-11 18:05:33",
    "duration": 387.0,
    "usageCount": 8,
    "lastStartOffset": 160.0
   },
   {
    "id": "e5d10c4c68ef4fd8b1d850564549ea27",
    "name": "数字人顾问 06",
    "posterUrl": "media/avatar-03.jpg",
    "videoUrl": "media/avatar-03.mp4",
    "personId": "讲师B",
    "createdAt": "2026-08-11 16:05:33",
    "duration": 424.4,
    "usageCount": 9,
    "lastStartOffset": 180.0
   }
  ]
 },
 "broll": {
  "ok": true,
  "assets": [
   {
    "id": "B001",
    "name": "暴雨积水的院落中有人躺在水里戏水.mp4",
    "summary": "暴雨积水的院落中有人躺在水里戏水",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "暴雨",
     "积水",
     "院落",
     "户外",
     "释放",
     "乐观",
     "荒诞",
     "人物"
    ],
    "duration": 7.033,
    "width": 576,
    "height": 1024,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-01.jpg",
    "videoUrl": "media/broll-clip-02.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B002",
    "name": "雨夜城市街道与撑伞行人.mp4",
    "summary": "雨夜城市街道与撑伞行人",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "城市",
     "雨夜",
     "街道",
     "孤独",
     "惆怅",
     "行人",
     "行走",
     "撑伞"
    ],
    "duration": 7.777,
    "width": 576,
    "height": 768,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-02.jpg",
    "videoUrl": "media/broll-clip-01.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B003",
    "name": "夜晚车窗外手持红色发光爱心.mp4",
    "summary": "夜晚车窗外手持红色发光爱心",
    "category": "亲密关系",
    "sourceGroup": "演示素材库",
    "tags": [
     "夜晚",
     "车内",
     "霓虹",
     "浪漫",
     "思念",
     "手部",
     "爱心",
     "手持"
    ],
    "duration": 9.611,
    "width": 720,
    "height": 1280,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-03.jpg",
    "videoUrl": "media/broll-clip-02.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B004",
    "name": "乌云下巨浪拍打海岸堤坝.mp4",
    "summary": "乌云下巨浪拍打海岸堤坝",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "海洋",
     "风暴",
     "乌云",
     "压迫",
     "震撼",
     "海浪",
     "翻涌",
     "困境"
    ],
    "duration": 10.667,
    "width": 720,
    "height": 1280,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-04.jpg",
    "videoUrl": "media/broll-clip-01.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B005",
    "name": "镜面海面上的小船与巨大云墙.mp4",
    "summary": "镜面海面上的小船与巨大云墙",
    "category": "个人成长",
    "sourceGroup": "演示素材库",
    "tags": [
     "天空",
     "海面",
     "梦境",
     "梦幻",
     "希望",
     "辽阔",
     "小船",
     "人物"
    ],
    "duration": 10.474,
    "width": 720,
    "height": 1280,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-05.jpg",
    "videoUrl": "media/broll-clip-02.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B006",
    "name": "燃烧的植物化为发光碎片.mp4",
    "summary": "燃烧的植物化为发光碎片",
    "category": "个人成长",
    "sourceGroup": "演示素材库",
    "tags": [
     "暗场",
     "火焰",
     "抽象",
     "强烈",
     "释放",
     "植物",
     "燃烧",
     "消散"
    ],
    "duration": 17.901,
    "width": 1440,
    "height": 2560,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-06.jpg",
    "videoUrl": "media/broll-clip-01.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B007",
    "name": "夜晚餐馆外独自打电话的女子.mp4",
    "summary": "夜晚餐馆外独自打电话的女子",
    "category": "亲密关系",
    "sourceGroup": "演示素材库",
    "tags": [
     "城市",
     "夜晚",
     "餐馆",
     "孤独",
     "等待",
     "焦虑",
     "女性",
     "手机"
    ],
    "duration": 11.0,
    "width": 720,
    "height": 1280,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-07.jpg",
    "videoUrl": "media/broll-clip-02.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B008",
    "name": "暴雨城市、田野背影与雨夜长椅组成的伤感合集.mp4",
    "summary": "暴雨城市、田野背影与雨夜长椅组成的伤感合集",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "暴雨",
     "城市",
     "田野",
     "夜晚",
     "孤独",
     "压抑",
     "悲伤",
     "人物"
    ],
    "duration": 19.644,
    "width": 1080,
    "height": 1920,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-08.jpg",
    "videoUrl": "media/broll-clip-01.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B009",
    "name": "昏暗房间里透过百叶窗看到城市夜景.mp4",
    "summary": "昏暗房间里透过百叶窗看到城市夜景",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "室内",
     "窗边",
     "夜晚",
     "安静",
     "孤独",
     "压抑",
     "窗户",
     "静止"
    ],
    "duration": 10.008,
    "width": 540,
    "height": 960,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-09.jpg",
    "videoUrl": "media/broll-clip-02.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   },
   {
    "id": "B010",
    "name": "暴雨城市、田野背影与雨夜长椅组成的伤感合集.mp4",
    "summary": "暴雨城市、田野背影与雨夜长椅组成的伤感合集",
    "category": "情绪氛围",
    "sourceGroup": "演示素材库",
    "tags": [
     "暴雨",
     "城市",
     "田野",
     "夜晚",
     "孤独",
     "压抑",
     "悲伤",
     "人物"
    ],
    "duration": 19.644,
    "width": 576,
    "height": 1024,
    "useMode": "ready",
    "usable": true,
    "uploaded": false,
    "posterUrl": "media/broll-10.jpg",
    "videoUrl": "media/broll-clip-01.mp4",
    "personId": "",
    "createdAt": "2026-08-11"
   }
  ]
 },
 "music": {
  "ok": true,
  "music": [
   {
    "id": "f7325372ad1144d68fbd8e9f183c6201",
    "name": "氛围垫乐 01",
    "duration": 117.6,
    "audioUrl": "media/music-01.mp3",
    "createdAt": "2026-08-11 18:10:18"
   },
   {
    "id": "3603f208ac0d4703a360d809b90ea8dd",
    "name": "氛围垫乐 02",
    "duration": 112.9,
    "audioUrl": "media/music-02.mp3",
    "createdAt": "2026-08-11 18:10:18"
   },
   {
    "id": "dd2e661b9e5144598e704927f1fb1c24",
    "name": "氛围垫乐 03",
    "duration": 63.8,
    "audioUrl": "media/music-03.mp3",
    "createdAt": "2026-08-11 18:10:18"
   },
   {
    "id": "2ab8fcfebea2446d956bd1c57caf317a",
    "name": "氛围垫乐 04",
    "duration": 96.4,
    "audioUrl": "media/music-04.mp3",
    "createdAt": "2026-08-11 18:10:18"
   }
  ]
 },
 "elevenlabs-config": {
  "ok": true,
  "accounts": [
   {
    "id": "demo-eleven-account-1",
    "name": "ElevenLabs 演示账号 1",
    "hasKey": true,
    "keyPreview": "demo",
    "enabled": true,
    "priority": 10,
    "status": "ready",
    "error": "",
    "subscription": {
     "tier": "creator",
     "status": "active",
     "characterCount": 46000,
     "characterLimit": 200000,
     "nextReset": 1789454177,
     "allowedToExtend": false,
     "usagePercent": 23.0
    },
    "models": [
     {
      "modelId": "eleven_v3",
      "name": "Eleven v3",
      "description": "The most expressive model. Supports 70+ languages. Requires more prompt engineering than our previous models.",
      "maxCharacters": 5000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_multilingual_v2",
      "name": "Eleven Multilingual v2",
      "description": "Our most life-like, emotionally rich mode in 29 languages. Best for voice overs, audiobooks, post-production, or any other content creation needs.",
      "maxCharacters": 10000,
      "recommended": true,
      "supportsStyle": true,
      "supportsSpeakerBoost": true
     },
     {
      "modelId": "eleven_flash_v2_5",
      "name": "Eleven Flash v2.5",
      "description": "Our ultra low latency model in 32 languages. Ideal for conversational use cases.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2_5",
      "name": "Eleven Turbo v2.5",
      "description": "Our high quality, low latency model in 32 languages. Best for developer use cases where speed matters and you need non-English languages.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2",
      "name": "Eleven Turbo v2",
      "description": "Our English-only, low latency model. Best for developer use cases where speed matters and you only need English. Performance is on par with Turbo v2.5.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_flash_v2",
      "name": "Eleven Flash v2",
      "description": "Our ultra low latency model in english. Ideal for conversational use cases.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     }
    ],
    "voices": [
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Adam - Dominant, Firm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Alice - Clear, Engaging Educator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bella - Professional, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bill - Wise, Mature, Balanced",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Brian - Deep, Resonant and Comforting",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Callum - Husky Trickster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Charlie - Deep, Confident, Energetic",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Chris - Charming, Down-to-Earth",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Dan - Captivating, Engaging and Inviting",
      "category": "professional"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Daniel - Steady Broadcaster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Eric - Smooth, Trustworthy",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "George - Warm, Captivating Storyteller",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Harry - Fierce Warrior",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Jessica - Playful, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Laura - Enthusiast, Quirky Attitude",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Liam - Energetic, Social Media Creator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Lily - Velvety Actress",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Matilda - Knowledgable, Professional",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "River - Relaxed, Neutral, Informative",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Roger - Laid-Back, Casual, Resonant",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Sarah - Mature, Reassuring, Confident",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Will - Relaxed Optimist",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "讲师A voice",
      "category": "professional"
     }
    ],
    "createdAt": "2026-08-12 22:21:58",
    "updatedAt": "2026-08-18 19:34:15",
    "lastCheckedAt": "2026-08-18 19:34:15"
   },
   {
    "id": "demo-eleven-account-2",
    "name": "ElevenLabs 演示账号 2",
    "hasKey": true,
    "keyPreview": "demo",
    "enabled": true,
    "priority": 20,
    "status": "error",
    "error": "无法连接 ElevenLabs，请检查网络或代理设置：[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
    "subscription": {
     "tier": "creator",
     "status": "active",
     "characterCount": 81000,
     "characterLimit": 100000,
     "nextReset": 1789119902,
     "allowedToExtend": false,
     "usagePercent": 81.0
    },
    "models": [
     {
      "modelId": "eleven_v3",
      "name": "Eleven v3",
      "description": "The most expressive model. Supports 70+ languages. Requires more prompt engineering than our previous models.",
      "maxCharacters": 5000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_multilingual_v2",
      "name": "Eleven Multilingual v2",
      "description": "Our most life-like, emotionally rich mode in 29 languages. Best for voice overs, audiobooks, post-production, or any other content creation needs.",
      "maxCharacters": 10000,
      "recommended": true,
      "supportsStyle": true,
      "supportsSpeakerBoost": true
     },
     {
      "modelId": "eleven_flash_v2_5",
      "name": "Eleven Flash v2.5",
      "description": "Our ultra low latency model in 32 languages. Ideal for conversational use cases.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2_5",
      "name": "Eleven Turbo v2.5",
      "description": "Our high quality, low latency model in 32 languages. Best for developer use cases where speed matters and you need non-English languages.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2",
      "name": "Eleven Turbo v2",
      "description": "Our English-only, low latency model. Best for developer use cases where speed matters and you only need English. Performance is on par with Turbo v2.5.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_flash_v2",
      "name": "Eleven Flash v2",
      "description": "Our ultra low latency model in english. Ideal for conversational use cases.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     }
    ],
    "voices": [
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Adam - Dominant, Firm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Alice - Clear, Engaging Educator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bella - Professional, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bill - Wise, Mature, Balanced",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Brian - Deep, Resonant and Comforting",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Callum - Husky Trickster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Charlie - Deep, Confident, Energetic",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Chris - Charming, Down-to-Earth",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Daniel - Steady Broadcaster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Eric - Smooth, Trustworthy",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "George - Warm, Captivating Storyteller",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Harry - Fierce Warrior",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Jessica - Playful, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Laura - Enthusiast, Quirky Attitude",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Liam - Energetic, Social Media Creator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Lily - Velvety Actress",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Matilda - Knowledgable, Professional",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "River - Relaxed, Neutral, Informative",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Roger - Laid-Back, Casual, Resonant",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Sarah - Mature, Reassuring, Confident",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Will - Relaxed Optimist",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "讲师B",
      "category": "professional"
     }
    ],
    "createdAt": "2026-08-12 23:45:23",
    "updatedAt": "2026-08-16 12:48:49",
    "lastCheckedAt": "2026-08-16 12:48:49"
   },
   {
    "id": "demo-eleven-account-3",
    "name": "ElevenLabs 演示账号 3",
    "hasKey": true,
    "keyPreview": "demo",
    "enabled": true,
    "priority": 30,
    "status": "ready",
    "error": "",
    "subscription": {
     "tier": "creator",
     "status": "active",
     "characterCount": 71500,
     "characterLimit": 200000,
     "nextReset": 1789274347,
     "allowedToExtend": false,
     "usagePercent": 35.8
    },
    "models": [
     {
      "modelId": "eleven_v3",
      "name": "Eleven v3",
      "description": "The most expressive model. Supports 70+ languages. Requires more prompt engineering than our previous models.",
      "maxCharacters": 5000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_multilingual_v2",
      "name": "Eleven Multilingual v2",
      "description": "Our most life-like, emotionally rich mode in 29 languages. Best for voice overs, audiobooks, post-production, or any other content creation needs.",
      "maxCharacters": 10000,
      "recommended": true,
      "supportsStyle": true,
      "supportsSpeakerBoost": true
     },
     {
      "modelId": "eleven_flash_v2_5",
      "name": "Eleven Flash v2.5",
      "description": "Our ultra low latency model in 32 languages. Ideal for conversational use cases.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2_5",
      "name": "Eleven Turbo v2.5",
      "description": "Our high quality, low latency model in 32 languages. Best for developer use cases where speed matters and you need non-English languages.",
      "maxCharacters": 40000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_turbo_v2",
      "name": "Eleven Turbo v2",
      "description": "Our English-only, low latency model. Best for developer use cases where speed matters and you only need English. Performance is on par with Turbo v2.5.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     },
     {
      "modelId": "eleven_flash_v2",
      "name": "Eleven Flash v2",
      "description": "Our ultra low latency model in english. Ideal for conversational use cases.",
      "maxCharacters": 30000,
      "recommended": false,
      "supportsStyle": false,
      "supportsSpeakerBoost": false
     }
    ],
    "voices": [
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Adam - Dominant, Firm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Alice - Clear, Engaging Educator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bella - Professional, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Bill - Wise, Mature, Balanced",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Brian - Deep, Resonant and Comforting",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Callum - Husky Trickster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Charlie - Deep, Confident, Energetic",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Chris - Charming, Down-to-Earth",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Daniel - Steady Broadcaster",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Eric - Smooth, Trustworthy",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "George - Warm, Captivating Storyteller",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Harry - Fierce Warrior",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Jessica - Playful, Bright, Warm",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Laura - Enthusiast, Quirky Attitude",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Liam - Energetic, Social Media Creator",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Lily - Velvety Actress",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Matilda - Knowledgable, Professional",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "River - Relaxed, Neutral, Informative",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Roger - Laid-Back, Casual, Resonant",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Sarah - Mature, Reassuring, Confident",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "Will - Relaxed Optimist",
      "category": "premade"
     },
     {
      "voiceId": "DEMO_VOICE_ID_NOT_REAL",
      "name": "讲师D",
      "category": "professional"
     }
    ],
    "createdAt": "2026-08-14 22:40:42",
    "updatedAt": "2026-08-18 19:34:19",
    "lastCheckedAt": "2026-08-18 19:34:19"
   }
  ],
  "models": [
   {
    "modelId": "eleven_multilingual_v2",
    "name": "Eleven Multilingual v2",
    "description": "Our most life-like, emotionally rich mode in 29 languages. Best for voice overs, audiobooks, post-production, or any other content creation needs.",
    "maxCharacters": 10000,
    "recommended": true,
    "supportsStyle": true,
    "supportsSpeakerBoost": true
   },
   {
    "modelId": "eleven_v3",
    "name": "Eleven v3",
    "description": "The most expressive model. Supports 70+ languages. Requires more prompt engineering than our previous models.",
    "maxCharacters": 5000,
    "recommended": false,
    "supportsStyle": false,
    "supportsSpeakerBoost": false
   },
   {
    "modelId": "eleven_turbo_v2",
    "name": "Eleven Turbo v2",
    "description": "Our English-only, low latency model. Best for developer use cases where speed matters and you only need English. Performance is on par with Turbo v2.5.",
    "maxCharacters": 30000,
    "recommended": false,
    "supportsStyle": false,
    "supportsSpeakerBoost": false
   },
   {
    "modelId": "eleven_flash_v2_5",
    "name": "Eleven Flash v2.5",
    "description": "Our ultra low latency model in 32 languages. Ideal for conversational use cases.",
    "maxCharacters": 40000,
    "recommended": false,
    "supportsStyle": false,
    "supportsSpeakerBoost": false
   },
   {
    "modelId": "eleven_turbo_v2_5",
    "name": "Eleven Turbo v2.5",
    "description": "Our high quality, low latency model in 32 languages. Best for developer use cases where speed matters and you need non-English languages.",
    "maxCharacters": 40000,
    "recommended": false,
    "supportsStyle": false,
    "supportsSpeakerBoost": false
   },
   {
    "modelId": "eleven_flash_v2",
    "name": "Eleven Flash v2",
    "description": "Our ultra low latency model in english. Ideal for conversational use cases.",
    "maxCharacters": 30000,
    "recommended": false,
    "supportsStyle": false,
    "supportsSpeakerBoost": false
   }
  ],
  "generationModes": [
   {
    "id": "multilingual_v2",
    "name": "Multilingual v2 · 音色稳定",
    "description": "中文长文稳定，优先保持本人音色。",
    "modelId": "eleven_multilingual_v2",
    "doublePass": false
   },
   {
    "id": "v3",
    "name": "V3 · 情感优先",
    "description": "情绪和语气更丰富，音色可能比本人略有变化。",
    "modelId": "eleven_v3",
    "doublePass": false
   },
   {
    "id": "turbo_v2",
    "name": "Eleven Turbo v2 · 快速输出",
    "description": "生成速度快；这个版本偏英文，中文优先使用 Multilingual v2 或结合版。",
    "modelId": "eleven_turbo_v2",
    "doublePass": false
   },
   {
    "id": "v3_voice_match",
    "name": "V3情感＋本人音色",
    "description": "先用V3生成情感，再转换回目标音色；效果优先，会调用两次云端处理。",
    "modelId": "eleven_v3",
    "doublePass": true
   }
  ],
  "outputFormats": [
   {
    "id": "mp3_44100_128",
    "name": "MP3 44.1kHz · 标准"
   },
   {
    "id": "mp3_44100_192",
    "name": "MP3 44.1kHz · 高码率"
   }
  ],
  "readyAccounts": 2
 },
 "queue": {
  "ok": true,
  "status": "done",
  "paused": false,
  "total": 4,
  "pending": 0,
  "pausedItems": 0,
  "completed": 2,
  "failed": 1,
  "activePosition": 0,
  "overallProgress": 65.0,
  "items": [
   {
    "id": "demo-q1",
    "position": 1,
    "title": "众生皆苦 苦在把一场体验当成了占有",
    "characters": 412,
    "avatarId": "fa346f6b6c5946dc9338b254e51172d9",
    "avatarName": "数字人顾问 01",
    "voiceName": "沉稳男声 · 讲师A",
    "voiceAccountName": "",
    "elevenGenerationMode": "",
    "elevenGenerationModeName": "",
    "avatarPosterUrl": "media/avatar-01.jpg",
    "status": "done",
    "progress": 100,
    "stage": "已完成",
    "result": "media/result.mp4",
    "cover": "media/result-cover.jpg",
    "error": null,
    "createdAt": 1791609557,
    "startedAt": 1791609857,
    "finishedAt": 1791610457,
    "quality": "v2",
    "resolution": "4k",
    "brollEnabled": true,
    "musicId": "f7325372ad1144d68fbd8e9f183c6201"
   },
   {
    "id": "demo-q2",
    "position": 2,
    "title": "不再渴望被爱 才真正拥有了爱",
    "characters": 368,
    "avatarId": "841ae75f4f8f4b86bbdb18e88750adbe",
    "avatarName": "数字人顾问 02",
    "voiceName": "亲切女声 · 讲师B",
    "voiceAccountName": "",
    "elevenGenerationMode": "",
    "elevenGenerationModeName": "",
    "avatarPosterUrl": "media/avatar-02.jpg",
    "status": "done",
    "progress": 100,
    "stage": "已完成",
    "result": "media/result.mp4",
    "cover": "media/result-cover.jpg",
    "error": null,
    "createdAt": 1791610757,
    "startedAt": 1791610957,
    "finishedAt": 1791611557,
    "quality": "v2",
    "resolution": "2k",
    "brollEnabled": true,
    "musicId": "3603f208ac0d4703a360d809b90ea8dd"
   },
   {
    "id": "demo-q3",
    "position": 3,
    "title": "身体比脑子更清楚 谁在消耗你",
    "characters": 296,
    "avatarId": "bb6bd72de2b247fab91aa21c52278d31",
    "avatarName": "数字人顾问 03",
    "voiceName": "磁性男声 · 讲师C",
    "voiceAccountName": "",
    "elevenGenerationMode": "",
    "elevenGenerationModeName": "",
    "avatarPosterUrl": "media/avatar-03.jpg",
    "status": "error",
    "progress": 42,
    "stage": "口型同步",
    "result": null,
    "cover": null,
    "error": "显存不足：需要 6500MB 可用，当前 5120MB（演示数据）",
    "createdAt": 1791614957,
    "startedAt": 1791615157,
    "finishedAt": 1791615557,
    "quality": "v2",
    "resolution": "4k",
    "brollEnabled": false,
    "musicId": ""
   },
   {
    "id": "demo-q4",
    "position": 4,
    "title": "越是顺 越要管住自己的嘴",
    "characters": 240,
    "avatarId": "fa346f6b6c5946dc9338b254e51172d9",
    "avatarName": "数字人顾问 01",
    "voiceName": "沉稳男声 · 讲师A",
    "voiceAccountName": "",
    "elevenGenerationMode": "",
    "elevenGenerationModeName": "",
    "avatarPosterUrl": "media/avatar-01.jpg",
    "status": "cancelled",
    "progress": 18,
    "stage": "分段合成语音",
    "result": null,
    "cover": null,
    "error": null,
    "createdAt": 1791617357,
    "startedAt": 1791617457,
    "finishedAt": 1791617657,
    "quality": "v2",
    "resolution": "2k",
    "brollEnabled": true,
    "musicId": "dd2e661b9e5144598e704927f1fb1c24"
   }
  ]
 },
 "job-main": {
  "kind": "main",
  "id": null,
  "status": "idle",
  "progress": 0,
  "stage": "",
  "message": "",
  "error": null,
  "result": null,
  "cover": null,
  "audio": null,
  "outputDir": null,
  "segmentsTotal": 0,
  "segmentsDone": 0,
  "startedAt": null,
  "elapsedSeconds": 0,
  "estimatedSeconds": null,
  "log": []
 },
 "job-preview": {
  "kind": "preview",
  "status": "idle",
  "progress": 0,
  "audio": null,
  "error": null
 },
 "job-clone": {
  "kind": "clone",
  "status": "idle",
  "progress": 0,
  "error": null
 },
 "job-setup": {
  "kind": "setup",
  "status": "idle",
  "progress": 0,
  "stage": "",
  "log": []
 },
 "ping": {
  "ok": true,
  "app": "LocalDigitalHuman · 在线演示"
 }
};
