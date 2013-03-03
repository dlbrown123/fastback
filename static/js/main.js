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

		postQuestion($('#comment-complex-textarea').val());
	});
	$('.comment-simple .question').on('click', function (event) {
		var el = $(event.currentTarget);
		event.preventDefault();

		postQuestion(el.text());
	});

	var triggerUpdate, updateFeed, postQuestion;

	postQuestion = function (content) {
		var now = new Date();

		$.post('/feed', {
				content: content,
				user: 'anon123',
				session: $('#session-id').val(),
				timestamp: Math.floor(now.getTime() / 1000)
			})
			.success(function () {
				$('.the-feed').slideDown();
				$('.comment-simple').slideUp();
				$('.comment-complex').slideUp();
			});
	};

	triggerUpdate = function (index, element) {
		var tID = window.setTimeout(function (element) {
			$.getJSON('/feed', $.proxy(updateFeed, $(element)))
				.complete(function () {triggerUpdate(0, element);});
		}, 2000, element);
	}

	updateFeed = function (data) {
		var el, i,
			template = _.template($('#feed-item-template').html());

		for (i in data) {
			el = this.find('.feed-item[rel="' + data[i]['id'] + '"]');
			if (el.length > 0) continue;
			el = template({obj: data[i]});
			this.find('h2').after(el);
		}

		this.find('.feed-item').slideDown();
		this.find('.feed-item:nth-child(n+10)').remove();
	};

	$('.the-feed').each(triggerUpdate);
});
