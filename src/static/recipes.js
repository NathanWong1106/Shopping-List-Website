//sends an asychronous ajax request to the recipe create route in app.py
function createNewRecipe(name, description)
{
    var ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/create',
        async: true,
        data: {name: name, description: description},
        success: function(res){
            if(res.status == 406){
                $('#flash').html(flashMessage(res))
            }
            else if (res.status == 200){
                location.reload()
            }
        }  
    })
}
function deleteRecipe(recipeID)
{
    var ajaxReq = $.ajax({
        type:'POST',
        url: '/recipes/delete',
        async: true,
        data: {id:recipeID}
    })
    .done(function(){
        location.reload()
    })
}
$('#createButton').click(function(){
    createNewRecipe($('#name').val(), $('#description').val())
})
$('.deleteButton').click(function(){
    deleteRecipe($(this).val())
})
$('#name').keyup(function(){
    if($(this).val() != '' && $('#description').val() != '')
    {
        $('#createButton').prop('disabled', false)
    }else{
        $('#createButton').prop('disabled', true)
    }
})
$('#description').keyup(function(){
    if($(this).val() != '' && $('#name').val() != '')
    {
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