const posts = [
    {
        id: 1,
        title: "今夜、辰口温泉に行ける人募集",
        category: "ride",
        tags: ["車募集", "今日", "温泉"],
        status: "車あり歓迎",
        destination: "辰口温泉",
        time: "今日 20:00 出発",
        meeting: "JAIST正面玄関",
        people: "2人募集中",
        contact: "LINE: jaist-onsen-demo",
        owner: "M1 情報科学系",
        cost: "ガソリン代を割り勘",
        summary: "授業後に温泉へ行きたいです。車を出せる方、または同乗したい方がいたら連絡ください。",
        detail: "帰りは22:30ごろJAIST着の予定です。車を出してくれる人には駐車場代とガソリン代を相談して支払います。"
    },
    {
        id: 2,
        title: "イオンモール白山で買い物したい",
        category: "ride",
        tags: ["車募集", "買い物", "週末"],
        status: "あと3人",
        destination: "イオンモール白山",
        time: "土曜 13:00 出発",
        meeting: "学生寄宿舎前",
        people: "3人募集中",
        contact: "X: @jaist_shop_demo",
        owner: "D1 マテリアル系",
        cost: "交通費相談",
        summary: "生活用品をまとめて買いに行きたいです。荷物が多くなりそうなので車がある方を探しています。",
        detail: "現地滞在は2時間くらいを想定しています。途中参加でも大丈夫です。"
    },
    {
        id: 3,
        title: "金沢駅まで送ってくれる人いませんか",
        category: "soon",
        tags: ["車募集", "明朝", "駅"],
        status: "急ぎ",
        destination: "金沢駅",
        time: "明日 7:30 出発",
        meeting: "JAISTバス停",
        people: "1人",
        contact: "mail: go-demo@example.com",
        owner: "M2 知識科学系",
        cost: "謝礼あり",
        summary: "早朝の電車に乗りたいので、金沢駅まで移動できる手段を探しています。",
        detail: "大きめのスーツケースが1つあります。時間が合う方がいたら連絡ください。"
    },
    {
        id: 4,
        title: "手取フィッシュランドに遊びに行く会",
        category: "event",
        tags: ["遊び", "車あり", "日曜"],
        status: "同乗可",
        destination: "手取フィッシュランド",
        time: "日曜 11:00 出発",
        meeting: "JAIST正面玄関",
        people: "あと2人",
        contact: "Discord: jaist-go-demo",
        owner: "B4 先端科学技術",
        cost: "各自精算",
        summary: "車を出せます。週末に軽く遊びに行きたい人を募集しています。",
        detail: "雨の場合は行き先を室内施設に変更します。初対面でも歓迎です。"
    },
    {
        id: 5,
        title: "夜ごはん、野々市方面に行きませんか",
        category: "event",
        tags: ["遊び", "ごはん", "車相談"],
        status: "相談中",
        destination: "野々市周辺",
        time: "金曜 18:40 出発",
        meeting: "研究棟前",
        people: "4人まで",
        contact: "LINE: jaist-dinner-demo",
        owner: "M1 融合科学系",
        cost: "食事代のみ",
        summary: "研究終わりに外でごはんを食べたいです。車を出せる人がいれば場所を相談したいです。",
        detail: "候補はラーメン、カレー、回転寿司あたりです。参加者で決めます。"
    }
];

const board = document.querySelector("#postList");
const detail = document.querySelector("#postDetail");
const searchInput = document.querySelector("#searchInput");
const filterButtons = document.querySelectorAll("[data-filter]");
const activeCount = document.querySelector("#activeCount");
const resultLabel = document.querySelector("#resultLabel");
const composeDialog = document.querySelector("#composeDialog");

let activeFilter = "all";

function postUrl(id) {
    return `/demo/posts/${id}`;
}

function tagClass(tag) {
    if (tag.includes("車")) return "ride";
    if (tag.includes("今日") || tag.includes("明朝")) return "urgent";
    return "";
}

function matchesFilter(post) {
    if (activeFilter === "all") return true;
    if (activeFilter === "soon") return post.category === "soon" || post.tags.some((tag) => ["今日", "明朝"].includes(tag));
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

    const visiblePosts = posts.filter((post) => matchesFilter(post) && matchesSearch(post));
    activeCount.textContent = posts.length;
    resultLabel.textContent = `${visiblePosts.length}件を表示`;

    if (visiblePosts.length === 0) {
        board.innerHTML = `<div class="empty-state">条件に合う募集がありません。検索語を変えてみてください。</div>`;
        return;
    }

    board.innerHTML = visiblePosts.map((post) => `
        <article class="post-card">
            <div>
                <div class="tag-row">
                    ${post.tags.map((tag) => `<span class="tag ${tagClass(tag)}">${tag}</span>`).join("")}
                    <span class="status-pill">${post.status}</span>
                </div>
                <h3>${post.title}</h3>
                <p>${post.summary}</p>
                <div class="meta-row">
                    <span>${post.time}</span>
                    <span>${post.destination}</span>
                    <span>${post.people}</span>
                </div>
            </div>
            <a class="post-action" href="${postUrl(post.id)}">詳細を見る</a>
        </article>
    `).join("");
}

function renderDetail() {
    if (!detail) return;

    const postId = Number(document.body.dataset.postId);
    const post = posts.find((item) => item.id === postId);

    if (!post) {
        detail.innerHTML = `
            <section class="empty-state">
                <h1>募集が見つかりません</h1>
                <p>デモ用データに存在しない募集です。</p>
                <a class="post-action" href="/demo/board">掲示板へ戻る</a>
            </section>
        `;
        return;
    }

    detail.innerHTML = `
        <section class="detail-main">
            <div class="tag-row">
                ${post.tags.map((tag) => `<span class="tag ${tagClass(tag)}">${tag}</span>`).join("")}
                <span class="status-pill">${post.status}</span>
            </div>
            <h1>${post.title}</h1>
            <p class="detail-lead">${post.summary}</p>
            <div class="detail-map" aria-label="集合場所から目的地までのイメージ">
                <span class="pin">集合</span>
                <span class="pin destination">目的地</span>
            </div>
            <div class="info-list">
                <div class="info-item"><span>出発予定</span><strong>${post.time}</strong></div>
                <div class="info-item"><span>集合場所</span><strong>${post.meeting}</strong></div>
                <div class="info-item"><span>目的地</span><strong>${post.destination}</strong></div>
                <div class="info-item"><span>人数</span><strong>${post.people}</strong></div>
                <div class="info-item"><span>費用</span><strong>${post.cost}</strong></div>
                <div class="info-item"><span>投稿者</span><strong>${post.owner}</strong></div>
            </div>
            <p class="detail-copy">${post.detail}</p>
        </section>
        <aside class="detail-side">
            <div class="contact-box">
                <h2>連絡先</h2>
                <p>参加したい、車を出せる、条件を相談したい場合はこの連絡先へ。</p>
                <div class="contact-value">${post.contact}</div>
            </div>
            <div class="side-actions">
                <button class="primary-button wide" type="button" data-toast="連絡先をコピーした想定です">連絡先をコピー</button>
                <button class="ghost-button" type="button" data-toast="この募集を保存した想定です">保存する</button>
                <a class="post-action" href="/demo/board">一覧へ戻る</a>
            </div>
        </aside>
    `;
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
    button.addEventListener("click", () => {
        if (composeDialog?.showModal) {
            composeDialog.showModal();
        }
    });
});

document.addEventListener("click", (event) => {
    const toastButton = event.target.closest("[data-toast]");
    if (toastButton) {
        showToast(toastButton.dataset.toast);
    }
});

renderBoard();
renderDetail();
