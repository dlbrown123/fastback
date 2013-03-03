$(function () {
	$('#simple-questions').on('click', function (event) {
		event.preventDefault();
		$('.the-feed').slideUp();
		$('.comment-simple').slideDown();
		$('.comment-complex').slideUp();
	});
	$('#comment-simple-close, #comment-complex-close').on('click', function (event) {
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
	$('.main-message-buttons a').on('click', function (event) {
		var el = $(event.currentTarget),
			enableButton;
		event.preventDefault();

		// prevent click spamming
		if (el.hasClass('clicked')) {
			return false;
		}

		enableButton = function () {
			this.removeClass('clicked');
		};

		postQuestion(el.data('content'));
		el.addClass('clicked');
		setTimeout($.proxy(enableButton, el), 3000);
	});
	$('.the-feed').on('click', 'a.agree', function (event) {
		var el = $(event.currentTarget),
			parent = el.parent();
		event.preventDefault();
		$.post(el.attr('href'), {like: true});
		parent.addClass('i-agree');
		parent.find('.likes').text(Number(parent.find('.likes').text()) + 1);
		el.remove();
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

	var triggerUpdate, updateFeed, postQuestion,
		getSessions, showSesssions;

	postQuestion = function (content) {
		var now = new Date();

		$.post('/feed', {
				content: content,
				user: $('#user').val(),
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
			$.getJSON('/feed', {session: $('#session-id').val(), limit: 10}, $.proxy(updateFeed, $(element)))
				.complete(function () {triggerUpdate(0, element);});
		}, 2000, element);
	};

	updateFeed = function (data) {
		var el, i, ts,
			now = new Date(),
			template = _.template($('#feed-item-template').html());

		for (i in data) {
			el = this.find('.feed-item[rel="' + data[i]['id'] + '"]');
			if (el.length > 0) continue;
			ts = new Date(now.toDateString() + ' ' + data[i]['timestamp'] + ' UTC');
			data[i]['timestamp'] = ts.toLocaleTimeString();
			el = template({obj: data[i]});
			this.find('h2').after(el);
		}

		this.find('.feed-item').slideDown();
		this.find('.feed-item:nth-child(n+13)').remove();
	};

	getSessions = function (index, element) {
		$.getJSON('/session', $.proxy(showSessions, $(element)));
	};

	showSessions = function (data) {
		var el, i,
			template = _.template($('#session-item-template').html());

		for (i in data) {
			el = template({obj: data[i]});
			this.append(el);
		}
	};

	$('.the-feed').each(triggerUpdate);
	$('.available-sessions').each(getSessions);
});
