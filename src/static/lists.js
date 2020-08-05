$('#createButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/lists/create',
        async: true,
        data: {name: $('#name').val()},
        success: function(res){
            if(res.status == 200){
                location.reload()
            } else {
                $('#flash').html(flashMessage(res))
            }
        }  
    })
})

$('.deleteButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/lists/delete',
        async: true,
        data: {id: $(this).val()}  
    })
    .done(function(){
        location.reload()
    })
})

$('#name').keyup(function(){
    if($(this).val() != ''){
        $('#createButton').prop('disabled', false)
    }else{
        $('#createButton').prop('disabled', true)
    }
})

var flashMessage = function(data){
    var html = ""
    if(data.status == 200){
        html = `<div class="alert alert-primary alert-dismissible fade show msg border text-center rounded-0 " 
                role="alert" style="margin:0;">${data.message}<button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span></button></div></button></div>`
    } else {
        html = `<div class="alert alert-warning alert-dismissible fade show msg border text-center rounded-0 " 
                role="alert" style="margin:0;">${data.message}<button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span></button></div></button></div>`
    }
    return html
};