"use strict";

// Keep the number of entries in here such that it has a large least common multiple with the number of colours.
var symbolsPathList = [
	{path: "M -3,-3 L 3,3 M 3,-3 L -3,3", strokeWidth: 2, fillOpacity: 0}, // X
	{path: "M -3,0 A 3,3 0 1 1 -3,0.0000001Z", strokeWidth: 0, fillOpacity: 1}, // Filled circle
	{path: "M 0,3 L 3,0 L 0,-3 L -3,0Z", strokeWidth: 0, fillOpacity: 1}, // Filled diamond
	{path: "M 0,-4 L 3.4641016,2 L -3.4641016,2Z", strokeWidth: 0, fillOpacity: 1}, // Filled triangle. I used legit trigonometry to get these coordinates.
	{path: "M -3,-3 L -3,3 L 3,3 L 3,-3Z", strokeWidth: 0, fillOpacity: 1}, // Filled square
	{path: "M 0,4 L 3.4641016,-2 L -3.4641016,-2Z", strokeWidth: 0, fillOpacity: 1}, // Filled upside-down triangle
	{path: "M 0,3 L 0,-3 M -3,0 L 3,0", strokeWidth: 2, fillOpacity: 0}, // +
	{path: "M 0,3 L 3,0 L 0,-3 L -3,0Z", strokeWidth: 2, fillOpacity: 0}, // Diamond
	{path: "M 0,-4 L 3.4641016,2 L -3.4641016,2Z", strokeWidth: 2, fillOpacity: 0}, // triangle
	{path: "M -3,-3 L -3,3 L 3,3 L 3,-3Z", strokeWidth: 2, fillOpacity: 0}, // Square
	{path: "M -3,0 A 3,3 0 1 1 -3,0.0000001Z", strokeWidth: 2, fillOpacity: 0}, // O
];

// Fuck JS and its lack of a standard library
var entityMap = {
	'&': '&amp;',
	'<': '&lt;',
	'>': '&gt;',
	'"': '&quot;',
	"'": '&#39;',
	'/': '&#x2F;',
	'`': '&#x60;',
	'=': '&#x3D;',
	' ': '&nbsp;'
};

function escapeHtml (string) {
	return String(string).replace(/[&<>"'`=\/ ]/g, function (s) {
		return entityMap[s];
	});
}

function getStats(force) {
	if (!(force || $('#auto-update').prop('checked'))) {
		return;
	}
	var graphType = $('#type').val();
	var drawFunction = {
		"percent-complete": drawCompletion,
		"time-completed": drawTimeCompleted(false),
		"progress": drawTimeCompleted(true),
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
		.data(data.puzzleCompletion);

	var enterBar = bar.enter()
		.append("g")
		.attr("class", "bar");
	enterBar.append("rect");
	enterBar.append("text");

	var updateBar = enterBar.merge(bar);
	updateBar.attr("transform", function(d, i) { return "translate(" + i * barWidth + ",0)"; })
		.select("rect")
		.attr("y", function(d) { return y(d.completion); })
		.attr("height", function(d) { return height - y(d.completion); })
		.attr("width", barWidth - 3);

	var percentFormatter = d3.format(".0%");

	updateBar.select("text")
		.attr("y", function(d) { return y(d.completion) + 3; })
		.attr("x", barWidth / 2)
		.attr("dy", ".75em")
		.text(function (d) { return percentFormatter(d.completion); });

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

function drawTimeCompleted(lines) {
	return function(data) {
		// Create the X and Y scales
		var x = d3.scalePoint()
			.range([0, width])
			.padding(0.5)
			.domain(data.puzzleCompletion.map(function(d) { return d.puzzle; }));
		var y = d3.scaleTime()
			.domain([new Date(data.startTime), new Date(data.endTime)])
			.range([0, height]);

		// Create scales for the marks on the graph
		var colours = d3.scaleOrdinal(d3.schemeCategory20)
			.domain(data.teams);
		var symbolsList = d3.symbols;
		var symbols = d3.scaleOrdinal()
			.range(symbolsPathList)
			.domain(data.teams);

		var timeCompleted = data.puzzleCompletion.map(
			function (d) { return d.completion }
		);
		// Load data into team groups
		var team = chart.selectAll("g.team")
			.data(data.puzzleProgress)

		// Kill the paths in the updating groups
		team.selectAll("path").remove();

		// Create new groups
		var enterTeam = team.enter()
			.append("g")
			.attr("class", "team");

		var updateTeam = enterTeam.merge(team)
		team.exit().remove();

		// MAIN STUFF
		// Now add data to this column for each correct answer, create a new path,
		// transform it to the right time and draw a symbol corresponding to the team that made the answer
		updateTeam.selectAll("path")
			.data(function(d, i) { return d.progress })
			.enter()
			.append("path")
			.attr("transform", function(d, i) { return "translate(" + x(d.puzzle) + "," + y(new Date(d.time)) + ")"; })
			.attr("class", function(d, i) { return "team-" + escapeHtml(parentData(this).team); })
			.attr("fill", function(d) { return colours(parentData(this).team); })
			.attr("fill-opacity", function(d) { return symbols(parentData(this).team).fillOpacity; })
			.attr("stroke", function(d) { return colours(parentData(this).team); })
			.attr("stroke-width", function(d) { return symbols(parentData(this).team).strokeWidth; })
			.attr("d", function(d) { return symbols(parentData(this).team).path; } );

		if (lines) {
			chart.selectAll(".progress-line").remove();
			var progressLine = d3.line()
				.x(function (d) { return x(d.puzzle); })
				.y(function (d) { return y(new Date(d.time)); });

			data.puzzleProgress.forEach(function (d, i) {
				chart.append("path")
					.attr("class", "line progress-line team-" + escapeHtml(d.team))
					.attr("stroke", colours(d.team))
					.attr("d", progressLine(d.progress));
			});
		}

		// Draw the axes with large negative tick sizes to get grid lines
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

		drawLegend(data, colours, symbols);
	};
}

function drawLegend(data, colours, symbols) {
	// Compute margin from the main graph margin
	var legendMargin = {top: margin.top + 20, right: 0, bottom: 0, left: 6}
	var entryHeight = 16;
	// Add data about the teams
	var legend = d3.select("#legend").selectAll("g").data(data.puzzleProgress);
	legend.selectAll("*").remove();
	var enterLegend = legend.enter()
		.append("g")
	// Transform each group to a position just right of the main graph, and down some for each line
	var updateLegend = enterLegend.merge(legend)
		.attr("transform", function(d, i) {
			return "translate(" +
				(width + margin.left + legendMargin.left) + "," +
				(legendMargin.top + i * entryHeight) +
			")";
		})
	updateLegend.on("click", function(d, i) {
		var active = d.active? false : true;
		var opacity = active? 0 : 1;
		d3.selectAll('[class~="team-' + escapeHtml(d.team) + '"]')
			.transition().duration(200)
			.style("opacity", opacity);
		d.active = active;
	});
	// Add the symbol corresponding to that team
	updateLegend.append("path")
		.attr("transform", "translate(5, -4)")
		.attr("class", function(d, i) { return "team-" + escapeHtml(d.team); })
		.attr("fill", function(d) { return colours(d.team); })
		.attr("fill-opacity", function(d) { return symbols(d.team).fillOpacity; })
		.attr("stroke", function(d) { return colours(d.team); })
		.attr("stroke-width", function(d) { return symbols(d.team).strokeWidth; })
		.attr("d", function(d) { return symbols(d.team).path; });
	// Add the team's name
	updateLegend.append("text")
		.attr("x", 16)
		.text(function(d) { return d.team; });
	// Delete vanished teams
	legend.exit().remove();
}

function parentData(n) {
	return n.parentNode.__data__;
}

var chart,
	margin,
	width,
	height,
	xAxisElt,
	yAxisElt;

function clearChart() {
	var svg = d3.select('#episode-stats');
	margin = {top: 100, right: 200, bottom: 100, left: 50};
	width = +svg.attr("width") - margin.left - margin.right;
	height = +svg.attr("height") - margin.top - margin.bottom;

	if (chart) {
		chart.selectAll("*").remove();
	} else {
		svg.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	}
	if (svg.select('#legend').empty()) {
		svg.append("g").attr("id", "legend");
	} else {
		clearLegend();
	}

	chart = svg.select("g")
	chart.append("rect")
		.attr("width", width)
		.attr("height", height)
		.attr("class", "chart-background");

	xAxisElt = chart.append("g")
		.attr("class", "axis axis-x");

	yAxisElt = chart.append("g")
		.attr("class", "axis axis-y");
}

function clearLegend() {
	d3.selectAll("#legend *").remove();
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

