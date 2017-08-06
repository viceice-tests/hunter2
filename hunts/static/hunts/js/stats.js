function getStats(force) {
	if (!(force || $('#auto-update').prop('checked'))) {
		return;
	}
	var graphType = $('#type').val();
	drawFunction = {
		"percent-complete": drawCompletion,
		"time-completed": drawTimeCompleted
	}[graphType];
	$.get('stats_content', {}, drawFunction);
	setTimeout(getStats, 5000);
}

function drawCompletion(data) {
	var x = d3.scaleBand()
		.rangeRound([0, width]).padding(0.1)
		.domain(data.puzzleCompletion.map(function(d) { return d.puzzle; }));
	var y = d3.scaleLinear()
		.domain([0, 1])
		.range([height, 0]);
	var barWidth = width / data.puzzleCompletion.length;

	var completion = data.puzzleCompletion.map(
		function (d) { return d.completion.length / data.numTeams; }
	);
	var bar = chart.selectAll("g.bar")
		.data(completion);

	var enterBar = bar.enter()
		.append("g")
		.attr("class", "bar");
	enterBar.append("rect");
	enterBar.append("text");

	updateBar = enterBar.merge(bar);
	updateBar.attr("transform", function(d, i) { return "translate(" + i * barWidth + ",0)"; })
		.select("rect")
		.attr("y", function(d) { return y(d); })
		.attr("height", function(d) { return height - y(d); })
		.attr("width", barWidth - 3);

	var percentFormatter = d3.format(".0%");

	updateBar.select("text")
		.attr("y", function(d) { return y(d) + 3; })
		.attr("x", barWidth / 2)
		.attr("dy", ".75em")
		.text(percentFormatter);

	bar.exit().remove();

	xAxisElt.call(d3.axisBottom(x))
		.attr("transform", "translate(0," + height + ")")
		.selectAll("text")
		.attr("transform", "rotate(-20)");

	var yAxis = d3.axisLeft(y)
		.tickSize(-width)
		.tickPadding(10)
		.tickFormat(percentFormatter);

	yAxisElt.call(yAxis);
}

function drawTimeCompleted(data) {
	var x = d3.scalePoint()
		.range([0, width])
		.padding(0.5)
		.domain(data.puzzleCompletion.map(function(d) { return d.puzzle; }));
	var y = d3.scaleTime()
		.domain([new Date(data.startTime), new Date(data.endTime)])
		.range([0, height]);
	var colWidth = width / data.puzzleCompletion.length;

	var timeCompleted = data.puzzleCompletion.map(
		function (d) { return d.completion }
	);
	var puzzle = chart.selectAll("g.puzzle")
		.data(data.puzzleCompletion)

	puzzle.selectAll("path").remove();

	var enterPuzzle = puzzle.enter()
		.append("g")
		.attr("class", "puzzle");

	var updatePuzzle = enterPuzzle.merge(puzzle)
		.attr("transform", function(d, i) { console.log(d); return "translate(" + x(d.puzzle) + ",0)"; })
	puzzle.exit().remove();

	var cross = d3.symbol().type(d3.symbolCross).size(30);

	updatePuzzle.selectAll("path")
		.data(function(d, i) { return d.completion; })
		.enter()
		.append("path")
		.attr("transform", function(d, i) { return "translate(0," + y(new Date(d.time)) + ") rotate(45)"; })
		.attr("d", cross);

	var xAxis = d3.axisTop(x)
		.tickSize(-height)
		.tickPadding(10);

	xAxisElt.call(xAxis)
		.selectAll("text")
		.attr("transform", "rotate(20)");

	var yAxis = d3.axisLeft(y)
		.tickSize(-width)
		.tickPadding(10);

	yAxisElt.call(yAxis);
}

var chart;

function clearChart() {
	if (chart) {
		chart.selectAll("*").remove();
	}
	var svg = d3.select('#episode-stats')
	var margin = {top: 100, right: 10, bottom: 100, left: 50}
	width = +svg.attr("width") - margin.left - margin.right
	height = +svg.attr("height") - margin.top - margin.bottom

	chart = svg.append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	chart.append("rect")
		.attr("width", width)
		.attr("height", height)
		.attr("class", "chart-background");

	xAxisElt = chart.append("g")
		.attr("class", "axis axis-x");

	yAxisElt = chart.append("g")
		.attr("class", "axis axis-y");
}

function typeChanged(ev) {
	clearChart();
	getStats(true);
}

function updateClicked(ev) {
	if ($(this).prop('checked')) {
		getStats();
	}
}

$(function () {
	clearChart();
	getStats(true);
	$('#type').change(typeChanged);
	$('#auto-update').click(updateClicked);
});

