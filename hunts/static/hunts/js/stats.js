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
		"team-total-stuckness": drawTeamStuckness
	}[graphType];
	$.get('stats_content', {}, drawFunction);
	setTimeout(getStats, 5000);
}

function drawCompletion(data) {
	// Create scales for a bar chart
	var x = d3.scaleBand()
		.rangeRound([0, width]).padding(0.1)
		.domain(data.puzzles);
	var y = d3.scaleLinear()
		.domain([0, data.numTeams])
		.range([height, 0]);

	// Join data to a group with class bar
	var bar = chart.selectAll("g.bar")
		.data(data.puzzleCompletion);

	// For new bars, create the group, rectangle and some text
	var enterBar = bar.enter()
		.append("g")
		.attr("class", "bar");
	enterBar.append("rect");
	enterBar.append("text");

	// Update the rectangle...
	var updateBar = enterBar.merge(bar);
	updateBar.attr("transform", function(d, i) { return "translate(" + x(d.puzzle) + ",0)"; })
		.select("rect")
		.attr("y", function(d) { return y(d.completion); })
		.attr("height", function(d) { return height - y(d.completion); })
		.attr("width", x.bandwidth());

	// ...and the text
	var percentFormatter = function (d) { return d3.format(".0%")(d / data.numTeams); };

	updateBar.select("text")
		.attr("y", function(d) { return y(d.completion) + 3; })
		.attr("x", x.bandwidth() / 2)
		.attr("dy", ".75em")
		.text(function (d) { return d.completion; });

	// Clear old bars
	bar.exit().remove();

	// Draw axes and horizontal marker lines
	xAxisElt.call(d3.axisBottom(x))
		.attr("transform", "translate(0," + height + ")")
		.selectAll("text")
		.attr("transform", "rotate(-20)");

	// On the y axis, don't draw the actual numbers but instead a percentage.
	var yForAxis = d3.scaleLinear()
		.domain([0, 1])
		.range([height, 0]);
	var yAxis = d3.axisLeft(yForAxis)
		.tickSize(-width)
		.tickPadding(10)
		.tickFormat(d3.format(".0%"));

	yAxisElt.call(yAxis);
}

function drawTimeCompleted(lines) {
	return function(data) {
		// Create the X and Y scales
		var x = d3.scalePoint()
			.range([0, width])
			.padding(0.5)
			.domain(data.puzzles);
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
			.attr("class", function(d, i) { return "hide-team team-" + escapeHtml(parentData(this).team); })
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
					.attr("class", "line progress-line hide-team team-" + escapeHtml(d.team))
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

function timeFormatter(seconds) {
	console.log(seconds); console.log(Math.floor(seconds / 3600) + ":" + Math.floor(seconds / 60) % 60);
	return Math.floor(seconds / 3600) + ":" + Math.floor(seconds / 60) % 60;
}

function drawTeamStuckness(data) {
	var stuckness = data.teamTotalStuckness.sort(function (a, b) { return b.stuckness - a.stuckness; });
	var y = d3.scaleBand()
		.domain(stuckness.map(function(d) { return d.team; }))
		.range([0, height])
		.padding(0.1);
	var x = d3.scaleTime()
		.domain([new Date(1970, 0, 0), new Date(1970, 0, 0, 0, 0, d3.max(stuckness.map(function(d) { return d.stuckness; })))])
		.range([0, width]);

	var bar = chart.selectAll("g.bar")
		.data(data.teamTotalStuckness);

	var enterBar = bar.enter()
		.append("g")
		.attr("class", "bar");
	enterBar.append("rect");

	var updateBar = enterBar.merge(bar);
	updateBar.attr("transform", function(d, i) { return "translate(0," + y(d.team) + ")"; })
		.select("rect")
		.attr("width", function(d) { return x(new Date(1970, 0, 0, 0, 0, d.stuckness)); })
		.attr("height", y.bandwidth());

	var xAxis = d3.axisTop(x)
		.tickSize(-height)
		.tickPadding(10)
		.tickFormat(timeFormatter);

	xAxisElt.call(xAxis)
		.selectAll("text")
		.style("text-anchor", "middle");

	yAxisElt.call(d3.axisLeft(y))
		.selectAll("text")
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
	// Hide/show graph stuff
	var hiddenOpacity = 0.1;
	updateLegend.on("click", function(d, i) {
		if (d3.event.ctrlKey) {
			var currentlyinvis = d3.select('[class~="invis"][class~="team-' + escapeHtml(d.team) + '"]').empty();
			d3.selectAll('[class~="team-' + escapeHtml(d.team) + '"]')
				.classed("invis", currentlyinvis)
				.transition(200)
				.style("opacity", currentlyinvis ? hiddenOpacity : 1);
		} else {
			// If all others are invis and this isn't, unhide all. Otherwise hide all but this one.
			var unhideAll = d3.selectAll('.hide-team:not([class~="invis"]):not([class~="team-' + escapeHtml(d.team) + '"])').empty();
			if (unhideAll) {
				d3.selectAll(".hide-team")
					.classed("invis", false)
					.transition(200)
					.style("opacity", 1);
			} else {
				// The second transition overrides the first, so only the second selection has to be complicated
				d3.selectAll(".hide-team")
					.classed("invis", true)
					.transition(200)
					.style("opacity", hiddenOpacity);
				d3.selectAll('[class~="team-' + escapeHtml(d.team) + '"]')
					.classed("invis", false)
					.transition(200)
					.style("opacity", 1);
			}
		}
	});
	// Add the symbol corresponding to that team
	updateLegend.append("path")
		.attr("transform", "translate(5, -4)")
		.attr("class", function(d, i) { return "hide-team team-" + escapeHtml(d.team); })
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
	margin = {top: 100, right: 200, bottom: 100, left: 100};
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

