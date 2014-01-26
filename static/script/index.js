$("document").ready(function(){
	var cards = [
					{ question: "First President of the United States",
					    answer: "George Washington"
					},
					{
					  question: "This man invented the lightbulb",
					    answer: "Thomas Edison"
					},
					{
					  question: "Do you love bacon?",
					    answer: "YES!"
					}
				];
	var cardIndex = 0;
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

				cards = data.cards;

				if($("#terms_div").height() > $("#related_div").height()){
					$("#related_div").css("height", $("#terms_div").height().toString());
				} else if($("#terms_div").height() < $("#related_div").height()){
					$("#terms_div").css("height", $("#related_div").height().toString());
				}

				$("card_div").css("height", $("card_div").width()*(3/4));
				loadCard();
				$("#terms_div").show();
				$("#related_div").show();
				$("#lower_div").show();
				$("#second_line").show();
			}
		});
		return false;
	});

	function loadCard(){
		$("#card_question").hide();
		$("#card_answer").hide();
		$("#card_question").empty();
		$("#card_answer").empty();
		$("#card_question").append(cards[cardIndex].question);
		$("#card_answer").append(cards[cardIndex].answer);
		$("#question").show();
	}

	$("#left_arrow").click( function(){
		if(cardIndex == 0){
			cardIndex = cards.length() - 1;
		} else if (cardIndex > 0){
			cardIndex--;
		}
		loadCard();
	});

	$("#right_arrow").click(function(){
		if(cardIndex == cards.length() - 1){
			cardIndex = 0;
		} else if (cardIndex < cards.length() - 1){
			cardIndex++;
		}
		loadCard();
	});
});
