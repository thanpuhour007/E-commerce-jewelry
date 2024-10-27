// static/js/datatables.js

function initializeDataTable(tableId, ajaxUrl, columns) {
    $('#' + tableId).DataTable({
        "ajax": {
            "url": ajaxUrl, // The URL to fetch data from
            "type": "GET",
            "dataSrc": "data"
        },
        "columns": columns,
        "responsive": true,
        "autoWidth": false,
        "paging": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "language": {
            "search": "Search:",
            "paginate": {
                "first": "First",
                "last": "Last",
                "next": "Next",
                "previous": "Previous"
            }
        }
    });
}
