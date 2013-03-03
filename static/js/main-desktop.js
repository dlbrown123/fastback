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
});
