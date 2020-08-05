const listID = $('#addButton').val()

$('#listName').keyup(function(){
    if($(this).val() != ''){
        $('#listNameButton').prop('disabled', false)
    } else {
        $('#listNameButton').prop('disabled', true)
    }
})

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

$('#listNameButton').click(function(){
    $.ajax({
        type: "POST",
        url: '/lists/edit/name',
        async: true,
        data: {name: $('#listName').val(), listID: listID},
        success: function(res){
                $('#flash').html(flashMessage(res))
        }
    })
})

$('#addButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/lists/edit/add',
        async: true,
        data: {listID: listID, name: $('#name').val(), quantity: +$('#quantity').val()},
        success: function(res){
            if(res.status != 200){
                $('#flash').html(flashMessage(res))
            }else{
                location.reload()
            }
        }
    })
})

$('#recipeNameButton').click(function(){
    //recipe names are guaranteed to be unique
    $.ajax({
        type: 'POST',
        url: '/lists/edit/add/recipes',
        async: true,
        data: {listID: listID, recipeName: $('#recipeName').val()},
        success: function(res){
            if(res.status == 200){
                location.reload()
            }else{
                $('#flash').html(flashMessage(res))
            }
            
        }
    })
})

$('.ingredientQuantity').change(function(){
    $(`#${$(this).attr('id').substr(3)}`).prop('disabled', false)
})

$('.removeButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/lists/edit/remove',
        async: true,
        data: {listID: listID, ingredientID: $(this).val()},
        success: function(res){
            if(res.status != 200){
                $('#flash').html(flashMessage(res))
            }else{
                location.reload()
            }
        }
    })
})

$('.changeQuantityButton').click(function(){
    $.ajax({
        type: 'POST',
        url: '/lists/edit/quantity',
        async: true,
        data: {listID: listID, ingredientID: $(this).attr('id'), quantity: $(`#num${$(this).attr('id')}`).val()},
        success: function(res){
            $('#flash').html(flashMessage(res))
        }
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