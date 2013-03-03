$(function () {
	$('.create-session').each(function (index, element) {
		var now = new Date;
		$(element).find('#timestamp').val(Math.floor(now.getTime() / 1000));
	});

	$('#start-time-datepicker').each(function (index, element) {
		$(element).datetimepicker({
			pickDate: false,
			pick12HourFormat: true,
			pickSeconds: false
		});
	});
	$('#end-time-datepicker').each(function (index, element) {
		$(element).datetimepicker({
			pickDate: false,
			pick12HourFormat: true,
			pickSeconds: false
		});
	});

	$('.create-session form').on('submit', function (event) {
		var time;

		$(event.currentTarget).find('.btn-primary').button('loading');

		time = new Date($('#start-time').val().replace(/ /, 'T') + '-05:00');
		$('#start-time').val(Math.floor(time.getTime() / 1000));

		time = new Date($('#end-time').val().replace(/ /, 'T') + '-05:00');
		$('#end-time').val(Math.floor(time.getTime() / 1000));
	});

	var queryChart, drawChart;

	queryChart = function () {
		$.getJSON('/chartData', {session: $('#session-id').val()}, drawChart);
	};
		
	drawChart = function (data) {
		var i, ts, question,
			chartData = new google.visualization.DataTable(),
			annotatedtimeline;

		chartData.addColumn('datetime', 'Date');
		chartData.addColumn('number', 'Like');
		chartData.addColumn('number', 'Huh?');
		chartData.addColumn('string', 'question');
		chartData.addColumn('string', 'likes');

		for (i in data) {
			ts = new Date(data[i]['timestamp']);
			if (data[i]['questions'].length === 0) {
				chartData.addRows([
					[ts, data[i]['count_like'], data[i]['count_confused'], null, null]
				]);
			}
			for (j in data[i]['questions']) {
				question = data[i]['questions'][j];
				chartData.addRows([
					[ts, data[i]['count_like'], data[i]['count_confused'], question, String(data[i]['count_confused'])]
				]);
			}
		}

		annotatedtimeline = new google.visualization.AnnotatedTimeLine(
			document.getElementById('visualization'));
		annotatedtimeline.draw(chartData, {'displayAnnotations': true, 'displayAnnotationsFilter': true, 'fill':25});

		setTimeout(queryChart, 5000);
	};

	$('#visualization').each(function (index, element) {
		queryChart();
	});
});
