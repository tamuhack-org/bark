console.log("hello is this working");
$('#screen-selector').on('click', function(event) {
    var button_type = $(event.target).text().toLowerCase();

    console.log(types)
    var button = $(event.target).closest('tr').find("td.email").text();
    console.log("You clicked on:", button);
});