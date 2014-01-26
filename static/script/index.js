$("document").ready(function(){
	var cards = [];
	var cardIndex = 0;
	$("#form").submit(function(){
		$.ajax({
			url: "/analyze/term/" + encodeURIComponent($("#term_in").val()) + ".json",
			data : {},
			success: function (data){
				data.cards = [
								{ question: "First President of thhjghgkjgjgkjghkjjhkghjghjgkghjghjghjghjghjgjgkjhgkjgkjgkjhghje United States",
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

				$("#card_div").css("height", $("#card_div").width()*(1.0/2.0));
				loadCard();
				$("#terms_div").show();
				$("#related_div").show();
				$("#lower_div").show();
				$("#second_line").show();
			}
		});
		return false;
	});

	var loadCard = function(){
		$("#card_question").hide();
		$("#card_answer").hide();
		$("#card_question").empty();
		$("#card_answer").empty();
		$("#card_question").append(cards[cardIndex].question);
		$("#card_answer").append(cards[cardIndex].answer);
		$("#card_question").show();
	}

	var flipCard = function(fnc){
		$("#card_div").animate({
			"width": "0px",
			"background-color":"gray",
			"margin-left":"275px"	
		}, 200, "swing", function(){
			$("#card_div").animate({
				"width": "550px",
				"background-color":"white",
				"margin-left":"0px"	
			}, 200, "swing", fnc);
		});
	}

	$("#left_arrow").click( function(){
		if(cardIndex == 0){
			cardIndex = cards.length - 1;
		} else if (cardIndex > 0){
			cardIndex--;
		}
		loadCard();
	});

	$("#right_arrow").click(function(){
		if(cardIndex == cards.length - 1){
			cardIndex = 0;
		} else if (cardIndex < cards.length - 1){
			cardIndex++;
		}
		loadCard();
	});

	$("#card_div").click(function(){
		if($("#card_question").css("display") == "none"){
			$("#card_answer").fadeOut(200, function(){
				flipCard(function(){
					$("#card_question").fadeIn(200);
				});
			});
		} else {
			$("#card_question").fadeOut(200, function(){
				flipCard(function(){
					$("#card_answer").fadeIn(200);
				});
			});
		}
	});
});