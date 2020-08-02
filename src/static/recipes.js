//sends an asychronous ajax request to the recipe create route in app.py
function createNewRecipe(name, description)
{
    var ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/create',
        async: true,
        data: {name: name, description: description}  
    })
    .done(function(){
        location.reload()
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