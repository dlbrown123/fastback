$(function () {
	$('.create-session').each(function (index, element) {
		var now = new Date;
		$(element).find('#timestamp').val(Math.floor(now.getTime() / 1000));
	});
});