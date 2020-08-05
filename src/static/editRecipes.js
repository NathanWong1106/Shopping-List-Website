const recipeID = $('#addButton').val()

$('#quantity').change(function(){
    if(Number.isInteger(+$(this).val()) && +$(this).val() > 0  && $(this).val() != '' && $('#name').val() != '')
    {
        $('#addButton').prop('disabled', false)
    }else{
        $('#addButton').prop('disabled', true)
    }
})

$('#name').keyup(function(){
    if(Number.isInteger(+$('#quantity').val()) && +$('#quantity').val() > 0  && $('#quantity').val() != '' && $(this).val() != '')
    {
        $('#addButton').prop('disabled', false)
    }else{
        $('#addButton').prop('disabled', true)
    }
})

$('#addButton').click(function(){
    ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/edit/add',
        async: true,
        data: {recipeID: recipeID, name: $('#name').val(), quantity: +$('#quantity').val()},
        success: function(res){
            if(res.status == 406){
                $('#flash').html(flashMessage(res))
            }
            else if (res.status == 200){
                location.reload()
            }
        }
    })
})

$('#recipeNameButton').click(function(){
    ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/edit/name',
        async: true,
        data: {name: $('#recipeName').val(), recipeID: recipeID},
        success: function(res){
            $('#flash').html(flashMessage(res))

            if(res.status == 200){
                $('#recipeNameButton').prop('disabled', true)
            }
        }
    })
})

$('#recipeDescriptionButton').click(function(){
    ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/edit/description',
        async: true,
        data: {description: $('#recipeDescription').val(), recipeID: recipeID},
        success: function(res){
            $('#flash').html(flashMessage(res))

            if(res.status == 200){
                $('#recipeDescriptionButton').prop('disabled', true)
            }
        }
    })
})

$('#recipeName').keyup(function(){
    if($(this).val() != ''){
        $('#recipeNameButton').prop('disabled', false)
    }else{
        $('#recipeNameButton').prop('disabled', true)
    }
})

$('#recipeDescription').keyup(function(){
    if($(this).val() != ''){
        $('#recipeDescriptionButton').prop('disabled', false)
    }else{
        $('#recipeDescriptionButton').prop('disabled', true)
    }
})

$('.changeQuantityButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/recipes/edit/quantity',
        async: true,
        data: {recipeID: recipeID, ingredientID: $(this).attr('id'), quantity: $(`#num${$(this).attr('id')}`).val()},
        success: function(res){
            $('#flash').html(flashMessage(res))
        }
    })
})

$('.ingredientQuantity').change(function(){
    $(`#${$(this).attr('id').substr(3)}`).prop('disabled', false)
})

$('.removeButton').click(function(){
    ajaxReq = $.ajax({
        type: 'POST',
        url: '/recipes/edit/remove',
        async: true,
        data: {recipeID: recipeID, ingredientID: $(this).val()},
    })
    .done(function(){
        location.reload()
    })
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