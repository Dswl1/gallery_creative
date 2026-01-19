document.addEventListener("DOMContentLoaded", () => {

  /* ===== NAVBAR SCROLL ===== */
  const nav = document.getElementById("navbar");
  if (nav) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 20) {
        nav.classList.add("bg-white/20", "backdrop-blur-lg", "shadow");
        nav.classList.remove("bg-white/90");
      } else {
        nav.classList.add("bg-white/90");
        nav.classList.remove("bg-white/20", "backdrop-blur-lg");
      }
    });
  }

  /* =========================
     IMAGE ZOOM MODAL
  ========================= */
  const zoomButtons = document.querySelectorAll(".zoom-btn");
  const modal = document.getElementById("imgModal");
  const modalImg = document.getElementById("modalImg");

  if (zoomButtons.length && modal && modalImg) {
    zoomButtons.forEach(btn => {
      btn.addEventListener("click", e => {
        e.preventDefault();
        e.stopPropagation();

        const imgSrc = btn.dataset.img;
        if (!imgSrc) return;

        modalImg.src = imgSrc;
        modal.classList.remove("hidden");
        modal.classList.add("flex");
      });
    });

    modal.addEventListener("click", e => {
      if (e.target === modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        modalImg.src = "";
      }
    });
  }

});


function confirmDelete(el) {
  const id = el.dataset.id;

  Swal.fire({
    title: "Yakin hapus konten?",
    text: "Konten akan dihapus permanen!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonText: "Ya, hapus",
    cancelButtonText: "Batal"
  }).then(function (result) {
    if (result.isConfirmed) {
      document.getElementById("deleteForm-" + id).submit();
    }
  });
}


function saveChange(event) {
  event.preventDefault();

  Swal.fire({
    title: "Apakah anda ingin simpan?",
    showDenyButton: true,
    showCancelButton: true,
    confirmButtonText: "simpan",
    denyButtonText: `jangan simpan`
  }).then((result) => {
    if (result.isConfirmed) {
      event.target.closest("form").submit();
      Swal.fire("Data berhasil disimpan!", "", "berhasil");
    } else if (result.isDenied) {
      Swal.fire("Perubahan tidak tersimpan", "", "info");
    }
  });
}


//MODALIMG
function initImageModal() {
  const modal = document.getElementById('imgModal');
  const modalImg = document.getElementById('modalImg');
  const closeBtn = document.getElementById('closeModalBtn');

  if (!modal || !modalImg || !closeBtn) {
    console.error('Modal elements not found');
    return;
  }

  // OPEN MODAL
  document.querySelectorAll('.zoom-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const imgSrc = this.dataset.img;
      if (!imgSrc) return;

      modalImg.src = imgSrc;
      modal.classList.remove('hidden');
      modal.classList.add('flex');

      requestAnimationFrame(() => {
        modalImg.classList.remove('scale-95');
        modalImg.classList.add('scale-100');
      });
    });
  });

  closeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    closeModal();
  });

  modal.addEventListener('click', function () {
    closeModal();
  });

  modalImg.addEventListener('click', function (e) {
    e.stopPropagation();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
  });

  function closeModal() {
    modalImg.classList.remove('scale-100');
    modalImg.classList.add('scale-95');

    setTimeout(() => {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      modalImg.src = '';
    }, 200);
  }
}
document.addEventListener('DOMContentLoaded', initImageModal);


function previewImage(event) {
  const reader = new FileReader();
  reader.onload = function () {
    document.getElementById('preview').src = reader.result;
  }
  reader.readAsDataURL(event.target.files[0]);
}



let page = 1;
let loading = false;

const grid   = document.getElementById('contentGrid');
const btn    = document.getElementById('loadMore');
const search = document.getElementById('searchInput');
const sort   = document.getElementById('sortSelect');

async function loadContent(reset = false) {
    if (loading) return;
    loading = true;

    if (reset) {
        page = 1;
        grid.innerHTML = '';
        btn.style.display = 'block';
    }

    const q = search.value;
    const s = sort.value;

    const res = await fetch(`/content/load?page=${page}&q=${q}&sort=${s}`);
    const html = await res.text();

    if (html.trim() === '') {
        btn.style.display = 'none';
    } else {
        grid.insertAdjacentHTML('beforeend', html);
        page++;
    }

    loading = false;
}

// LOAD MORE
btn.addEventListener('click', () => loadContent());

// SEARCH (debounce)
let t;
search.addEventListener('input', () => {
    clearTimeout(t);
    t = setTimeout(() => loadContent(true), 400);
});

// SORT
sort.addEventListener('change', () => loadContent(true));
