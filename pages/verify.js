
    const statusBox = document.getElementById("status");
    const detailsSection = document.getElementById("details");
    const commitShaEl = document.getElementById("commit-sha");
    const commitAuthorEl = document.getElementById("commit-author");
    const commitDateEl = document.getElementById("commit-date");
    const branchHeadEl = document.getElementById("branch-head");
    const form = document.getElementById("manual-check");
    const pageTitleEl = document.getElementById("page-title");
    const headingEl = document.getElementById("page-heading");
    const introTextEl = document.getElementById("intro-text");

    function escapeHtml(str) {
      return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

    function updateStatus(type, message, sub) {
      statusBox.dataset.state = type;
      statusBox.innerHTML = `<strong>${escapeHtml(message)}</strong>` + (sub ? `<span>${escapeHtml(sub)}</span>` : "");
      // Trigger animation by removing and re-adding the class
      statusBox.style.animation = 'none';
      statusBox.offsetHeight; // Trigger reflow
      statusBox.style.animation = '';
    }

    function formatDate(iso) {
      try {
        return new Intl.DateTimeFormat(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        }).format(new Date(iso));
      } catch (err) {
        return iso;
      }
    }

    function showDetails(data) {
      detailsSection.hidden = false;
      commitShaEl.innerHTML = `<a href="https://github.com/${encodeURIComponent(data.repo)}/commit/${encodeURIComponent(data.sha)}" target="_blank" rel="noopener" class="truncate" data-full-text="${escapeHtml(data.sha)}">${escapeHtml(data.sha)}</a>`;
      commitAuthorEl.textContent = `${data.author} (${data.email})`;
      commitDateEl.textContent = formatDate(data.date);
      branchHeadEl.innerHTML = `<a href="https://github.com/${encodeURIComponent(data.repo)}/commit/${encodeURIComponent(data.branchHead)}" target="_blank" rel="noopener" class="truncate" data-full-text="${escapeHtml(data.branchHead)}">${escapeHtml(data.branchHead)}</a>`;
    }

    async function verify({ commit, repo, branch }) {
      updateStatus("warn", "Verifying commit…", `Fetching metadata for ${commit} in ${repo}.`);
      detailsSection.hidden = true;

      const headers = { "Accept": "application/vnd.github+json" };

      const commitResp = await fetch(`https://api.github.com/repos/${repo}/commits/${commit}`, { headers });
      if (commitResp.status === 404) {
        updateStatus("err", "Commit not found", `Commit ${commit} is not present in ${repo}.`);
        return;
      }
      if (!commitResp.ok) {
        updateStatus("err", "GitHub API error", `Received status ${commitResp.status}. Try again later.`);
        return;
      }
      const commitData = await commitResp.json();

      const branchResp = await fetch(`https://api.github.com/repos/${repo}/branches/${branch}`, { headers });
      if (branchResp.status === 404) {
        updateStatus("err", "Branch not found", `Branch ${branch} does not exist in ${repo}.`);
        return;
      }
      if (!branchResp.ok) {
        updateStatus("err", "GitHub API error", `Received status ${branchResp.status} while fetching branch information.`);
        return;
      }
      const branchData = await branchResp.json();
      const headSha = branchData.commit?.sha;

      const compareUrl = `https://api.github.com/repos/${repo}/compare/${commit}...${branch}`;
      const compareResp = await fetch(compareUrl, { headers });
      let compareData = null;
      if (compareResp.ok) {
        compareData = await compareResp.json();
      }

      const authorName = commitData.commit?.author?.name ?? "Unknown";
      const authorEmail = commitData.commit?.author?.email ?? "\u2014";
      const authorDate = commitData.commit?.author?.date ?? commitData.commit?.committer?.date ?? "";
      showDetails({
        sha: commitData.sha,
        author: authorName,
        email: authorEmail,
        date: authorDate,
        repo,
        branchHead: headSha ?? "Unknown",
      });

      if (commitData.sha === headSha) {
        updateStatus("ok", "Document up to date, commit matches branch head", `${commitData.sha} is the current tip of ${branch}.`);
        return;
      }

      if (compareData && compareData.status === "behind") {
        updateStatus(
          "warn",
          "Outdated, commit is behind branch head",
          `${branch} is ${compareData.behind_by} commits ahead of ${commitData.sha}.`
        );
        return;
      }

      if (compareData && compareData.status === "ahead") {
        updateStatus(
          "warn",
          "Commit is ahead of branch head",
          `${commitData.sha} is ${compareData.ahead_by} commits ahead of ${branch}.`
        );
        return;
      }

      updateStatus(
        "warn",
        "Commit differs from branch head",
        `${commitData.sha} does not match ${branch}. Verify the branch or repository parameters.`
      );
    }

    function parseQuery() {
      const params = new URLSearchParams(window.location.search);
      return {
        commit: params.get("commit")?.trim(),
        repo: params.get("repo")?.trim() || "WyattAu/OmniLaTeX-template",
        branch: params.get("branch")?.trim() || "main",
        project: params.get("project")?.trim(),
      };
    }

    function applyProjectLabel(project) {
      if (!project) {
        return;
      }
      const safeProject = escapeHtml(project);
      pageTitleEl.textContent = `${safeProject} PDF Verification`;
      headingEl.textContent = `Verify ${safeProject} Build Provenance`;
      introTextEl.innerHTML = `This tool confirms whether the PDF you are reading was generated from the latest commit of the <strong>${safeProject}</strong> repository. Pass the commit hash (embedded in the PDF) through the <code>?commit=&lt;sha&gt;</code> query parameter—links inside the template do this automatically.`;
    }

    async function bootstrap() {
      const query = parseQuery();
      form.elements.commit.value = query.commit ?? "";
      form.elements.repo.value = query.repo;
      form.elements.branch.value = query.branch;
      applyProjectLabel(query.project || query.repo?.split("/")?.[1] || "OmniLaTeX");

      if (query.commit) {
        try {
          await verify(query);
        } catch (err) {
          console.error(err);
          updateStatus("err", "Unexpected error", err.message ?? "Unknown error");
        }
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const commit = formData.get("commit").trim();
      const repo = formData.get("repo").trim();
      const branch = formData.get("branch").trim();

      if (!commit) {
        updateStatus("warn", "Commit hash required", "Provide a commit hash to perform verification.");
        return;
      }

      const url = new URL(window.location.href);
      url.searchParams.set("commit", commit);
      url.searchParams.set("repo", repo);
      url.searchParams.set("branch", branch);
      history.replaceState(null, "", url.toString());

      try {
        await verify({ commit, repo, branch });
      } catch (err) {
        console.error(err);
        updateStatus("err", "Unexpected error", err.message ?? "Unknown error");
      }
    });

    bootstrap();
