$(function(){
    var url = "http://127.0.0.21:5000/users";


    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            loadUrl: url ,
            insertUrl: url ,
            updateUrl: url ,
            deleteUrl: url ,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),
        editing: {
            allowUpdating: true,
            allowDeleting: true,
            allowAdding: true
        },
        remoteOperations: {
            sorting: true,
            paging: true
        },
        paging: {
            pageSize: 12
        },
        pager: {
            showPageSizeSelector: true,
            allowedPageSizes: [8, 12, 20]
        },
        columns: [{
            dataField: "id",
            dataType: "number",
            allowEditing: false
        }, {
            dataField: "Content"
        }, {
            dataField: "Sent on"
        }, {
            dataField: "User_from_id"
        }, {
            dataField: "User_to_id"
        }, {
            dataField: "User_from"
        }, {
            dataField: "User_to"
        },
         ],
    }).dxDataGrid("instance");
});
