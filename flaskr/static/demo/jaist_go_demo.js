let allPosts = [];
let activeFilter = "all";

const board = document.querySelector("#postList");
const detail = document.querySelector("#postDetail");
const searchInput = document.querySelector("#searchInput");
const filterButtons = document.querySelectorAll("[data-filter]");
const activeCount = document.querySelector("#activeCount");
const resultLabel = document.querySelector("#resultLabel");
const composeDialog = document.querySelector("#composeDialog");
const composeForm = document.querySelector("#composeForm");
const composeError = document.querySelector("#composeError");

function postUrl(id) {
    return `/posts/${id}`;
}

function esc(str) {
    const div = document.createElement("div");
    div.textContent = String(str ?? "");
    return div.innerHTML;
}

function tagClass(tag) {
    if (tag.includes("車")) return "ride";
    if (tag.includes("今日") || tag.includes("明朝") || tag === "急ぎ") return "urgent";
    return "";
}

function matchesFilter(post) {
    if (activeFilter === "all") return true;
    return post.category === activeFilter;
}

function matchesSearch(post) {
    const query = (searchInput?.value || "").trim().toLowerCase();
    if (!query) return true;
    return [
        post.title,
        post.destination,
        post.meeting,
        post.contact,
        post.summary,
        ...post.tags
    ].join(" ").toLowerCase().includes(query);
}

function renderBoard() {
    if (!board) return;

    const visiblePosts = allPosts.filter((post) => matchesFilter(post) && matchesSearch(post));
    if (activeCount) activeCount.textContent = allPosts.length;
    if (resultLabel) resultLabel.textContent = `${visiblePosts.length}件を表示`;

    if (visiblePosts.length === 0) {
        board.innerHTML = `<div class="empty-state">条件に合う募集がありません。検索語を変えてみてください。</div>`;
        return;
    }

    board.innerHTML = visiblePosts.map((post) => `
        <article class="post-card">
            <div>
                <div class="tag-row">
                    ${post.tags.map((tag) => `<span class="tag ${tagClass(tag)}">${esc(tag)}</span>`).join("")}
                    <span class="status-pill">${esc(post.status)}</span>
                </div>
                <h3>${esc(post.title)}</h3>
                <p>${esc(post.summary)}</p>
                <div class="meta-row">
                    <span>${esc(post.time)}</span>
                    <span>${esc(post.destination)}</span>
                    <span>${esc(post.people)}</span>
                </div>
            </div>
            <a class="post-action" href="${postUrl(post.id)}">詳細を見る</a>
        </article>
    `).join("");
}

async function loadAndRenderBoard() {
    if (!board) return;
    if (resultLabel) resultLabel.textContent = "読み込み中…";
    try {
        const res = await fetch("/api/posts");
        if (res.status === 401) { window.location.href = "/login"; return; }
        allPosts = await res.json();
        renderBoard();
    } catch {
        board.innerHTML = `<div class="empty-state">データの読み込みに失敗しました。</div>`;
        if (resultLabel) resultLabel.textContent = "エラー";
    }
}

async function loadAndRenderDetail() {
    if (!detail) return;

    const postId = Number(document.body.dataset.postId);
    try {
        const res = await fetch(`/api/posts/${postId}`);
        if (res.status === 401) { window.location.href = "/login"; return; }
        if (!res.ok) {
            detail.innerHTML = `
                <section class="empty-state">
                    <h1>募集が見つかりません</h1>
                    <p>削除されたか、存在しない募集です。</p>
                    <a class="post-action" href="/">掲示板へ戻る</a>
                </section>
            `;
            return;
        }
        const post = await res.json();

        const deleteButton = post.is_owner
            ? `<button class="ghost-button" type="button" onclick="deletePost(${post.id})">この募集を削除</button>`
            : "";

        const hasRoute = post.map_id && post.dest_latitude != null && post.dest_longitude != null;
        const mapSrc = hasRoute
            ? `/map/${post.map_id}?dest_lat=${post.dest_latitude}&dest_lng=${post.dest_longitude}`
            : post.map_id ? `/map/${post.map_id}` : null;
        const mapSection = mapSrc
            ? `<iframe src="${mapSrc}" class="detail-map-iframe" title="集合場所の地図" loading="lazy"></iframe>`
            : `<div class="detail-map" aria-label="集合場所から目的地までのイメージ">
                    <span class="pin">集合</span>
                    <span class="pin destination">目的地</span>
                </div>`;

        detail.innerHTML = `
            <section class="detail-main">
                <div class="tag-row">
                    ${post.tags.map((tag) => `<span class="tag ${tagClass(tag)}">${esc(tag)}</span>`).join("")}
                    <span class="status-pill">${esc(post.status)}</span>
                </div>
                <h1>${esc(post.title)}</h1>
                <p class="detail-lead">${esc(post.summary)}</p>
                ${mapSection}
                <div class="info-list">
                    <div class="info-item"><span>出発予定</span><strong>${esc(post.time)}</strong></div>
                    <div class="info-item"><span>集合場所</span><strong>${esc(post.meeting)}</strong></div>
                    <div class="info-item"><span>目的地</span><strong>${esc(post.destination)}</strong></div>
                    <div class="info-item"><span>人数</span><strong>${esc(post.people)}</strong></div>
                    <div class="info-item"><span>費用</span><strong>${esc(post.cost)}</strong></div>
                    <div class="info-item"><span>投稿者</span><strong>${esc(post.owner)}</strong></div>
                </div>
                <p class="detail-copy">${esc(post.detail)}</p>
            </section>
            <aside class="detail-side">
                <div class="contact-box">
                    <h2>連絡先</h2>
                    <p>参加したい、車を出せる、条件を相談したい場合はこの連絡先へ。</p>
                    <div class="contact-value">${esc(post.contact)}</div>
                </div>
                <div class="side-actions">
                    <button class="primary-button wide" type="button" data-toast="連絡先をコピーした想定です">連絡先をコピー</button>
                    <button class="ghost-button" type="button" data-toast="この募集を保存した想定です">保存する</button>
                    ${deleteButton}
                    <a class="post-action" href="/">一覧へ戻る</a>
                </div>
            </aside>
        `;
    } catch {
        detail.innerHTML = `<section class="empty-state"><p>データの読み込みに失敗しました。</p></section>`;
    }
}

async function deletePost(postId) {
    if (!confirm("この募集を削除しますか？")) return;
    try {
        const res = await fetch(`/api/posts/${postId}`, { method: "DELETE" });
        if (res.ok) {
            showToast("削除しました");
            setTimeout(() => { window.location.href = "/"; }, 1200);
        } else {
            showToast("削除に失敗しました");
        }
    } catch {
        showToast("削除に失敗しました");
    }
}

function showToast(message) {
    const oldToast = document.querySelector(".toast");
    oldToast?.remove();

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2200);
}

filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
        activeFilter = button.dataset.filter;
        filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));
        renderBoard();
    });
});

searchInput?.addEventListener("input", renderBoard);

document.querySelectorAll("[data-open-compose]").forEach((button) => {
    button.addEventListener("click", () => composeDialog?.showModal());
});

document.querySelector("#closeCompose")?.addEventListener("click", () => {
    composeDialog?.close();
});

composeForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (composeError) composeError.hidden = true;

    const data = {
        title: composeForm.querySelector("[name=title]").value.trim(),
        category: composeForm.querySelector("[name=category]").value,
        destination: composeForm.querySelector("[name=destination]").value.trim(),
        time: composeForm.querySelector("[name=time]").value.trim(),
        meeting: composeForm.querySelector("[name=meeting]").value.trim(),
        people: composeForm.querySelector("[name=people]").value.trim(),
        contact: composeForm.querySelector("[name=contact]").value.trim(),
        cost: composeForm.querySelector("[name=cost]").value.trim(),
        detail: composeForm.querySelector("[name=detail]").value.trim(),
        place_name: composeForm.querySelector("[name=meeting]").value.trim(),
        latitude: parseFloat(composeForm.querySelector("[name=latitude]").value),
        longitude: parseFloat(composeForm.querySelector("[name=longitude]").value),
        dest_latitude: parseFloat(composeForm.querySelector("[name=dest_latitude]").value),
        dest_longitude: parseFloat(composeForm.querySelector("[name=dest_longitude]").value),
    };

    try {
        const res = await fetch("/api/posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (res.ok) {
            composeDialog.close();
            composeForm.reset();
            await loadAndRenderBoard();
            showToast("募集を投稿しました");
        } else {
            const errorData = await res.json();
            if (composeError) {
                composeError.textContent = errorData.error || "投稿に失敗しました";
                composeError.hidden = false;
            }
        }
    } catch {
        if (composeError) {
            composeError.textContent = "投稿に失敗しました";
            composeError.hidden = false;
        }
    }
});

document.addEventListener("click", (event) => {
    const toastButton = event.target.closest("[data-toast]");
    if (toastButton) {
        showToast(toastButton.dataset.toast);
    }
});

loadAndRenderBoard();
loadAndRenderDetail();
