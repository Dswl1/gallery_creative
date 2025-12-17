document.addEventListener('DOMContentLoaded', function () {

  const tableEl = document.getElementById('dataTables');
  if (!tableEl) return;

  if ($.fn.DataTable.isDataTable(tableEl)) return;

  const dt = $('#dataTables').DataTable({
    responsive: true,
    scrollX: true,
    autoWidth: false, // 🔥 KUNCI UTAMA

    pageLength: 10,
    lengthMenu: [5, 10, 25, 50],

    order: [[1, 'asc']],
    columnDefs: [
      { orderable: false, targets: [0, -1] }
    ],

    dom:
      '<"flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-3"lf>' +
      'rt' +
      '<"flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mt-4"ip>',

    language: {
      search: "",
      searchPlaceholder: "Cari data...",
      lengthMenu: "_MENU_ entries",
      info: "Menampilkan _START_–_END_ dari _TOTAL_ data",
      paginate: {
        previous: "‹",
        next: "›"
      }
    }
  });

  // 🔒 FIX WIDTH PAS SORT / PAGINATION
  dt.on('order.dt draw.dt', function () {
    dt.columns.adjust();
  });

});
