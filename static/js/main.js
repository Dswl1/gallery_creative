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


// SWEETALERT
function deleteBtn() {
  Swal.fire({
    title: "Are you sure?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Yes, delete it!"
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Deleted!",
        text: "Your file has been deleted.",
        icon: "success"
      });
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
