const state = {
  showAll: false,
  query: '',
  manifest: null,
  lang: 'en',
  tagType: 'series',
  tagValue: '',
  modelValue: '',
};

// Per-model expand state for artifact lists (keyed by group_path).
const expandedModels = new Set();

const cardsEl = document.getElementById('cards');
const metaEl = document.getElementById('meta');
const searchEl = document.getElementById('search');
const latestBtn = document.getElementById('latestBtn');
const allBtn = document.getElementById('allBtn');
const zhBtn = document.getElementById('zhBtn');
const enBtn = document.getElementById('enBtn');
const tagIndexLabelEl = document.getElementById('tagIndexLabel');
const tagSelectLabelEl = document.getElementById('tagSelectLabel');
const tagSelectEl = document.getElementById('tagSelect');
const tagTabs = Array.from(document.querySelectorAll('[data-tag-type]'));
const modelSelectLabelEl = document.getElementById('modelSelectLabel');
const modelSelectEl = document.getElementById('modelSelect');
const eyebrowEl = document.getElementById('eyebrow');
const heroTitleEl = document.getElementById('heroTitle');
const subheadEl = document.getElementById('subhead');
const searchLabelEl = document.getElementById('searchLabel');
const footerTextEl = document.getElementById('footerText');
const repoLinkTextEl = document.getElementById('repoLinkText');

const i18n = {
  en: {
    eyebrow: 'Loongson Community firmware',
    heroTitle: 'Downloads Hub',
    subhead: 'Latest BIOS and firmware artifacts, grouped by device model. Use search or switch to full history when needed.',
    repoLink: 'GitHub Repo',
    searchLabel: 'Search',
    searchPlaceholder: 'Model, series, or path',
    latest: 'Latest',
    all: 'All',
    language: 'Language',
    indexBy: 'Index by',
    indexAll: 'All',
    indexCollection: 'Collection',
    indexSeries: 'Series',
    indexCategory: 'Category',
    indexTags: 'Tags',
    indexAllTags: 'All tags',
    indexModels: 'Models',
    indexAllModels: 'All models',
    metaSummary: (models, artifacts) => `${models} models, ${artifacts} artifacts`,
    loading: 'Loading manifest...',
    loadError: 'Failed to load manifest.json',
    generatedFrom: 'Generated from',
    generatedJoin: 'and',
    firmwareType: 'Firmware Type',
    edkBaseline: 'EDK2 Baseline',
    refcodeBaseline: 'RefCode Baseline',
    boardId: 'Board ID',
    boardRev: 'Board Rev',
    version: 'Version',
    build: 'Build',
    releaseTime: 'Push Time',
    download: 'Download',
    noArtifacts: 'No artifacts found for this model.',
    expandMore: (count) => `Show more (${count})`,
    collapse: 'Collapse',
    na: 'N/A',
    colon: ': ',
  },
  zh: {
    eyebrow: '龙芯社区固件',
    heroTitle: '下载中心',
    subhead: '按机型分组的 BIOS/固件下载列表，可搜索或切换到完整历史。',
    repoLink: '访问 GitHub 仓库',
    searchLabel: '搜索',
    searchPlaceholder: '型号、系列或路径',
    latest: '最新',
    all: '全部',
    language: '语言',
    indexBy: '索引类型',
    indexAll: '全部',
    indexCollection: '集合',
    indexSeries: '系列',
    indexCategory: '类别',
    indexTags: '标签',
    indexAllTags: '全部标签',
    indexModels: '型号',
    indexAllModels: '全部型号',
    metaSummary: (models, artifacts) => `${models} 个机型，${artifacts} 个固件`,
    loading: '加载清单中...',
    loadError: 'manifest.json 加载失败',
    generatedFrom: '数据来源',
    generatedJoin: '、',
    firmwareType: '固件类型',
    edkBaseline: 'EDK2 基线',
    refcodeBaseline: 'RefCode 基线',
    boardId: '主板标识',
    boardRev: '主板版本',
    version: '版本号',
    build: '构建类型',
    releaseTime: '推送时间',
    download: '下载',
    noArtifacts: '该机型暂无固件。',
    expandMore: (count) => `展开更多（${count}）`,
    collapse: '收起',
    na: 'N/A',
    colon: '：',
  },
};

const DEFAULT_VISIBLE = 2;
const RAW_BASE_URL = 'https://raw.githubusercontent.com/loongson/firmware/main/';

function detectLanguage() {
  const stored = localStorage.getItem('fw_lang');
  if (stored && i18n[stored]) return stored;
  //const browser = (navigator.language || '').toLowerCase();
  //return browser.startsWith('zh') ? 'zh' : 'en';
  return 'en';
}

function applyLanguage(lang) {
  const locale = i18n[lang] || i18n.en;
  state.lang = lang;
  localStorage.setItem('fw_lang', lang);

  if (eyebrowEl) eyebrowEl.textContent = locale.eyebrow;
  if (heroTitleEl) heroTitleEl.textContent = locale.heroTitle;
  if (subheadEl) subheadEl.textContent = locale.subhead;
  if (repoLinkTextEl) repoLinkTextEl.textContent = locale.repoLink;
  if (searchLabelEl) searchLabelEl.textContent = locale.searchLabel;
  if (searchEl) searchEl.placeholder = locale.searchPlaceholder;
  if (footerTextEl) {
    footerTextEl.innerHTML = `${locale.generatedFrom} <code>manifest.json</code> ${locale.generatedJoin} <code>SHA256SUMS.txt</code>.`;
  }
  latestBtn.textContent = locale.latest;
  allBtn.textContent = locale.all;
  if (tagIndexLabelEl) tagIndexLabelEl.textContent = locale.indexBy;
  if (tagSelectLabelEl) tagSelectLabelEl.textContent = locale.indexTags;
  if (modelSelectLabelEl) modelSelectLabelEl.textContent = locale.indexModels;
  tagTabs.forEach((tab) => {
    const type = tab.dataset.tagType;
    if (type === 'all') tab.textContent = locale.indexAll;
    if (type === 'collection') tab.textContent = locale.indexCollection;
    if (type === 'series') tab.textContent = locale.indexSeries;
    if (type === 'category') tab.textContent = locale.indexCategory;
  });

  zhBtn.classList.toggle('is-active', lang === 'zh');
  enBtn.classList.toggle('is-active', lang === 'en');

  if (!state.manifest && metaEl) {
    metaEl.textContent = locale.loading;
  }
  updateTagOptions();
  updateModelOptions();
  render();
}

function normalize(value) {
  return (value || '').toLowerCase();
}

function uniqueSorted(values) {
  const list = Array.from(new Set(values.filter(Boolean)));
  return list.sort((a, b) => String(a).localeCompare(String(b)));
}

function buildTagValues(type, machines) {
  if (!type || type === 'all') return [];
  const values = machines.map((machine) => machine[type]).filter(Boolean);
  return uniqueSorted(values);
}

function updateTagOptions() {
  if (!tagSelectEl) return;
  const locale = i18n[state.lang] || i18n.en;
  const machines = state.manifest?.machines || [];
  const type = state.tagType || 'all';
  const values = buildTagValues(type, machines);

  tagSelectEl.innerHTML = '';
  const allOption = document.createElement('option');
  allOption.value = '';
  allOption.textContent = locale.indexAllTags;
  tagSelectEl.appendChild(allOption);

  values.forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    tagSelectEl.appendChild(option);
  });

  tagSelectEl.disabled = type === 'all';
  if (type === 'all') {
    state.tagValue = '';
    tagSelectEl.value = '';
  } else if (state.tagValue && values.includes(state.tagValue)) {
    tagSelectEl.value = state.tagValue;
  } else {
    state.tagValue = '';
    tagSelectEl.value = '';
  }
}

function updateModelOptions() {
  if (!modelSelectEl) return;
  const locale = i18n[state.lang] || i18n.en;
  const machines = state.manifest?.machines || [];
  const values = uniqueSorted(machines.map((machine) => machine.model || machine.group_path).filter(Boolean));

  modelSelectEl.innerHTML = '';
  const allOption = document.createElement('option');
  allOption.value = '';
  allOption.textContent = locale.indexAllModels;
  modelSelectEl.appendChild(allOption);

  values.forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    modelSelectEl.appendChild(option);
  });

  if (state.modelValue && values.includes(state.modelValue)) {
    modelSelectEl.value = state.modelValue;
  } else {
    state.modelValue = '';
    modelSelectEl.value = '';
  }
}

function buildTagList(machine) {
  const tags = [];
  if (machine.series) tags.push(machine.series);
  if (machine.category) tags.push(machine.category);
  if (machine.collection) tags.push(machine.collection);
  return tags;
}

function artifactTitleLine(artifact) {
  // Display title in a user-facing way:
  // UEFI / <BoardID> <BoardRev> / <BUILD>
  const baseline = artifact.edk2_baseline || artifact.edk || artifact.base || null;
  const fwType = (baseline && /^(EDK|UDK)/i.test(baseline))
    ? 'UEFI'
    : (artifact.firmware_type || artifact.fw_type || baseline || null);
  const boardId = artifact.board_id || artifact.machine || null;
  const boardRev = artifact.board_rev || artifact.version || null;
  const build = artifact.build ? artifact.build.toUpperCase() : null;

  const left = [
    fwType || 'N/A',
    (boardId ? `${boardId}${boardRev ? ' ' + boardRev : ''}` : 'N/A'),
  ].join(' / ');

  return build ? `${left} / ${build}` : left;
}


function artifactMetaLines(artifact) {
  // Key-value rows; missing values show as N/A.
  const locale = i18n[state.lang] || i18n.en;
  const baseline = artifact.edk2_baseline || artifact.edk || artifact.base || null;
  const fwType = (baseline && /^(EDK|UDK)/i.test(baseline))
    ? 'UEFI'
    : (artifact.firmware_type || artifact.fw_type || null);
  const refcode = artifact.refcode_base || artifact.release_tag || null;

  const boardId = artifact.board_id || artifact.machine || null;
  const boardRev = artifact.board_rev || artifact.version || null;

  // Prefer a fully-formed version string; otherwise compose from parts.
  const verFull = artifact.version_full
    || artifact.fw_version_full
    || (artifact.fw_version && artifact.stage ? `${artifact.fw_version}_${artifact.stage}` : artifact.fw_version)
    || null;

  const build = artifact.build || null;
  const releasedRaw = artifact.git_datetime || artifact.datetime || null;
  const released = releasedRaw ? releasedRaw.replace('T', ' ') : null;

  return [
    [locale.boardId, boardId],
    [locale.boardRev, boardRev],
    [locale.firmwareType, fwType || (baseline && /^(EDK|UDK)/i.test(baseline) ? 'UEFI' : null)],
    [locale.edkBaseline, baseline],
    [locale.refcodeBaseline, refcode],
    [locale.version, verFull],
    [locale.build, build],
    [locale.releaseTime, released],
  ].map(([k, v]) => `${k}${locale.colon}${v || locale.na}`);
}

function parseDateKey(text) {
  if (!text) return null;
  const m1 = text.match(/(20\d{6})/);
  if (m1) {
    const val = m1[1];
    return [Number(val.slice(0, 4)), Number(val.slice(4, 6)), Number(val.slice(6, 8))];
  }
  const m2 = text.match(/(20\d{4})/);
  if (m2) {
    const val = m2[1];
    return [Number(val.slice(0, 4)), Number(val.slice(4, 6)), 0];
  }
  const m3 = text.match(/(\d{2})(\d{2})[_-]?(\d{2})(\d{2})/);
  if (m3) {
    const [, yy, mm, dd1, dd2] = m3;
    return [2000 + Number(yy), Number(mm), Number(dd1 + dd2)];
  }
  const m4 = text.match(/(?<!\d)(\d{2})(\d{2})(?!\d)/);
  if (m4) {
    const [, yy, mm] = m4;
    return [2000 + Number(yy), Number(mm), 0];
  }
  return null;
}

function versionKey(version) {
  if (!version) return [];
  return (version.match(/\d+/g) || []).map((n) => Number(n));
}

function compareNumberArray(a = [], b = []) {
  const len = Math.max(a.length, b.length);
  for (let i = 0; i < len; i += 1) {
    const av = a[i] || 0;
    const bv = b[i] || 0;
    if (av !== bv) return av - bv;
  }
  return 0;
}

function artifactSortKey(artifact) {
  const ts = artifact?.timestamp || 0;
  const text = `${artifact?.refcode_base || ''} ${artifact?.path || ''}`;
  const dateKey = parseDateKey(text) || [0, 0, 0];
  const verKey = versionKey(artifact?.refcode_base);
  const edk = artifact?.edk || '';
  const build = artifact?.build || '';
  return { ts, dateKey, verKey, edk, build };
}

function compareArtifactKey(aKey, bKey) {
  if (aKey.ts !== bKey.ts) return aKey.ts - bKey.ts;
  const dateCmp = compareNumberArray(aKey.dateKey, bKey.dateKey);
  if (dateCmp) return dateCmp;
  const verCmp = compareNumberArray(aKey.verKey, bKey.verKey);
  if (verCmp) return verCmp;
  const edkCmp = aKey.edk.localeCompare(bKey.edk);
  if (edkCmp) return edkCmp;
  return aKey.build.localeCompare(bKey.build);
}

function bestArtifactKey(artifacts) {
  if (!Array.isArray(artifacts) || !artifacts.length) return null;
  let best = artifactSortKey(artifacts[0]);
  for (let i = 1; i < artifacts.length; i += 1) {
    const nextKey = artifactSortKey(artifacts[i]);
    if (compareArtifactKey(best, nextKey) < 0) {
      best = nextKey;
    }
  }
  return best;
}

function updateArtifactList(container, artifacts, key, toggle) {
  const locale = i18n[state.lang] || i18n.en;
  const isExpanded = expandedModels.has(key);
  const visibleCount = isExpanded
    ? artifacts.length
    : Math.min(DEFAULT_VISIBLE, artifacts.length);

  container.innerHTML = '';

  for (let i = 0; i < visibleCount; i += 1) {
    container.appendChild(createArtifactBox(artifacts[i]));
  }

  if (!artifacts.length) {
    const empty = document.createElement('div');
    empty.className = 'artifact';
    empty.textContent = locale.noArtifacts;
    container.appendChild(empty);
  }

  if (toggle) {
    toggle.textContent = isExpanded
      ? locale.collapse
      : locale.expandMore(artifacts.length - DEFAULT_VISIBLE);
  }
}


function matchQuery(machine, query) {
  if (!query) return true;
  const listLatest = machine.latest || [];
  const listAll = machine.artifacts || [];
  const haystack = [
    machine.series,
    machine.category,
    machine.model,
    machine.group_path,
    ...listLatest.flatMap((a) => [
      a.path,
      a.edk, a.base,
      a.board_rev, a.version,
      a.refcode_base, a.release_tag,
      a.build,
      a.firmware_type, a.fw_type,
    ]),
    ...listAll.flatMap((a) => [
      a.path,
      a.edk, a.base,
      a.board_rev, a.version,
      a.refcode_base, a.release_tag,
      a.build,
      a.firmware_type, a.fw_type,
    ]),
  ]
    .filter(Boolean)
    .map(normalize)
    .join(' ');
  return haystack.includes(query);
}

function matchTag(machine) {
  if (!state.tagType || state.tagType === 'all') return true;
  if (!state.tagValue) return true;
  return machine[state.tagType] === state.tagValue;
}

function matchModel(machine) {
  if (!state.modelValue) return true;
  return (machine.model || machine.group_path) === state.modelValue;
}

function createArtifactBox(artifact) {
  const locale = i18n[state.lang] || i18n.en;
  const box = document.createElement('div');
  box.className = 'artifact';

  const label = document.createElement('div');
  label.className = 'artifact-title';
  label.textContent = artifactTitleLine(artifact);

  const meta = document.createElement('div');
  meta.className = 'artifact-meta';
  artifactMetaLines(artifact).forEach((metaItem) => {
    const row = document.createElement('div');
    row.className = 'meta-row';
    row.textContent = metaItem;
    meta.appendChild(row);
  });

  const link = document.createElement('a');
  link.href = encodeURI(`${RAW_BASE_URL}${artifact.path}`);
  link.textContent = `${locale.download} ${artifact.path.split('/').pop()}`;
  link.setAttribute('download', '');

  const sha = document.createElement('div');
  sha.className = 'sha';
  sha.textContent = `SHA256: ${artifact.sha256 || 'unknown'}`;

  box.appendChild(label);
  if (meta.childNodes.length) box.appendChild(meta);
  box.appendChild(link);
  box.appendChild(sha);

  return box;
}

function render() {
  if (!state.manifest) return;
  const query = normalize(state.query);
  const machines = state.manifest.machines || [];
  const filtered = machines.filter((machine) => matchQuery(machine, query) && matchTag(machine) && matchModel(machine));

  const totalArtifacts = filtered.reduce((count, machine) => {
    const list = state.showAll ? machine.artifacts : machine.latest;
    return count + (Array.isArray(list) ? list.length : 0);
  }, 0);

  const locale = i18n[state.lang] || i18n.en;
  metaEl.textContent = locale.metaSummary(filtered.length, totalArtifacts);

  cardsEl.innerHTML = '';
  const sorted = filtered
    .map((machine) => {
      const candidates = (machine.latest && machine.latest.length)
        ? machine.latest
        : machine.artifacts;
      const key = bestArtifactKey(candidates);
      return {
        machine,
        hasArtifacts: Array.isArray(candidates) && candidates.length > 0,
        sortKey: key,
      };
    })
    .sort((a, b) => {
      if (a.hasArtifacts !== b.hasArtifacts) return a.hasArtifacts ? -1 : 1;
      if (a.sortKey && b.sortKey) {
        return compareArtifactKey(b.sortKey, a.sortKey);
      }
      const aName = `${a.machine.series || ''}-${a.machine.category || ''}-${a.machine.model || ''}`;
      const bName = `${b.machine.series || ''}-${b.machine.category || ''}-${b.machine.model || ''}`;
      return aName.localeCompare(bName);
    });

  sorted.forEach(({ machine }, index) => {
      const card = document.createElement('article');
      card.className = 'card';
      card.style.setProperty('--i', index);

      const title = document.createElement('h2');
      title.textContent = machine.model || machine.group_path || 'Unknown model';

      const tags = document.createElement('div');
      tags.className = 'tags';
      buildTagList(machine).forEach((tagText) => {
        const tag = document.createElement('span');
        tag.className = 'tag';
        tag.textContent = tagText;
        tags.appendChild(tag);
      });

      const group = document.createElement('div');
      group.className = 'artifact-meta';
      group.textContent = machine.group_path || '';

      const list = state.showAll ? machine.artifacts : machine.latest;
      const artifacts = Array.isArray(list) ? list : [];

      card.appendChild(title);
      if (tags.childNodes.length) card.appendChild(tags);
      if (group.textContent) card.appendChild(group);

      // Collapsible list inside each model card.
      const key = machine.group_path || machine.model || String(index);
      const artifactList = document.createElement('div');
      artifactList.className = 'artifact-list';
      updateArtifactList(artifactList, artifacts, key, null);
      card.appendChild(artifactList);

      if (artifacts.length > DEFAULT_VISIBLE) {
        const toggle = document.createElement('button');
        toggle.className = 'artifact-toggle';
        toggle.type = 'button';
        toggle.textContent = expandedModels.has(key)
          ? locale.collapse
          : locale.expandMore(artifacts.length - DEFAULT_VISIBLE);

        toggle.addEventListener('click', () => {
          if (expandedModels.has(key)) {
            expandedModels.delete(key);
          } else {
            expandedModels.add(key);
          }
          updateArtifactList(artifactList, artifacts, key, toggle);
          card.scrollIntoView({ block: 'start', behavior: 'smooth' });
        });

        card.appendChild(toggle);
      }

      cardsEl.appendChild(card);
    });
}

function setMode(showAll) {
  state.showAll = showAll;
  latestBtn.classList.toggle('is-active', !showAll);
  allBtn.classList.toggle('is-active', showAll);
  render();
}

searchEl.addEventListener('input', (event) => {
  state.query = event.target.value;
  render();
});

latestBtn.addEventListener('click', () => setMode(false));
allBtn.addEventListener('click', () => setMode(true));
zhBtn.addEventListener('click', () => applyLanguage('zh'));
enBtn.addEventListener('click', () => applyLanguage('en'));
tagTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    const type = tab.dataset.tagType || 'all';
    state.tagType = type;
    state.tagValue = '';
    tagTabs.forEach((btn) => btn.classList.toggle('is-active', btn === tab));
    updateTagOptions();
    render();
  });
});

if (tagSelectEl) {
  tagSelectEl.addEventListener('change', (event) => {
    state.tagValue = event.target.value;
    render();
  });
}

if (modelSelectEl) {
  modelSelectEl.addEventListener('change', (event) => {
    state.modelValue = event.target.value;
    render();
  });
}

fetch('manifest.json')
  .then((resp) => {
    if (!resp.ok) throw new Error(i18n[state.lang]?.loadError || i18n.en.loadError);
    return resp.json();
  })
  .then((data) => {
    state.manifest = data;
    updateTagOptions();
    updateModelOptions();
    render();
  })
  .catch((err) => {
    metaEl.textContent = err.message;
  });

applyLanguage(detectLanguage());
