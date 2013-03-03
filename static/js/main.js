$(function () {
	$('#simple-questions').on('click', function (event) {
		event.preventDefault();
		$('.the-feed').slideUp();
		$('.comment-simple').slideDown();
		$('.comment-complex').slideUp();
	});
	$('#comment-simple-close').on('click', function (event) {
		event.preventDefault();
		$('.the-feed').slideDown();
		$('.comment-simple').slideUp();
		$('.comment-complex').slideUp();
	});
	$('#comment-simple-other').on('click', function (event) {
		event.preventDefault();
		$('.the-feed').slideUp();
		$('.comment-simple').slideUp();
		$('.comment-complex').slideDown();
	});
	$('#comment-complex-submit').on('click', function (event) {
		event.preventDefault();
		var now = new Date();

		$('.the-feed h2').after(
			'<div>'
				+ '<a href="#">+</a>'
				+ '<h3>' + $('#comment-complex-textarea').val() + '</h3>'
				+ '<p class="timestamp">' + (now.getHours() % 12) + ':' + now.getMinutes() + '</p>'
			+ '</div>'
		);

		$('.the-feed').slideDown();
		$('.comment-simple').slideUp();
		$('.comment-complex').slideUp();
	});
});
