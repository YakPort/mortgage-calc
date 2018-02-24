var ctx = $("#irrChart");
	var irrChart = new Chart(ctx, {
		type: 'line',
		data: {
			labels: [],
			datasets: [{
				label: 'IRR',
				data: [],
				borderColor: 'white',
			}],
		},
		options: {
			legend: {
				display: false,
			},
			title: {
				display: false,
				text: 'Annualized return by year',
				fontColor: 'white',
			},
			scales: {
				yAxes: [{
					scaleLabel: {
						display: true,
						labelString: 'Annualized return',
						fontColor: 'white',
					},
					gridLines: {
						color: 'white',
					},
					ticks: {
						fontColor: 'white',
						callback: function(value, index, values) {
							return value + '%';
						},
					}
				}],
				xAxes: [{
					scaleLabel: {
						display: true,
						labelString: 'Years since purchase',
						fontColor: 'white',
					},
					gridLines: {
						color: 'transparent',
					},
					ticks: {
						fontColor: 'white',
					}
				}],
			},
		},
	});