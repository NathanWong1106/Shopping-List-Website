function isInteger(event){
    //returns null if the backspace, space, or delete is pressed // only returns [0-9] through charcodes
    return (event.charCode == 8 || event.charCode == 0 || event.charCode == 13) ? null : event.charCode >= 48 && event.charCode <= 57
}