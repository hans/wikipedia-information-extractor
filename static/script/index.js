$("document").ready(function(){
	$("#form").submit(function(){
		$.ajax({
			url: "/analyze/" + encodeURIComponent($("#term_in").val()) + ".json",
			data : {},
			success: function (data){
				console.log(data);
				$("#terms_list").empty();
				$("#related_list").empty();
				$.each(data.terms, function(i, entry){
					$("#terms_list").append("<div class=\"term\"><b>" + entry.name + ": </b>" + entry.definition + "</div>");
				});
				$.each(data.related, function(i, entry){
					$("#related_list").append("<a href=\"" + entry.url + "\"><div class=\"link\">" + entry.name + "</div></a>");
				});

				if($("#terms_div").height() > $("#related_div").height()){
					$("#related_div").css("height", $("#terms_div").height().toString());
				} else if($("#terms_div").height() < $("#related_div").height()){
					$("#terms_div").css("height", $("#related_div").height().toString());
				}

				$("#terms_div").show();
				$("#related_div").show();
				$("#lower_div").show();
				$("#second_line").show();
			}
		});
		return false;
	});
});
