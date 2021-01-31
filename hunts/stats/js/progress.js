import Chart from 'chart.js'
import 'chartjs-adapter-luxon'
import distinctColors from 'distinct-colors'

let dateAxis = 'x'
let puzzleAxis = 'y'
let puz0name = '(started)'

function generateTeamColours(episode_progress) {
  let team_set = new Set()
  for (let episode in episode_progress) {
    for (let team of episode_progress[episode].teams) {
      team_set.add(team.team_id)
    }
  }
  let colours = distinctColors({count: team_set.size, chromaMin: 10, chromaMax: 90, lightMin: 20, lightMax: 80})
  let teams = Array.from(team_set)
  let team_colours = new Map()
  for (let i = 0; i < teams.length; ++i) {
    team_colours.set(teams[i], colours[i])
  }
  console.log(team_colours)
  return team_colours
}

function timesToChartForm(data, puzfn) {
  let times = data.puzzle_times
  let result = []
  for (let i = 0; i < times.length; ++i)
    result.push({[puzzleAxis]: puzfn(i), [dateAxis]: times[i].date})
  return result
}

function getChartDataSets(teamdata, team_colours) {
  let puzfn = function (n) {
    return n
  }
  if (Object.prototype.hasOwnProperty.call(teamdata, 'puzzle_names')) {
    puzfn = function(n) {
      return (n > 0) ? teamdata.puzzle_names[n-1] : puz0name
    }
  }

  let teamchartdatasets = []
  console.log(teamdata)
  for (let team of teamdata.teams) {
    let colour = team_colours.get(team.team_id)
    console.log(`${team.team_id} ${colour}`)
    teamchartdatasets.push({
      data: timesToChartForm(team, puzfn),
      borderColor: colour,
      borderWidth: 2,
      hoverBorderColor: colour,
      hoverBorderWidth: 4,
      fill: false,
      label: team.team_name,
      lineTension: 0,
      pointRadius: 2,
      pointHoverRadius: 2,
    })
  }
  return teamchartdatasets
}

function setAllHidden(chart, hidden) {
  chart.data.datasets.forEach(dataset => {
    Object.keys(dataset._meta).forEach(key => {
      dataset._meta[key].hidden = hidden
    })
  })
  chart.update()
}

let team_colours = generateTeamColours(window.episode_progress)

for (let canvas of document.getElementsByClassName('progress-graph')) {
  let puzaxis = {}

  let episode_data = window.episode_progress[canvas.dataset.episode]

  if (Object.prototype.hasOwnProperty.call(episode_data, 'puzzle_names')) {
    puzaxis.type = 'category'
    puzaxis.labels = [puz0name].concat(episode_data.puzzle_names)
    if (puzzleAxis == 'y')
      puzaxis.labels = puzaxis.labels.reverse() // Y axis categories start from the top... :|
  } else {
    puzaxis.type = 'linear'
    puzaxis.ticks = {
      stepSize: 1,
      suggestedMin: 0,
      precision: 0,
      beginAtZero: true,
    }
  }

  let teamchartdatasets = getChartDataSets(episode_data, team_colours)

  let height = 0.2 * window.innerHeight
  canvas.height = height
  canvas.style.height = height
  let ctx = canvas.getContext('2d')
  let chart = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: teamchartdatasets,
    },
    options: {
      hover: {
        mode: 'dataset',
      },
      layout: {
        padding: {
          left: 50,
          right: 50,
          top: 50,
          bottom: 50,
        },
      },
      scales: {
        [dateAxis + 'Axes']: [{
          type: 'time',
          time: {
            unit: 'hour',
            displayFormats: {hour: 'HH:mm'},
          },
        }],
        [puzzleAxis + 'Axes']: [puzaxis],
      },
    },
  })

  let showAllButton = document.getElementById(`show-all-${canvas.dataset.episode}`)
  showAllButton.addEventListener('click', function() {
    setAllHidden(chart, false)
  })

  let hideAllButton = document.getElementById(`hide-all-${canvas.dataset.episode}`)
  hideAllButton.addEventListener('click', function() {
    setAllHidden(chart, true)
  })
}
