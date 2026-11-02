"use strict";
// The generator orders every download by repository update time.
const $ = (id) => document.getElementById(id);
let savedLanguage;
try {
  savedLanguage = localStorage.getItem("fw_lang");
} catch (_) {
  /* file/private mode */
}
const state = {
  lang: ["zh", "en"].includes(savedLanguage)
    ? savedLanguage
    : navigator.language.startsWith("zh")
      ? "zh"
      : "en",
  query: "",
  series: "",
  category: "",
  kind: "all",
  sort: "model",
};
const catalog = window.FIRMWARE_CATALOG;
const machines = Array.isArray(catalog?.machines) ? catalog.machines : [];
const words = {
  zh: {
    title: "找到主板，再选固件。",
    releaseNotes: "更新说明",
    baselineNotes: "基线更新说明",
    notesScope: "这里记录公共参考代码基线的变化，不是当前板卡的完整更新记录；具体功能是否适用，请以板卡说明为准。",
    notesIntro: "按参考代码基线查阅仓库已有的更新文档。文档在 GitHub 中打开。",
    notesEmpty: "暂无对应的更新说明。",
    notesZh: "中文说明 ↗",
    notesEn: "英文说明 ↗",
    notesFallback: "（仅中文）",
    notesFallbackEn: "（仅英文）",
    subtitle:
      "按机型查找固件映像、压缩包和官方支持入口。先确认硬件版本，再进行更新。",
    series: "系列",
    category: "用途",
    sort: "排序",
    sortModel: "默认（图片优先）",
    sortUpdated: "最近仓库更新",
    all: "全部",
    image: "固件映像",
    archive: "压缩包",
    external: "厂商链接",
    encrypted: "加密映像",
    tool: "工具",
    models: "机型",
    files: "文件",
    externalCount: "外部入口",
    loading: "正在读取仓库清单…",
    noMatch: "没有匹配的机型",
    trySearch: "试试缩短关键词，或清除筛选条件。",
    reset: "清除筛选",
    rulesTitle: "排序与时间说明",
    rulesLatest:
      "全部文件按仓库更新时间从新到旧排列；时间相同时按文件名排序，缺少时间的放最后。不判断最新固件版本，也不自动推荐刷写。",
    rulesTime:
      "发布日期、构建时间和仓库更新时间分别显示。仓库更新时间来自文件的 Git 提交记录，不是发布时间或推送时间；缺少的信息不推测。",
    rulesFormat:
      "压缩包需先阅读包内说明；文件格式不能证明适用性。校验值只标识文件完整性，不代表兼容性验证。",
    footer: "源自仓库文件与机型元数据 · 不自动推荐刷写",
    search: "搜索型号、版本或文件名…",
    result: (n) => `${n} 个匹配条目`,
    noPhoto: "暂无主板照片",
    details: "查看详情 →",
    updated: "仓库更新",
    unknown: "未提供",
    noVersion: "版本未标注",
    officialOnly: "通过官方支持页面获取固件及更新指导。",
    fileCount: (n) => `${n} 个文件 · 按仓库更新时间排列`,
    back: "← 返回机型目录",
    doc: "主板说明 ↗",
    support: "前往官方支持 ↗",
    upstream: "上游仓库 ↗",
    upstreamNote: "可前往上游仓库跟踪最新版本与开发进展；本站收录的文件不一定是上游最新版。",
    hardware: "硬件版本",
    variant: "功能变体",
    mainlineDvfsNote: "mainline-dvfs：供社区主线内核调频支持使用的预览版本。",
    fieldGuide: "固件字段说明",
    relNote: "rel：Release 版本，不包含调试打印信息。",
    dbgNote: "dbg：Debug 版本，包含调试打印信息。",
    noGmemNote: "NoGmem：适用于主板未安装板载显存颗粒的特别定制机型，仅支持外接独立显卡。",
    rcBaseline: "参考代码主基线",
    edk2Baseline: "EDK2上游基线",
    build: "构建类型",
    release: "发布日期",
    built: "构建时间",
    timezone: "UTC+08:00",

    downloads: "固件与下载",
    download: "下载文件 ↗",
    downloadArchive: "下载压缩包 ↗",
    warning:
      "刷写前请核对主板型号、硬件版本和固件说明。照片仅供识别，不作为兼容性依据。",
    externalTitle: "此机型提供官方支持入口",
    externalNote:
      "本仓库不托管此机型的固件。版本、发布日期及更新方法请以官方页面为准。",
    archiveNote:
      "这是压缩包，请先查看包内说明，不要将压缩包直接当作固件映像刷写。",
    encryptedNote: "这是加密文件，请先确认解密及更新方法。",
    checksum: "SHA256 校验值",
    noChecksum: "未提供 SHA256 校验值",
    copy: "复制",
    copied: "已复制",
    copyFail: "复制不可用，请手动选择校验值",
    size: "文件大小",
    unclassified: "未标注 / 未确认",

    latestNote:
      "显示全部文件，按仓库更新时间倒序。最近更新不代表最新版本或推荐刷写。",
    noFiles: "没有本地下载文件",
    source: "数据基线",
    error: "清单加载失败。请先运行 scripts/generate-manifest.py。",
    photoOpen: "查看完整主板照片",
    VirtualMachine: "虚拟机 / QEMU、KVM",
    PC: "台式机",
    Server: "服务器",
    Laptop: "笔记本",
    Other: "其他",

  },
  en: {
    title: "Find your board. Choose your firmware.",
    releaseNotes: "Release notes",
    baselineNotes: "Baseline release notes",
    notesScope: "These documents describe shared ReferenceCode baseline changes, not the complete changelog for a specific board. Check the board documentation for applicability.",
    notesIntro: "Browse existing release documents by ReferenceCode baseline. Documents open on GitHub.",
    notesEmpty: "No matching release notes are available.",
    notesZh: "Chinese notes ↗",
    notesEn: "English notes ↗",
    notesFallback: " (Chinese only)",
    notesFallbackEn: " (English only)",
    subtitle:
      "Firmware images, archives and official support, organized by model. Check your hardware revision before updating.",
    series: "Series",
    category: "Category",
    sort: "Sort",
    sortModel: "Default (photos first)",
    sortUpdated: "Repository update",
    all: "All",
    image: "Images",
    archive: "Archives",
    external: "Vendor links",
    encrypted: "Encrypted images",
    tool: "Tools",
    models: "Models",
    files: "Files",
    externalCount: "External links",
    loading: "Loading repository catalog…",
    noMatch: "No matching models",
    trySearch: "Try a shorter search or clear the filters.",
    reset: "Clear filters",
    rulesTitle: "Sorting and dates",
    rulesLatest:
      "All files are sorted by repository update time, newest first. Ties use filenames; missing dates come last. No latest-version selection or flashing recommendation is made.",
    rulesTime:
      "Release, build and repository-update dates are separate. Repository updates use the file’s Git commit record, not a release or push timestamp. Missing dates are not inferred.",
    rulesFormat:
      "Read the instructions inside archives. A file format does not establish compatibility; a checksum identifies file integrity, not compatibility testing.",
    footer:
      "Repository files + model metadata · No automatic flashing recommendations",
    search: "Search model, version or filename…",
    result: (n) => `${n} matching entries`,
    noPhoto: "NO BOARD PHOTO",
    details: "View details →",
    updated: "Repository update",
    unknown: "Not provided",
    noVersion: "Unspecified version",
    officialOnly:
      "Get firmware and update instructions from the official support page.",
    fileCount: (n) => `${n} files · Ordered by repository update`,
    back: "← Back to models",
    doc: "Board documentation ↗",
    support: "Official support ↗",
    upstream: "Upstream repository ↗",
    upstreamNote: "Follow the upstream repository for the latest versions and development updates. Files listed here may not be the latest upstream release.",
    hardware: "Hardware revision",
    variant: "Feature variant",
    mainlineDvfsNote: "mainline-dvfs: Preview firmware for CPU frequency scaling support in community mainline kernels.",
    fieldGuide: "Firmware field guide",
    relNote: "rel: Release build without debug logging.",
    dbgNote: "dbg: Debug build with debug logging.",
    noGmemNote: "NoGmem: Custom firmware for special board configurations without onboard graphics-memory chips; only an external discrete graphics card is supported.",
    rcBaseline: "ReferenceCode baseline",
    edk2Baseline: "EDK2 upstream baseline",
    build: "Build type",
    release: "Release date",
    built: "Build time",
    timezone: "UTC+08:00",

    downloads: "Firmware & downloads",
    download: "Download file ↗",
    downloadArchive: "Download archive ↗",
    warning:
      "Verify the exact model, hardware revision and firmware instructions before flashing. Photos are for identification, not evidence of compatibility.",
    externalTitle: "Official support is available for this model",
    externalNote:
      "This repository does not host firmware for this model. Check the official page for versions, release dates and update instructions.",
    archiveNote:
      "This is an archive. Read the enclosed instructions; do not flash the archive itself as a firmware image.",
    encryptedNote:
      "This file is encrypted. Check the decryption and update instructions first.",
    checksum: "SHA256 checksum",
    noChecksum: "SHA256 checksum not provided",
    copy: "Copy",
    copied: "Copied",
    copyFail: "Copy unavailable; select the checksum manually",
    size: "File size",
    unclassified: "Unspecified / unconfirmed",

    latestNote:
      "All files are shown, newest repository updates first. Recently updated does not mean latest version or recommended firmware.",
    noFiles: "No local downloads",
    source: "Data revision",
    error:
      "Catalog could not be loaded. Run scripts/generate-manifest.py first.",
    photoOpen: "View full board photo",
    VirtualMachine: "Virtual machine / QEMU, KVM",
    PC: "Desktop",
    Server: "Server",
    Laptop: "Laptop",
    Other: "Other",
    group: "Compatibility group",
  },
};
const t = (key, ...args) =>
  typeof words[state.lang][key] === "function"
    ? words[state.lang][key](...args)
    : words[state.lang][key] || key;
const el = (tag, className, text) => {
  const e = document.createElement(tag);
  if (className) e.className = className;
  if (text !== undefined) e.textContent = text;
  return e;
};
function safeURL(value) {
  if (!value || typeof value !== "string") return null;
  try {
    const url = new URL(value, location.href);
    if (["https:", "http:"].includes(url.protocol)) return url.href;
    if (
      location.protocol === "file:" &&
      url.protocol === "file:" &&
      !value.includes("://") &&
      !value.startsWith("//")
    )
      return url.href;
  } catch (_) {
    /* malformed catalog URL */
  }
  return null;
}
function link(text, href, className) {
  const a = el("a", className, text);
  const url = safeURL(href);
  if (url) {
    a.href = url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
  }
  return a;
}
function badge(text, cls = "") {
  return el("span", `badge ${cls}`, text);
}
function date(value, full = false) {
  if (!value) return t("unknown");
  if (/^\d{4}-\d{2}(-\d{2})?$/.test(value)) return value;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return t("unknown");
  return (
    new Intl.DateTimeFormat(state.lang === "zh" ? "zh-CN" : "en-GB", {
      timeZone: "Asia/Shanghai",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      ...(full ? { hour: "2-digit", minute: "2-digit", hourCycle: "h23" } : {}),
    }).format(d) + (full ? " UTC+08:00" : "")
  );
}
function bytes(n) {
  if (n === null || n === undefined) return t("unknown");
  if (n < 1024) return `${n} B`;
  if (n < 1048576) return `${(n / 1024).toFixed(1)} KiB`;
  return `${(n / 1048576).toFixed(1)} MiB`;
}
function kinds(m) {
  return [
    ...new Set([
      ...(m.artifacts || []).map((a) => a.kind),
      ...(m.category === "tool" ? ["tool"] : []),
      ...(m.support_url ? ["external"] : []),
    ]),
  ];
}
function placeholder() {
  const box = el("div", "photo-placeholder");
  box.innerHTML =
    '<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="12" y="8" width="40" height="48" rx="3"/><rect x="22" y="18" width="16" height="16" rx="2"/><path d="M18 42h28M18 48h20M44 16v18M8 18h4M8 26h4M8 34h4M52 18h4M52 26h4M52 34h4"/></svg>';
  box.append(el("span", "", t("noPhoto")));
  return box;
}
function photo(m, className, zoom = false) {
  const box = el("div", className);
  const url = safeURL(m.image_url);
  if (!url) {
    box.append(placeholder());
    return box;
  }
  const img = el("img");
  img.alt = m.model;
  img.src = url;
  img.loading = zoom ? "eager" : "lazy";
  img.decoding = "async";
  img.addEventListener("error", () => box.replaceChildren(placeholder()), {
    once: true,
  });
  if (zoom) {
    const a = link("", url);
    a.setAttribute("aria-label", t("photoOpen"));
    a.append(img);
    box.append(a);
  } else box.append(img);
  return box;
}
function optionList(id, values, label) {
  const select = $(id);
  const current = state[id];
  select.replaceChildren();
  const all = el("option", "", `${label} · ${t("all")}`);
  all.value = "";
  select.append(all);
  for (const v of [...new Set(values.filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, undefined, { numeric: true }),
  )) {
    const op = el("option", "", id === "category" ? t(v) : v);
    op.value = v;
    select.append(op);
  }
  select.value = current;
}
function applyLanguage() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  document.title =
    state.lang === "zh"
      ? "LoongArch · 固件目录"
      : "LoongArch · Firmware catalog";
  document
    .querySelectorAll("[data-i18n]")
    .forEach((e) => (e.textContent = t(e.dataset.i18n)));
  $("language").textContent = state.lang === "zh" ? "English" : "中文";
  $("search").placeholder = t("search");
  $("search").setAttribute("aria-label", t("search"));
  $("series").setAttribute("aria-label", t("series"));
  $("category").setAttribute("aria-label", t("category"));
  $("sort").setAttribute("aria-label", t("sort"));
  optionList(
    "series",
    machines.map((m) => m.series),
    t("series"),
  );
  optionList(
    "category",
    machines.map((m) => m.category),
    t("category"),
  );
  renderSummary();
  renderCards();
  renderRoute(false);
}
function renderSummary() {
  const stats = [
    [machines.filter((m) => Boolean(m.series) || m.category === "VirtualMachine").length, "models"],
    [machines.reduce((n, m) => n + (m.artifacts || []).length, 0), "files"],
    [machines.filter((m) => m.support_url).length, "externalCount"],
  ];
  $("summary").replaceChildren(
    ...stats.map(([n, key]) => {
      const e = el("div", "stat");
      e.append(el("strong", "", n), el("span", "", t(key)));
      return e;
    }),
  );
  $("provenance").textContent = catalog?.source_commit
    ? `${t("source")} · ${catalog.source_commit.slice(0, 8)}`
    : "";
}
function renderCards() {
  const chips = $("kind-filter");
  chips.replaceChildren();
  for (const kind of [
    "all",
    "image",
    "archive",
    "external",
    "encrypted",
    "tool",
  ]) {
    const count = machines.filter(
      (m) => kind === "all" || kinds(m).includes(kind),
    ).length;
    if (!count && kind !== "all") continue;
    const b = el(
      "button",
      `chip ${state.kind === kind ? "active" : ""}`,
      t(kind),
    );
    b.type = "button";
    b.dataset.kind = kind;
    b.setAttribute("aria-pressed", String(state.kind === kind));
    b.append(el("span", "count", count));
    b.onclick = () => {
      state.kind = kind;
      renderCards();
    };
    chips.append(b);
  }
  const q = state.query.trim().toLowerCase();
  const list = machines.filter(
    (m) =>
      (!state.series || m.series === state.series) &&
      (!state.category || m.category === state.category) &&
      (state.kind === "all" || kinds(m).includes(state.kind)) &&
      (!q ||
        [
          m.model,
          m.group_path,
          m.series,
          ...(m.artifacts || []).flatMap((a) => [
            a.filename,
            a.version,
            a.hardware_rev,
            a.variant,
          ]),
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase()
          .includes(q)),
  );
  list.sort((a, b) => {
    if (state.sort === "model" && Boolean(a.image_url) !== Boolean(b.image_url))
      return a.image_url ? -1 : 1;
    if (state.sort === "updated") {
      const delta =
        (Date.parse(b.updated_at) || 0) - (Date.parse(a.updated_at) || 0);
      if (delta) return delta;
    }
    if (Boolean(a.series) !== Boolean(b.series)) return a.series ? -1 : 1;
    return `${a.series || ""}|${a.category || ""}|${a.model}|${a.collection || ""}`.localeCompare(
      `${b.series || ""}|${b.category || ""}|${b.model}|${b.collection || ""}`,
      undefined,
      { numeric: true },
    );
  });
  $("result-count").textContent = t("result", list.length);
  $("empty").hidden = !!list.length;
  $("cards").replaceChildren();
  $("cards").setAttribute("aria-busy", "false");
  for (const m of list) {
    const card = el("article", "card");
    card.dataset.model = m.model;
    card.append(photo(m, "card-photo"));
    const body = el("div", "card-body");
    body.append(
      el(
        "div",
        "card-topline",
        [m.series, t(m.category || "Other"), m.collection]
          .filter(Boolean)
          .join(" / "),
      ),
      el("h2", "", m.model),
    );
    const tags = el("div", "tag-row");
    kinds(m).forEach((k) => tags.append(badge(t(k), k)));
    body.append(
      tags,
      el(
        "p",
        "card-note",
        (m.artifacts || []).length
          ? t("fileCount", m.artifacts.length)
          : m.support_url ? t("officialOnly") : t("noFiles"),
      ),
    );
    card.append(body);
    const foot = el("div", "card-bottom");
    foot.append(el("span", "", `${t("updated")} · ${date(m.updated_at)}`));
    const a = el("a", "", t("details"));
    a.href = `#model=${encodeURIComponent(m.id || m.group_path)}`;
    a.setAttribute("aria-label", `${m.model} · ${t("details")}`);
    foot.append(a);
    card.append(foot);
    $("cards").append(card);
  }
}
function selectedModel() {
  if (!location.hash.startsWith("#model=")) return null;
  try {
    const id = decodeURIComponent(location.hash.slice(7));
    return machines.find((m) => (m.id || m.group_path) === id) || null;
  } catch (_) {
    return null;
  }
}
function notesFor(a) {
  const candidates = (catalog.release_notes || []).filter(n => n.baseline === a.rc_baseline);
  const exact = candidates.filter(n => n.version && a.firmware_version && n.version.toLowerCase() === a.firmware_version.toLowerCase());
  if (exact.length === 1) return exact[0];
  const defaults = candidates.filter(n => n.default === true);
  if (defaults.length === 1) return defaults[0];
  return candidates.length === 1 ? candidates[0] : null;
}
function artifactBox(a) {
  const box = el("article", "artifact");
  box.dataset.path = a.path;
  const row = el("div", "artifact-title-row");
  const title = el("div");
  title.append(
    el("h3", "artifact-title", a.version || a.filename || t("noVersion")),
  );
  const tags = el("div", "tag-row");
  tags.append(badge(t(a.kind), a.kind), badge((a.format || "").toUpperCase()));
  if (a.build) tags.append(badge(a.build));

  title.append(tags);
  row.append(title);
  if (safeURL(a.url))
    row.append(
      link(
        t(a.kind === "archive" ? "downloadArchive" : "download"),
        a.url,
        "primary",
      ),
    );
  box.append(row, el("p", "artifact-file", a.filename || a.path));
  const meta = el("dl", "artifact-meta");
  for (const [key, value] of [
    ["hardware", a.hardware_rev || t("unclassified")],
    ["variant", a.variant || t("unclassified")],
    ["rcBaseline", a.rc_baseline || t("unknown")],
    ["edk2Baseline", a.edk2_baseline || t("unknown")],
    ["release", date(a.release_date)],
    ["built", date(a.build_date, true)],
    ["updated", date(a.updated_at, true)],
    ["size", bytes(a.size_bytes)],
  ]) {
    const pair = el("div");
    pair.append(el("dt", "", t(key)), el("dd", "", value));
    meta.append(pair);
  }
  box.append(meta);
  const notes = notesFor(a);
  if (notes) {
    const language = notes.documents[state.lang] ? state.lang : (notes.documents.zh ? "zh" : "en");
    const suffix = language === state.lang ? "" : t(language === "zh" ? "notesFallback" : "notesFallbackEn");
    const noteLink = link(t("baselineNotes") + suffix + " ↗", notes.documents[language], "text-link");
    noteLink.title = t("notesScope");
    const noteRow = el("p", "release-note-link");
    noteRow.append(noteLink);
    box.append(noteRow);
  }

  if (a.kind === "archive" || a.kind === "encrypted")
    box.append(
      el(
        "p",
        "artifact-warning",
        t(a.kind === "archive" ? "archiveNote" : "encryptedNote"),
      ),
    );
  if (a.sha256) {
    const d = el("details", "artifact-check");
    d.append(el("summary", "", t("checksum")));
    const content = el("div", "checksum");
    const code = el("code", "", a.sha256);
    const b = el("button", "", t("copy"));
    b.type = "button";
    b.onclick = async () => {
      try {
        await navigator.clipboard.writeText(a.sha256);
        b.textContent = t("copied");
      } catch (_) {
        b.textContent = t("copyFail");
        const range = document.createRange();
        range.selectNodeContents(code);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      }
    };
    content.append(code, b);
    d.append(content);
    box.append(d);
  } else box.append(el("p", "artifact-warning", t("noChecksum")));
  return box;
}
function renderDetail(m, focus) {
  const view = $("detail-view");
  view.replaceChildren();
  const back = el("a", "back", t("back"));
  back.href = "#";
  view.append(back);
  const hero = el("div", "detail-hero");
  hero.append(photo(m, "detail-image", true));
  const info = el("div", "detail-info");
  info.append(
    el(
      "p",
      "eyebrow",
      [m.series, t(m.category || "Other")].filter(Boolean).join(" / "),
    ),
  );
  const h = el("h1", "", m.model);
  h.tabIndex = -1;
  info.append(h);
  const tags = el("div", "tag-row");
  kinds(m).forEach((k) => tags.append(badge(t(k), k)));
  info.append(tags);
  const actions = el("div", "detail-actions");
  const doc =
    state.lang === "zh"
      ? m.readme_zh_url || m.readme_url
      : m.readme_url || m.readme_zh_url;
  if (safeURL(doc)) actions.append(link(t("doc"), doc, "secondary"));
  if (safeURL(m.support_url))
    actions.append(link(t("support"), m.support_url, "primary"));
  if (safeURL(m.upstream_url))
    actions.append(link(t("upstream"), m.upstream_url, "secondary"));
  info.append(
    actions,
    el("p", "detail-note", `${t("updated")} · ${date(m.updated_at, true)}`),
  );
  if (safeURL(m.upstream_url))
    info.append(el("p", "detail-note", t("upstreamNote")));
  hero.append(info);
  view.append(hero, el("aside", "notice", t("warning")));
  if (m.support_url) {
    const panel = el("div", "external-panel");
    panel.append(
      el("h2", "", t("externalTitle")),
      el(
        "p",
        "",
        (m.artifacts || []).length ? t("officialOnly") : t("externalNote"),
      ),
      link(t("support"), m.support_url, "secondary"),
    );
    view.append(panel);
  }
  if ((m.artifacts || []).length) {
    const heading = el("div", "artifact-heading");
    heading.append(el("h2", "", t("downloads")));
    view.append(heading, el("p", "history-note", t("latestNote")));
    if (m.artifacts.some(a => notesFor(a)))
      view.append(el("p", "history-note", t("notesScope")));
    const guide = el("details", "rules field-guide");
    guide.append(el("summary", "", t("fieldGuide")));
    const guideBody = el("div", "rules-body");
    for (const key of ["relNote", "dbgNote", "noGmemNote", "mainlineDvfsNote"])
      guideBody.append(el("p", "", t(key)));
    guide.append(guideBody);
    view.append(guide);
    const list = el("div", "artifact-list");
    for (const a of m.artifacts) {
      list.append(artifactBox(a));
    }
    view.append(list);
  }
  if (focus) {
    h.focus({ preventScroll: true });
    window.scrollTo(0, 0);
  }
}
function renderReleaseNotes(focus) {
  const view = $("release-notes-view");
  view.replaceChildren();
  const back = el("a", "back", t("back"));
  back.href = "#";
  const heading = el("h1", "", t("releaseNotes"));
  heading.tabIndex = -1;
  view.append(back, heading, el("p", "lede", t("notesIntro")), el("aside", "notice", t("notesScope")));
  for (const notes of catalog.release_notes || []) {
    const card = el("article", "external-panel release-note-card");
    card.append(el("h2", "", notes.title), badge(notes.baseline));
    const actions = el("div", "detail-actions");
    const languages = state.lang === "zh" ? ["zh", "en"] : ["en", "zh"];
    let first = true;
    for (const language of languages) {
      if (!safeURL(notes.documents[language])) continue;
      actions.append(link(t(language === "zh" ? "notesZh" : "notesEn"), notes.documents[language], first ? "primary" : "secondary"));
      first = false;
    }
    card.append(actions);
    view.append(card);
  }
  if (!(catalog.release_notes || []).length) view.append(el("p", "", t("notesEmpty")));
  if (focus) { heading.focus({preventScroll: true}); window.scrollTo(0, 0); }
}
function renderRoute(focus = true) {
  const model = selectedModel();
  const showNotes = location.hash === "#release-notes";
  $("catalog-view").hidden = !!model || showNotes;
  $("detail-view").hidden = !model;
  $("release-notes-view").hidden = !showNotes;
  $("rules").hidden = showNotes;
  if (showNotes) renderReleaseNotes(focus);
  else if (model) renderDetail(model, focus);
  else if (focus) window.scrollTo(0, 0);
}
$("search").addEventListener("input", (e) => {
  state.query = e.target.value;
  renderCards();
});
for (const id of ["series", "category", "sort"])
  $(id).addEventListener("change", (e) => {
    state[id] = e.target.value;
    renderCards();
  });
$("language").onclick = () => {
  state.lang = state.lang === "zh" ? "en" : "zh";
  try {
    localStorage.setItem("fw_lang", state.lang);
  } catch (_) {}
  applyLanguage();
};
$("reset").onclick = () => {
  Object.assign(state, {
    query: "",
    series: "",
    category: "",
    kind: "all",
    sort: "model",
  });
  $("search").value = "";
  $("sort").value = "model";
  applyLanguage();
};
window.addEventListener("hashchange", () => {
  renderRoute();
});
window.addEventListener("keydown", (e) => {
  if (
    e.key === "/" &&
    !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName) &&
    !selectedModel()
  ) {
    e.preventDefault();
    $("search").focus();
  }
});
if (!catalog || !Array.isArray(catalog.machines)) {
  document
    .querySelectorAll("[data-i18n]")
    .forEach((e) => (e.textContent = t(e.dataset.i18n)));
  $("cards").replaceChildren(el("p", "error", t("error")));
  $("cards").setAttribute("aria-busy", "false");
} else applyLanguage();
