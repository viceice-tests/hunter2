var height = 420;
var width = 420;

var svg = d3.select('#episode-stats'),
	margin = {top: 20, right: 20, bottom: 100, left: 20},
	width = +svg.attr("width") - margin.left - margin.right,
	height = +svg.attr("height") - margin.top - margin.bottom;

var chart = svg.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var xAxis = chart.append("g")
	.attr("class", "axis axis-x");

function updateStats(force) {
	if (!(force || $('#auto-update').prop('checked'))) {
		return;
	}
	//$('#fill-me-up-you-slut').load('stats_content' + window.location.search);
	$.get('stats_content', {}, function(allData) {
		var data = allData.puzzleCompletion;

		/*
			.attr('height', height)
			.attr('width', barWidth * data.length)
			*/

		var x = d3.scaleBand()
			.rangeRound([0, width]).padding(0.1)
			.domain(data.map(function(d) { return d.puzzle; }));
		var y = d3.scaleLinear()
			.domain([0, 100])
			.range([height, 0]);
		var barWidth = width / data.length;

		var bar = chart.selectAll("g.bar")
			.data(data);

		// clear out old bars
		enterBar = bar.enter()
			.append("g")
			.attr("class", "bar");
		enterBar.append("rect");
		enterBar.append("text");

		updateBar = enterBar.merge(bar);
		updateBar.attr("transform", function(d, i) { return "translate(" + i * barWidth + ",0)"; })
			.select("rect")
			.attr("y", function(d) { return y(d.completion); })
			.attr("height", function(d) { return height - y(d.completion); })
			.attr("width", barWidth - 1);

		updateBar.select("text")
			.attr("y", function(d) { return y(d.completion) + 3; })
			.attr("x", barWidth / 2)
		    .attr("dy", ".75em")
		    .text(function(d) { return d.completion + '%'; });

		bar.exit().remove();

		xAxis.call(d3.axisBottom(x))
			.attr("transform", "translate(0," + height + ")")
			.selectAll("text")
			.attr("transform", "rotate(-20)");
	});

	setTimeout(updateStats, 5000);
}

function updateClicked(ev) {
	if ($(this).prop('checked')) {
		updateStats();
	}
}

$(function () {
	updateStats(true);
	$('#auto-update').click(updateClicked);
});

