(function () {
  const modal = document.getElementById("gallery-member-modal");
  if (!modal) return;

  const modalImg = document.getElementById("gallery-member-modal-img");
  const modalTitle = document.getElementById("gallery-member-modal-title");
  const modalText = document.getElementById("gallery-member-modal-text");
  const backdrop = modal.querySelector(".gallery-member-modal-backdrop");
  const closeBtn = modal.querySelector(".gallery-member-modal-close");
  let lastFocus = null;

  function readPayload(el) {
    return {
      img: el.getAttribute("data-img") || "",
      title: el.getAttribute("data-title") || "",
      body: el.getAttribute("data-body") || "",
    };
  }

  function openModal(payload) {
    const titleText = payload.title || "";
    const bodyText = payload.body || "";
    const imgSrc = payload.img || "";

    modalImg.src = imgSrc;
    modalImg.alt = titleText;
    modalTitle.textContent = titleText;

    if (bodyText && bodyText !== titleText) {
      modalText.textContent = bodyText;
      modalText.hidden = false;
    } else {
      modalText.textContent = "";
      modalText.hidden = true;
    }

    lastFocus = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("gallery-member-modal-open");
    closeBtn.focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("gallery-member-modal-open");
    modalImg.removeAttribute("src");
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  function bindOpen(el) {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      openModal(readPayload(el));
    });
  }

  document.querySelectorAll(".gallery-member-thumb-btn, .gallery-member-more").forEach(bindOpen);

  document.querySelectorAll(".gallery-member-card").forEach((card) => {
    const titleEl = card.querySelector(".gallery-member-title");
    const caption = card.querySelector(".gallery-member-caption");
    const thumb = card.querySelector(".gallery-member-thumb-btn");
    if (!titleEl || !caption || !thumb || caption.querySelector(".gallery-member-more")) return;

    if (titleEl.scrollHeight <= titleEl.clientHeight + 2) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "gallery-member-more";
    btn.textContent = "عرض المزيد";
    btn.setAttribute("data-img", thumb.getAttribute("data-img") || "");
    btn.setAttribute("data-title", thumb.getAttribute("data-title") || "");
    btn.setAttribute("data-body", thumb.getAttribute("data-body") || "");
    caption.appendChild(btn);
    bindOpen(btn);
  });

  backdrop.addEventListener("click", closeModal);
  closeBtn.addEventListener("click", closeModal);

  document.addEventListener("keydown", (e) => {
    if (!modal.hidden && e.key === "Escape") closeModal();
  });
})();
