$(function () {
	$('.create-session').each(function (index, element) {
		var now = new Date;
		$(element).find('#timestamp').val(Math.floor(now.getTime() / 1000));
	});

	$('#start-time-datepicker').datetimepicker({
		pickDate: false,
		pick12HourFormat: true,
		pickSeconds: false
	});
	$('#end-time-datepicker').datetimepicker({
		pickDate: false
	});

	$('.create-session form').on('submit', function (event) {
		var time;

		$(event.currentTarget).find('.btn-primary').button('loading');

		time = new Date($('#start-time').val());
		$('#start-time').val(Math.floor(time.getTime() / 1000));

		time = new Date($('#end-time').val());
		$('#end-time').val(Math.floor(time.getTime() / 1000));
	});

	$('#visualization').each(function (index, element) {
		$.getJSON('/chartData', {session: $('#session-id').val()}, function (data) {
			var i, ts, question,
				chartData = new google.visualization.DataTable(),
				annotatedtimeline;

			chartData.addColumn('datetime', 'Date');
			chartData.addColumn('number', 'Like');
			chartData.addColumn('string', 'question');
			chartData.addColumn('string', 'likes');
			chartData.addColumn('number', 'Huh?');

			for (i in data) {
				ts = new Date(data[i]['timestamp']);
				console.log(data[i]);
				if (data[i]['questions'].length > 0) {
					question = data[i]['questions'][0];
				} else {
					question = null;
				}
				chartData.addRows([
					[ts, data[i]['count_like'], question, '' + data[i]['count_confused'], data[i]['count_confused']]
				]);
			}

			annotatedtimeline = new google.visualization.AnnotatedTimeLine(
				document.getElementById('visualization'));
			annotatedtimeline.draw(chartData, {'displayAnnotations': true, 'displayAnnotationsFilter': true, 'fill':25});
		});
	});
});
