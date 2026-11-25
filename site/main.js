// GitHub "owner/repo" that publishes the release downloads.
const REPO = "grainandglow/preset-picker";

const $ = s => document.querySelector(s);
const repoUrl = `https://github.com/${REPO}`;
const assetUrl = name => `${repoUrl}/releases/latest/download/${name}`;

for (const a of document.querySelectorAll("[data-repo-link]")) a.href = repoUrl + (a.dataset.path || "");
for (const a of document.querySelectorAll("[data-asset]")) a.href = assetUrl(a.dataset.asset);

/* Which build fits this visitor? */
async function detect() {
  const ua = navigator.userAgent;
  let os = /Windows/.test(ua) ? "win" : /Macintosh|Mac OS X/.test(ua) && !/iPhone|iPad/.test(ua) ? "mac" : null;
  let arch = null;
  try {
    const v = await navigator.userAgentData?.getHighEntropyValues(["architecture", "platform"]);
    if (v) {
      if (v.platform === "Windows") os = "win";
      if (v.platform === "macOS") os = "mac";
      arch = v.architecture;            // "x86" or "arm"
    }
  } catch { /* not available in Safari / Firefox */ }
  if (os === "mac" && !arch) {
    // Safari doesn't expose the CPU; the GPU name does ("Apple M1" vs "Intel").
    try {
      const gl = document.createElement("canvas").getContext("webgl");
      const ext = gl.getExtension("WEBGL_debug_renderer_info");
      const gpu = gl.getParameter(ext ? ext.UNMASKED_RENDERER_WEBGL : gl.RENDERER) || "";
      if (/Intel|AMD|Radeon/i.test(gpu)) arch = "x86";
      else if (/Apple/i.test(gpu)) arch = "arm";
    } catch { /* ignore */ }
  }
  return { os, arch };
}

detect().then(({ os, arch }) => {
  const hero = $("#heroDownload");
  const hint = $("#heroHint");
  let pick = null;
  if (os === "win") {
    pick = arch === "arm" ? "#win-arm64" : "#win-x64";
    $("#dl-win").classList.add("mine");
    hero.textContent = "Download for Windows";
    hint.textContent = arch === "arm" ? "Free · Windows 11 on ARM" : "Free · Windows 10 & 11";
  } else if (os === "mac") {
    $("#dl-mac").classList.add("mine");
    if (arch === "x86") {
      $("#intelMac").hidden = false;
      hint.textContent = "Needs a Mac with Apple Silicon (M1 or newer)";
    } else {
      pick = "#mac-arm64";
      hero.textContent = "Download for Mac";
      hint.textContent = "Free · macOS 11+ · Apple Silicon";
    }
  }
  if (pick) {
    $(pick).classList.add("pick");
    hero.href = $(pick).href;
  }
});

/* Version and file sizes from the latest GitHub release. */
fetch(`https://api.github.com/repos/${REPO}/releases/latest`)
  .then(r => (r.ok ? r.json() : Promise.reject(r.status)))
  .then(rel => {
    const date = new Date(rel.published_at).toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" });
    $("#version").textContent = `Version ${rel.tag_name.replace(/^v/, "")} · ${date}`;
    for (const a of document.querySelectorAll("[data-asset]")) {
      const asset = rel.assets.find(x => x.name === a.dataset.asset);
      const size = a.querySelector(".size");
      if (!asset) a.classList.add("disabled");
      else if (size) size.textContent = `${Math.round(asset.size / 1e6)} MB`;
    }
  })
  .catch(() => { $("#version").textContent = "Free download"; });

/* Before/after slider */
const compare = $("#compare");
$("#slider").addEventListener("input", e => compare.style.setProperty("--pos", e.target.value + "%"));
