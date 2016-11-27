//footer fix
function refitFooter() {
	if ($('body').height() < $(window).height() ) {
		$('footer').css({'position': 'absolute'});
	} else {
		$('footer').css({'position': 'relative'});
	}

	$('footer').show();
}

$(window).resize(function() { refitFooter(); });


